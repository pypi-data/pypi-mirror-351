# Connexity Pipecat

**Connexity Pipecat** is a flexible voice‑AI agent framework that pairs the audio‑first power of [Pipecat](https://github.com/voximetry/pipecat) with Twilio telephony and an LLM of your choice (OpenAI, Gemini, Groq, Fireworks, …). Use it to spin up production‑grade phone agents that can talk, listen and book meetings—all in real time.

---

## Contents

- [Installation](#installation)
  - [From PyPI](#from-pypi)
  - [Local development](#local-development)
- [Repository layout](#repository-layout)
- [Quick start](#quick-start)
- [Creating your own agent](#creating-your-own-agent)
  - [Project scaffold](#project-scaffold)
  - [Configuration file (`config.yaml`)](#configuration-file-configyaml)
    - [Dynamic variables (`generators`)](#dynamic-variables-generators)
    - [Registering custom tools](#registering-custom-tools)
    - [Registering custom handlers](#registering-custom-handlers)
  - [Built‑in handlers and processors](#built-in-libraries)
    - [Generators](#generators)
    - [Tools](#tools)
    - [Handlers](#handlers)
- [Environment variables](#environment-variables)
- [License](#license)

---

## Installation

### From PyPI

```bash
pip install connexity-pipecat
```

### Local development

```bash
git clone /link/
cd connexity-pipecat
pip install -e ".[dev,docs]"
```

---

## Repository layout

```
src/connexity_pipecat/
├── core/                 # Runtime core: agents, config, LLMs, tools
│   ├── tools/            # Built‑in tool registry + helpers
│   ├── generators/       # Data generators for dynamic prompt values
│   ├── voice_calls/      # Twilio integration helpers & templates
│   ├── config.py         # YAML loader + caching
│   └── ...
├── api/                  # FastAPI routers & handler glue
├── data/                 # Pydantic schemas, cache, constants
└── assets/               # Background audio & SFX
```

---

## Quick start

```python
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from connexity_pipecat import init_config, register_routes

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
init_config(str(PROJECT_ROOT / "config.yaml"))

app = FastAPI()
register_routes(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Start the server:

```bash
uvicorn main:app --reload
```

---

## Creating your own agent

### Project scaffold

```
my-agent/
├── main.py
├── .env
├── config.yaml
└── custom/
    ├── handlers/
    │   └── say_hi.py
    └── tools/
        ├── config.yaml
        └── functions/
            └── greet_user.py
```

### Configuration file (`config.yaml`)

Everything is driven by a single YAML file. A trimmed example:

```yaml
llm:
  main: {vendor: openai, model: gpt-4o-mini}

agent_inputs:
  agent_name: Emma
  current_timestamp: {generator: current_timestamp}  # evaluated at runtime

tools: ["end_call"]

routes:
  routers:
    - prefix: ""
      routes:
        - {path: /, methods: [POST], handler: platform_inference}
  websockets:
    - prefix: ""
      routes:
        - {path: /outbound/ws, handler: outbound_websocket_endpoint}
```


#### Full key reference

| Key (dot-notation) | Type | Allowed / typical values | Notes |
|--------------------|------|--------------------------|-------|
| `vad_params.confidence` | float | 0.0 – 1.0 | Voice-activity detector (higher = stricter). |
| `vad_params.min_volume` | float | 0.0 – 1.0 | Minimum RMS loudness considered speech. |
| `vad_params.start_secs` | float | > 0.0 | Silence threshold (s) before speech start. |
| `vad_params.stop_secs` | float | > 0.0 | Silence threshold (s) before speech end. |
| `llm.main.vendor` | str | `openai`, `groq`, `fireworks`, `google`, … | LLM backend for primary inference. |
| `llm.main.model` | str | Model name | e.g. `gpt-4o-mini`, `mixtral-8x7b`. |
| `llm.utils.vendor` | str | same as above | Lightweight helper LLM. |
| `llm.utils.model` | str | Model name | Used for summaries, embeddings, etc. |
| `use_connexity_observer` | bool | `true` / `false` | Push call metrics to Connexity API. |
| `pipeline_settings.audio_in_sample_rate` | int | 8000 – 48000 | Incoming PCM sample-rate (Hz). |
| `pipeline_settings.allow_interruptions` | bool | `true` / `false` | Let user barge-in over TTS. |
| `pipeline_settings.enable_metrics` | bool | `true` / `false` | Collect latency & token stats. |
| `pipeline_settings.report_only_initial_ttfb` | bool | `true` / `false` | Emit only first-token metrics. |
| `vector_db.type` | str | `Weaviate`, `Chroma`, `None` | External store for long-term memory. |
| `embedding.type` | str | Provider/model id | e.g. `OpenAI/text-embedding-3-small`. |
| `agent_inputs.project_name` | str | lowercase slug | Logical project grouping. |
| `agent_inputs.language_code` | ISO 639-1 | `en`, `de`, `es`, … | Used for STT/LLM model selection. |
| `agent_inputs.language` | str | Language name | Display-only. |
| `agent_inputs.translate_prompt` | bool | `true` / `false` | Auto-translate system prompt. |
| `agent_inputs.agent_name` | str | Human-friendly | “Emma”, “Max”, etc. |
| `agent_inputs.agent_company_name` | str | Free text | Company brand in prompts. |
| `agent_inputs.*.generator` | str | Function name | Any registered generator (see below). |
| `tools` | list[str] | Built-ins + custom | e.g. `["end_call", "book_appointment"]`. |
| `agent_id` | str | slug/UUID | Internal analytics identifier. |
| `routes.routers[].prefix` | str | Path prefix | Empty string = root. |
| `routes.routers[].routes[].path` | str | URL path | Must match FastAPI route. |
| `routes.routers[].routes[].methods` | list[str] | `["GET"]`, `["POST"]`, … | HTTP verbs. |
| `routes.routers[].routes[].handler` | str | Handler name | From `connexity_pipecat.api.handlers` or custom. |
| `routes.websockets[].prefix` | str | Path prefix | Usually empty. |
| `routes.websockets[].routes[].path` | str | URL path | WebSocket endpoint. |
| `routes.websockets[].routes[].handler` | str | Handler name | From `api.handlers` or custom. |
| `start_message` | str | Short greeting | Spoken when call connects (optional). |
| `prompts.agent.<lang>` | str (multiline) | Any | Primary system prompt. |
| `prompts.quick_response.<lang>` | str (multiline) | Any | Prompt for filler-phrase generator. |
| `prompts.post_analysis.<lang>` | str (multiline) | Any | Prompt for call summariser. |

<sup>Dot-notation shows nested keys; array items are marked with `[]`.</sup>

#### Dynamic variables (`generators`)

Any scalar can be generated dynamically with a function. Built‑ins include:

| Generator | What it returns |
|-----------|-----------------|
| `current_timestamp` | `"YYYY‑MM‑DD, Monday. Time: 15:04."` |
| `get_available_time_slots_str` | JSON list of free slots for next business days |

Add your own generator and register it with `register_custom_generators()`.

#### Registering custom tools

1. Describe your tool in **`custom/tools/config.yaml`**.  
2. Implement it in **`custom/tools/functions/`**.  
3. Register them:

```python
register_custom_tools("custom/tools/functions", "custom/tools/config.yaml")
```

#### Registering custom handlers

Drop additional FastAPI handlers in **`custom/handlers/`** and register:

```python
register_custom_handlers("custom/handlers")
```

### Built‑in handlers and processors

#### Generators (for computed agent_inputs)

- `current_timestamp`
- `get_available_time_slots_str`
- `get_grouped_calendar`

#### Tools

- `transfer_call`
- `end_call`
- `get_weekday`
- `get_available_time_slots`
- `await_call_transfer`
- `book_appointment`

#### Handlers

`connexity_pipecat.api.handlers` exposes reusable **FastAPI coroutine handlers** for both HTTP and WebSocket endpoints.  
You may add them to the `routes` section of your **`config.yaml`** as shown in the sample project.

| Path | Method(s) | Handler name | Purpose                                                     |
|------|-----------|--------------|-------------------------------------------------------------|
| `/` | `POST` | `platform_inference` | WNH platform text-only inference |
| `/initiate_phone_call` | `POST` | `initiate_phone_call` | Kick off an outbound Twilio call                            |
| `/voice_updates` | `POST` | `receive_voice_updates` | Update response-ID & turn-taking flags from the client      |
| `/call_status/{sid}` | `GET` | `status_callback_get` | Poll current call status                                    |
| `/call_status` | `POST` | `status_callback_post` | Twilio `StatusCallback` webhook                             |
| `/outbound/webhook` | `POST` | `outbound_webhook` | Return TwiML to connect Twilio ↔ WebSocket (outbound)       |
| `/inbound/webhook` | `POST` | `inbound_webhook` | Return TwiML to connect Twilio ↔ WebSocket (inbound)        |

**WebSocket endpoints**

| Path | Handler name | Purpose |
|------|--------------|---------|
| `/outbound/ws` | `outbound_websocket_endpoint` | Media stream for outbound calls |
| `/inbound/ws` | `inbound_websocket_endpoint` | Media stream for inbound calls |

Add the routes to your `config.yaml` like so:

```yaml
routes:
  routers:
    - prefix: ""
      routes:
        - {path: /, methods: [POST], handler: platform_inference}
        - {path: /initiate_phone_call, methods: [POST], handler: initiate_phone_call}
        - {path: /voice_updates, methods: [POST], handler: receive_voice_updates}
        - {path: /call_status/{sid}, methods: [GET], handler: status_callback_get}
        - {path: /call_status, methods: [POST], handler: status_callback_post}
        - {path: /outbound/webhook, methods: [POST], handler: outbound_webhook}
        - {path: /inbound/webhook, methods: [POST], handler: inbound_webhook}

  websockets:
    - prefix: ""
      routes:
        - {path: /outbound/ws, handler: outbound_websocket_endpoint}
        - {path: /inbound/ws, handler: inbound_websocket_endpoint}
```
---
## Environment variables

Create a `.env` next to `main.py`:

```
###############################################
# Connexity-Pipecat – Environment Variables   #
# Copy this file to `.env` and fill the blanks #
###############################################

##########################
# LLM provider API keys  #
##########################
OPENAI_API_KEY=
GROQ_API_KEY=
FIREWORKS_API_KEY=
# Google-Vertex / Gemini
GOOGLE_CREDENTIALS_JSON=

##########################
# Voice & speech         #
##########################
DEEPGRAM_API_KEY=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=

##########################
# Calendar / tools hooks #
##########################
TOOL_CHECK_SLOT_AVAILABILITY_WEBHOOK_URL=
TOOL_BOOKING_WEBHOOK_URL=

##########################
# Twilio telephony       #
##########################
TWILIO_ACCOUNT_ID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=+15555555555

####################################
# Public hostname of your FastAPI  #
####################################
# e.g. "voice.example.com" (no http://, no trailing slash)
SERVER_ADDRESS=

###########################################
# Optional call-status callback endpoint  #
###########################################
CALL_STATUS_URL=

###########################################################
# Connexity API #
###########################################################
CONNEXITY_API_KEY=
```

---

## License

MIT – see [LICENSE](LICENSE).
