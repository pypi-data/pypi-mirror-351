import inspect
from datetime import datetime
from functools import lru_cache
from inspect import isfunction, signature
from typing import List, Optional, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, create_model

from connexity_pipecat.core.generators.management import get_generators
from connexity_pipecat.data.consts import StateEnum
from connexity_pipecat.core.config import get_config

class ConversationFlow(BaseModel):
    active_agent: StateEnum = StateEnum.MAIN_AGENT_FLOW
    arguments: dict = Field(default_factory=dict)


class PostCallAnalysisSchema(BaseModel):
    callback_time: Optional[datetime]  # Null if no appointment was set
    call_status: str  # One of the predefined status strings
    call_summary: str  # A brief 1-2 sentence natural-language summary

class AgentSettings(BaseModel):
    voice_provider: str
    voice_url: Optional[str]
    voice_id: Optional[str]
    start_message: Optional[str] = None
    speak_first: Optional[bool] = False


class RequestBodyForVoiceAI(BaseModel):
    prompt: str
    inputs: Optional[dict]
    from_number: Optional[str]
    to_number: Optional[str]
    agent_settings: Optional[AgentSettings]
    end_call_seconds: Optional[int] = None
    background_noise: Optional[bool] = False
    language: Optional[str] = 'en'
    play_audio_url: Optional[str] = None


class Metadata(BaseModel):
    history: List[Dict[str, Any]] = Field(default_factory=list)

    generated_messages_per_turn: list[dict] = Field(default_factory=list)
    active_flow: ConversationFlow = Field(default_factory=ConversationFlow)
    finalize_action: Optional[Literal["__end__", "__transfer__"]] = None
    finalize_action_kwargs: Optional[dict] = Field(default_factory=dict)


class PlatformMetadata(BaseModel):
    platform: Optional[Literal["retell", "elevenlabs"]] = None
    response_id: Optional[int] = None
    turn_taking: Optional[Literal["agent_turn", "user_turn"]] = None
    tools: Optional[List] = None


class RequestBody(BaseModel):
    conversation_id: str
    query: Optional[str] = None
    agent_inputs: BaseModel = Field(default_factory=lambda: create_agent_inputs())
    metadata: Optional[Metadata] = None
    stream: bool = False
    history: Optional[List[Dict[str, Any]]] = None
    platform_metadata: Optional[PlatformMetadata] = None


class RelevantResponseRequest(BaseModel):
    conversation_id: str
    platform_metadata: PlatformMetadata


class CallMonitor(BaseModel):
    listenUrl: str
    controlUrl: str


class Transport(BaseModel):
    assistantVideoEnabled: bool


class AssistantOverrides(BaseModel):
    clientMessages: List[str]


class Call(BaseModel):
    id: str
    orgId: str
    createdAt: str
    updatedAt: str
    type: str
    monitor: CallMonitor
    transport: Transport
    webCallUrl: str
    status: str
    assistantId: str
    assistantOverrides: AssistantOverrides


class Message(BaseModel):
    role: str
    content: str


class VapiRequestBody(BaseModel):
    model: str
    messages: List[Message]
    temperature: float
    stream: bool
    max_tokens: int
    call: Call
    metadata: Dict[str, Any]
    credentials: List[Any]


class ElevenlabsRequestBody(BaseModel):
    messages: List
    model: str
    max_tokens: int
    stream: bool
    temperature: float
    tools: Optional[List[Dict]]
    elevenlabs_extra_body: Optional[dict] = None


class ContentResponse(BaseModel):
    response_type: Literal["response"] = "response"
    content: str


class ToolCallInvocationResponse(BaseModel):
    response_type: Literal["tool_call_invocation"] = "tool_call_invocation"
    tool_call_id: str
    name: str
    arguments: str


class ToolCallResultResponse(BaseModel):
    response_type: Literal["tool_call_result"] = "tool_call_result"
    tool_call_id: str
    content: str


InferenceEvent = Union[
    ContentResponse | ToolCallInvocationResponse | ToolCallResultResponse
]


_TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "dict": dict,
    "list": list,
}

@lru_cache
def _build_agent_inputs_model() -> type[BaseModel]:
    cfg_defaults = get_config()["agent_inputs"]

    fields: dict[str, tuple[type, Any]] = {}
    generators = get_generators()

    for key, raw in cfg_defaults.items():
        if isinstance(raw, dict):
            if "value" in raw:                          # plain constant
                value = raw["value"]
                typ   = _TYPE_MAP.get(raw.get("type"), type(value))
            elif "generator" in raw:                    # computed at run time
                gen_name = raw["generator"]
                gen_fn   = generators.get(gen_name)
                if not isfunction(gen_fn):
                    raise ValueError(f"No generator named '{gen_name}'")

                # Use return annotation if present, otherwise default to Any
                ret_ann  = signature(gen_fn).return_annotation
                typ      = ret_ann if ret_ann is not inspect.Signature.empty else Any
                value    = Field(default_factory=gen_fn)   # defer execution
            else:
                raise ValueError(
                    f"Field '{key}' must define 'value' or 'generator'"
                )
        else:                                            # bare literal in YAML
            value, typ = raw, type(raw)

        fields[key] = (typ, value)

    return create_model(
        f"{get_config()['agent_inputs']['project_name'].replace('_', '').capitalize()}AgentInputs", __base__=BaseModel, **fields     # dynamic model
    )


def create_agent_inputs() -> BaseModel:
    """
    Create a Pydantic model instance for agent inputs using only
    the default values from the project config.
    """
    model_cls = _build_agent_inputs_model()
    cfg_defaults = get_config()["agent_inputs"]
    generators = get_generators()

    values: dict[str, Any] = {}
    for key, raw in cfg_defaults.items():
        if raw is None:
            continue
        if isinstance(raw, dict):
            if "value" in raw:
                values[key] = raw["value"]
            elif "generator" in raw:
                gen_fn = generators[raw["generator"]]
                # Provide already-resolved values so generators can be dependent
                values[key] = gen_fn(values)
        else:
            values[key] = raw

    return model_cls(**values)
