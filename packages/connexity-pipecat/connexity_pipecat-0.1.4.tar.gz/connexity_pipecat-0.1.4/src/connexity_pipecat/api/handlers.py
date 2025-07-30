"""
Voice-AI FastAPI handlers and helpers.

This module exposes several FastAPI-compatible coroutine handlers used by the
Connexity voice-AI stack:

*  Initiating inbound / outbound Twilio calls.
*  Handling Twilio web-hook callbacks (TwiML & WebSocket media).
*  Plain HTTP inference endpoints for text-only chat.
*  Utility callbacks for updating call status in Redis‐like cache.

The codebase is large, so the most valuable improvements concentrate on:

*   Import ordering & deduplication (PEP 8 § Imports).
*   Type annotations, doc-strings and inline comments.
*   Removal of unused / duplicate imports.
"""

from __future__ import annotations

# ──────────────────────────────── stdlib ──────────────────────────────────────
import json
import os
import sys
import time
from typing import Any, Dict, Optional

from connexity.metrics.pipecat import ConnexityTwilioObserver
from deepgram import LiveOptions
# ────────────────────────────── 3rd-party ─────────────────────────────────────
from fastapi import Request, WebSocket
from loguru import logger
from pipecat.audio.mixers.soundfile_mixer import SoundfileMixer
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.transports.network.fastapi_websocket import FastAPIWebsocketTransport, FastAPIWebsocketParams
from starlette.responses import HTMLResponse, JSONResponse
from starlette.websockets import WebSocketDisconnect

from pipecat.frames.frames import (
    EndFrame, TTSSpeakFrame, LLMMessagesFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import (
    OpenAILLMContext,
    OpenAILLMContextFrame,
)
from pipecat.services.openai.llm import OpenAILLMService

from connexity_pipecat.core.voice_calls.helpers.EndCallProcessor import EndCallProcessor
from connexity_pipecat.core.voice_calls.helpers.get_tts_service import get_tts_service
from connexity_pipecat.core.config import get_config
from connexity_pipecat.core.voice_calls.helpers.initiate_vad_params import initiate_vad_params
from connexity_pipecat.core.prompts import get_prompt
from connexity_pipecat.core.tools import get_function_handlers, get_functions_meta
from connexity_pipecat.data.cache import (
    delete_call_status,
    get_call_status,
    set_call_status,
    update_response_id,
)
from connexity_pipecat.data.consts import (
    OPENAI_API_KEY,
    SERVER_ADDRESS,
    PromptType, BACKGROUND_AUDIO_DICT, CONNEXITY_API_KEY, TWILIO_ACCOUNT_ID, TWILIO_AUTH_TOKEN, DEEPGRAM_API_KEY,
)
from connexity_pipecat.data.schemas import (
    RelevantResponseRequest,
    RequestBody,
    RequestBodyForVoiceAI,
    create_agent_inputs,
)
from connexity_pipecat.data.validators import (
    is_valid_end_call_time,
    is_valid_iso_language,
    is_valid_voice_settings,
)
from connexity_pipecat.core.voice_calls.templates import (
    twiml_template_inbound,
    twiml_template_outbound,
    twiml_template_outbound_with_play,
)
from connexity_pipecat.core.voice_calls.twilio_service import TwilioClient
from connexity_pipecat.helpers.get_model import get_llm_service

# ────────────────────────────── logging ───────────────────────────────────────
# Remove any default handlers (Loguru raises if id 0 does not exist)
logger.remove()
logger.add(sys.stderr, level="DEBUG")

# ─────────────────────────── module globals ───────────────────────────────────
twilio_client = TwilioClient()
#: In-memory scratch-pad storing per-call data (non-persistent, process-local).
data_storage: Dict[str, Dict[str, Any]] = {}

# =============================================================================
#                       Utility & callback endpoints
# =============================================================================


async def receive_voice_updates(request: RelevantResponseRequest) -> None:
    """
    Update :pydata:`connexity_pipecat.data.cache` with the latest *response_id*
    and *turn-taking* flag for a conversation.

    Args:
        request: Parsed FastAPI request body.
    """
    update_response_id(
        call_id=request.conversation_id,
        response_id=request.platform_metadata.response_id,
        turn_taking=request.platform_metadata.turn_taking,
    )


async def status_callback_get(sid: str) -> Dict[str, Optional[str]]:
    """
    Lightweight health endpoint for Twilio ``StatusCallback``.

    Args:
        sid: Twilio Call-SID.

    Returns:
        Mapping containing the current status (e.g. *in-progress* /
        *completed* / *initiated*).
    """
    return {"status": get_call_status(sid)}


async def status_callback_post(request: Request) -> None:
    """
    Twilio POST ``StatusCallback`` handler – reflects Twilio’s call-life-cycle
    back into the in-process cache.

    Twilio sends x-www-form-urlencoded payloads.

    * ``busy``      → mark as *completed* (so the caller can stop polling).
    * ``completed`` → purge status + local scratch data.

    Args:
        request: FastAPI Request containing form-data.
    """
    post_data = await request.form()
    call_sid = post_data.get("CallSid")

    if post_data.get("CallStatus") == "busy":
        set_call_status(call_sid, "completed")

    if post_data.get("CallStatus") == "completed":
        delete_call_status(call_sid)
        data_storage.pop(call_sid, None)

# =============================================================================
#                          Outbound call handlers
# =============================================================================


async def initiate_phone_call(request_body: RequestBodyForVoiceAI) -> Any:
    """
    Trigger an **outbound** Twilio voice call and stash the request details
    for use by subsequent WebSocket media streams.

    Args:
        request_body: JSON payload received from the orchestrating
            application / front-end.

    Returns:
        • ``JSONResponse`` with *403 / 500* on failure.

        • ``dict``     with *sid*, *from*, *to* on success (HTTP 200).
    """
    # ─────────────── validation ───────────────
    language = request_body.language
    if not is_valid_iso_language(language):
        return JSONResponse(
            status_code=403,
            content={"message": f"Invalid language {language!r}"},
        )

    if not is_valid_voice_settings(
        request_body.agent_settings.voice_id, request_body.agent_settings.voice_url
    ):
        return JSONResponse(
            status_code=403,
            content={"message": "Invalid voice settings – both empty"},
        )

    if not is_valid_end_call_time(request_body.end_call_seconds):
        return JSONResponse(
            status_code=403,
            content={"message": "end_call_seconds must be ≥ 60"},
        )

    # ─────────────── Twilio call ───────────────
    try:
        sid = twilio_client.create_phone_call(
            request_body.from_number,
            request_body.to_number,
        )
        set_call_status(sid, "initiated")
    except Exception as exc:  # pragma: no-cover – Twilio raises dozens of types
        return JSONResponse(
            status_code=500,
            content={"message": f"Internal Server Error: {exc}"},
        )

    # cache everything we’ll need when WebSocket media starts streaming
    data_storage[sid] = request_body.model_dump()
    data_storage[sid].update({"sid": sid, "call_type": "outbound"})

    return {"sid": sid, "from": request_body.from_number, "to": request_body.to_number}


async def outbound_webhook(request: Request) -> HTMLResponse:
    """
    Twilio *TwiML* webhook for **outbound** calls – returns an XML document
    instructing Twilio to connect to our WebSocket media stream.

    Args:
        request: FastAPI Request (x-www-form-urlencoded).

    Returns:
        TwiML XML wrapped in :class:`starlette.responses.HTMLResponse`.
    """
    data = await request.form()
    sid = data.get("CallSid")
    call_info = data_storage.get(sid, {})
    audio_url = call_info.get("play_audio_url")

    xml_template = (
        twiml_template_outbound_with_play
        if audio_url
        else twiml_template_outbound
    )
    formatted_xml = xml_template.format(audio_url=audio_url, wss_url=SERVER_ADDRESS)
    return HTMLResponse(content=formatted_xml, media_type="application/xml")


async def outbound_websocket_endpoint(websocket: WebSocket) -> None:
    """
    Handle Twilio media stream for an **outbound** call.

    The first two messages sent by Twilio are JSON control frames
    (``start`` / stream info).  After that we switch to 8 kHz 16-bit
    mono   µ-law *audio/PCMU*.
    """
    call_sid = None
    try:
        await websocket.accept()
        start_data = websocket.iter_text()
        await start_data.__anext__()  # Skip first message
        call = json.loads(await start_data.__anext__())
        print(call, flush=True)
        call_sid = call["start"]["callSid"]
        stream_sid = call["start"]["streamSid"]
        call_info = data_storage.get(call_sid, {})
        print("WebSocket connection accepted")

        start_time = time.time()
        set_call_status(call_info.get("sid"), "in-progress")

        selected_sound = call_info.get("background_noise")

        default_sound = (
            selected_sound if selected_sound in BACKGROUND_AUDIO_DICT.keys() else "test"
        )

        soundfile_mixer = SoundfileMixer(
            sound_files=BACKGROUND_AUDIO_DICT,
            default_sound=default_sound,
            volume=0.5,
        )

        vad_params = initiate_vad_params()

        transport = FastAPIWebsocketTransport(
            websocket=websocket,
            params=FastAPIWebsocketParams(
                audio_out_enabled=True,
                audio_out_mixer=(
                    soundfile_mixer if call_info.get("background_noise") else None
                ),
                add_wav_header=False,
                audio_in_enabled=True,
                vad_analyzer=SileroVADAnalyzer(params=vad_params),
                audio_in_passthrough=True,
                serializer=TwilioFrameSerializer(stream_sid, call_sid=call_info.get("sid"),
                                                 account_sid=TWILIO_ACCOUNT_ID,
                                                 auth_token=TWILIO_AUTH_TOKEN),
            ),
        )

        # crafting a prompt
        agent_inputs = create_agent_inputs()

        if agent_inputs.translate_prompt:
            prompt_str = get_prompt(
                PromptType.AGENT,
                agent_inputs.language_code,
            )
        else:
            prompt_str = get_prompt(
                PromptType.AGENT
            )

        prompt = prompt_str.format(**agent_inputs.model_dump())

        message_history = [{"role": "system", "content": prompt}]

        # Use appropriate Deepgram model for language (TODO: update when multi-language supported)
        if agent_inputs.language_code != "en":
            live_options = LiveOptions(
                model="nova-2-general",
                language=agent_inputs.language_code,
            )
        else:
            live_options = None

        stt = DeepgramSTTService(
            api_key=DEEPGRAM_API_KEY, live_options=live_options
        )

        tts = get_tts_service(call_info)

        llm_service = OpenAILLMService(
            model=get_config()["llm"]["main"]["model"],
            params=OpenAILLMService.InputParams(
                top_p=0.05,
                temperature=1,
                max_tokens=1000
            ),
            api_key=OPENAI_API_KEY
        )

        tools_meta = get_functions_meta(get_config()["tools"])
        function_handlers = get_function_handlers(get_config()["tools"])
        for name, handler in function_handlers.items():
            llm_service.register_function(name, handler)

        context = OpenAILLMContext(message_history, tools=tools_meta)
        context_aggregator = llm_service.create_context_aggregator(context)

        # EndCallProcessor with static seconds (should be made dynamic if needed)
        end_call = EndCallProcessor(
            start_time=start_time, sid=call_info.get("sid"), seconds=300
        )

        pipeline = Pipeline(
            [
                transport.input(),
                stt,
                context_aggregator.user(),
                llm_service,
                tts,
                transport.output(),
                context_aggregator.assistant(),
                end_call,
            ]
        )

        observers = []
        if get_config()["use_connexity_observer"]:
            connexity_metrics_observer = ConnexityTwilioObserver()
            await connexity_metrics_observer.initialize(sid=call_sid,
                                                        api_key=CONNEXITY_API_KEY,
                                                        agent_id=get_config()["agent_id"],
                                                        agent_phone_number=call_info.get("to"),
                                                        user_phone_number=call_info.get("from"),
                                                        phone_call_provider='twilio',
                                                        twilio_account_sid=TWILIO_ACCOUNT_ID,
                                                        twilio_auth_token=TWILIO_AUTH_TOKEN,
                                                        voice_provider='11labs',
                                                        llm_model=get_config()["llm"]["utils"]["model"],
                                                        llm_provider=get_config()["llm"]["utils"]["vendor"],
                                                        call_type=call_info.get('call_type'),
                                                        transcriber='deepgram')

            observers.append(connexity_metrics_observer)

        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                audio_in_sample_rate=get_config()["pipeline_settings"].get("audio_in_sample_rate", 8000),
                allow_interruptions=get_config()["pipeline_settings"].get("allow_interruptions", True),
                enable_metrics=get_config()["pipeline_settings"].get("enable_metrics", True),
                report_only_initial_ttfb=get_config()["pipeline_settings"].get("report_only_initial_ttfb", True),
            ),
            observers=observers
        )

        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            """
            Sends a greeting or initial message when the client connects.
            """
            if get_config()["start_message"]:
                await task.queue_frames([TTSSpeakFrame(get_config()["start_message"])])
            else:
                await task.queue_frames([LLMMessagesFrame(message_history)])

        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            """
            Cancels the task and marks call as completed on disconnect.
            """
            await task.cancel()
            set_call_status(call_info.get("sid"), "completed")

        runner = PipelineRunner(handle_sigint=False, force_gc=True)

        await runner.run(task)

    except WebSocketDisconnect:
        print(f"LLM WebSocket disconnected for {call_sid}")
    except Exception as e:
        print(f"Error in LLM WebSocket: {e} for {call_sid}")
        await websocket.close(1011, "Server error")

# =============================================================================
#                          Inbound call handlers
# =============================================================================


async def inbound_webhook(request: Request) -> HTMLResponse:
    """
    Twilio *TwiML* webhook for **inbound** PSTN calls.

    Args:
        request: FastAPI Request (JSON or x-www-form-urlencoded).

    Returns:
        XML response instructing Twilio to connect to our WebSocket.
    """
    if request.headers.get("content-type", "").startswith("application/json"):
        form: Dict[str, Any] = await request.json()
    else:
        form = dict(await request.form())

    sid = form.get("CallSid")
    data_storage[sid] = {
        "to": form.get("To"),
        "from": form.get("From"),
        "sid": sid,
        "inputs": form.get("inputs", {}),
        "agent_settings": form.get("agent_settings", {}),
        "call_type": "inbound",
        "language": "en",
        "end_call_seconds": form.get("end_call_seconds") or True,
        "prompt": "",
    }

    formatted_xml = twiml_template_inbound.format(
        status_callback=SERVER_ADDRESS,
        transcription_url=SERVER_ADDRESS,
        wss_url=SERVER_ADDRESS,
    )
    return HTMLResponse(content=formatted_xml, media_type="application/xml")


async def inbound_websocket_endpoint(websocket: WebSocket) -> None:
    """
    Handle inbound websocket endpoint for streaming voice data and run agent.

    Args:
        websocket (WebSocket): The websocket connection.

    Returns:
        None
    """
    call_sid = None
    try:
        await websocket.accept()
        start_data = websocket.iter_text()
        await start_data.__anext__()  # Skip first message
        call = json.loads(await start_data.__anext__())
        print(call, flush=True)
        call_sid = call["start"]["callSid"]
        stream_sid = call["start"]["streamSid"]
        call_info = data_storage.get(call_sid, {})
        print("WebSocket connection accepted")

        start_time = time.time()
        set_call_status(call_info.get("sid"), "in-progress")

        selected_sound = call_info.get("background_noise")

        default_sound = (
            selected_sound if selected_sound in BACKGROUND_AUDIO_DICT.keys() else "test"
        )

        soundfile_mixer = SoundfileMixer(
            sound_files=BACKGROUND_AUDIO_DICT,
            default_sound=default_sound,
            volume=0.5,
        )

        vad_params = initiate_vad_params()

        transport = FastAPIWebsocketTransport(
            websocket=websocket,
            params=FastAPIWebsocketParams(
                audio_out_enabled=True,
                audio_out_mixer=(
                    soundfile_mixer if call_info.get("background_noise") else None
                ),
                add_wav_header=False,
                audio_in_enabled=True,
                vad_analyzer=SileroVADAnalyzer(params=vad_params),
                audio_in_passthrough=True,
                serializer=TwilioFrameSerializer(stream_sid, call_sid=call_info.get("sid"), account_sid=TWILIO_ACCOUNT_ID,
                                             auth_token=TWILIO_AUTH_TOKEN),
            ),
        )

        # crafting a prompt
        agent_inputs = create_agent_inputs()

        if agent_inputs.translate_prompt:
            prompt_str = get_prompt(
                PromptType.AGENT,
                agent_inputs.language_code,
            )
        else:
            prompt_str = get_prompt(
                PromptType.AGENT
            )

        prompt = prompt_str.format(**agent_inputs.model_dump())

        message_history = [{"role": "system", "content": prompt}]

        # Use appropriate Deepgram model for language (TODO: update when multi-language supported)
        if agent_inputs.language_code != "en":
            live_options = LiveOptions(
                model="nova-2-general",
                language=agent_inputs.language_code,
            )
        else:
            live_options = None

        stt = DeepgramSTTService(
            api_key=DEEPGRAM_API_KEY, live_options=live_options
        )

        tts = get_tts_service(call_info)

        llm_service = get_llm_service(
            vendor=get_config()["llm"]["main"]["vendor"],
            model_name=get_config()["llm"]["main"]["model"]
        )

        tools_meta = get_functions_meta(get_config()["tools"])
        function_handlers = get_function_handlers(get_config()["tools"])
        for name, handler in function_handlers.items():
            llm_service.register_function(name, handler)

        context = OpenAILLMContext(message_history, tools=tools_meta)
        context_aggregator = llm_service.create_context_aggregator(context)

        # EndCallProcessor with static seconds (should be made dynamic if needed)
        end_call = EndCallProcessor(
            start_time=start_time, sid=call_info.get("sid"), seconds=300
        )

        pipeline = Pipeline(
            [
                transport.input(),
                stt,
                context_aggregator.user(),
                llm_service,
                tts,
                transport.output(),
                context_aggregator.assistant(),
                end_call,
            ]
        )

        observers = []
        if get_config()["use_connexity_observer"]:
            connexity_metrics_observer = ConnexityTwilioObserver()
            await connexity_metrics_observer.initialize(sid=call_sid,
                                                        api_key=CONNEXITY_API_KEY,
                                                        agent_id=get_config()["agent_id"],
                                                        agent_phone_number=call_info.get("to"),
                                                        user_phone_number=call_info.get("from"),
                                                        phone_call_provider='twilio',
                                                        twilio_account_sid=TWILIO_ACCOUNT_ID,
                                                        twilio_auth_token=TWILIO_AUTH_TOKEN,
                                                        voice_provider='11labs',
                                                        llm_model=get_config()["llm"]["utils"]["model"],
                                                        llm_provider=get_config()["llm"]["utils"]["vendor"],
                                                        call_type=call_info.get('call_type'),
                                                        transcriber='deepgram')

            observers.append(connexity_metrics_observer)

        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                audio_in_sample_rate=get_config()["pipeline_settings"].get("audio_in_sample_rate", 8000),
                allow_interruptions=get_config()["pipeline_settings"].get("allow_interruptions", True),
                enable_metrics=get_config()["pipeline_settings"].get("enable_metrics", True),
                report_only_initial_ttfb=get_config()["pipeline_settings"].get("report_only_initial_ttfb", True),
            ),
            observers=observers
        )

        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport, client):
            """
            Sends a greeting or initial message when the client connects.
            """
            if get_config()["start_message"]:
                await task.queue_frames([TTSSpeakFrame(get_config()["start_message"])])
            else:
                await task.queue_frames([LLMMessagesFrame(message_history)])

        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport, client):
            """
            Cancels the task and marks call as completed on disconnect.
            """
            await task.cancel()
            set_call_status(call_info.get("sid"), "completed")

        runner = PipelineRunner(handle_sigint=False, force_gc=True)

        await runner.run(task)

    except WebSocketDisconnect:
        print(f"LLM WebSocket disconnected for {call_sid}")
    except Exception as e:
        print(f"Error in LLM WebSocket: {e} for {call_sid}")
        await websocket.close(1011, "Server error")

async def platform_inference(request_body: RequestBody) -> JSONResponse:
    """
    One-shot plain-text inference (no streaming) for embedding
    Connexity Agent into messaging platforms (Slack, Discord …).

    * Builds ‘system’ prompt using :data:`PromptType.AGENT`.
    * Registers **function-call** handlers.
    * Returns assistant message and cached usage metrics.
    """
    # extend chat history with the new user turn
    conversation_history = list(request_body.history or [])
    conversation_history.append({"role": "user", "content": request_body.query})

    llm_service = get_llm_service(
        vendor=get_config()["llm"]["main"]["vendor"],
        model_name=get_config()["llm"]["main"]["model"]
    )

    agent_inputs = create_agent_inputs()
    system_prompt = get_prompt(PromptType.AGENT, agent_inputs.language_code).format(
        **agent_inputs.model_dump()
    )

    message_history = [{"role": "system", "content": system_prompt}, *conversation_history]

    tools_meta = get_functions_meta(get_config()["tools"])
    function_handlers = get_function_handlers(get_config()["tools"])
    for name, handler in function_handlers.items():
        llm_service.register_function(name, handler)

    context = OpenAILLMContext(message_history, tools=tools_meta)
    assistant_aggr = llm_service.create_context_aggregator(context).assistant()

    pipeline = Pipeline([llm_service, assistant_aggr])
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=get_config()["pipeline_settings"].get("allow_interruptions", True),
            enable_metrics=get_config()["pipeline_settings"].get("enable_metrics", True),
            report_only_initial_ttfb=get_config()["pipeline_settings"].get("report_only_initial_ttfb", True),
        ),
        check_dangling_tasks=False,  # suppress “coroutine never awaited”
    )

    await task.queue_frames([OpenAILLMContextFrame(context), EndFrame()])
    await PipelineRunner(handle_sigint=False, force_gc=True).run(task)

    return JSONResponse(
        content={
            "model": get_config()["llm"]["main"]["model"],
            "message": context.messages[-1]["content"].replace('  ', 'A0TEMP').replace(' ', '').replace('A0TEMP', ' '),
            "steps": [],
            "error": None,
            "metadata": {},
            "body": {},
        }
    )