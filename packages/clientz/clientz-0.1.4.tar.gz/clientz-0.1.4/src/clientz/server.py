""" server save """
import time
import uuid
import asyncio
import importlib.resources
from typing import List, Optional, Dict, Union, Literal
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse
import yaml
from .core import ChatBox


class ChatMessage(BaseModel):
    """ x """
    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str] = None
    # tool_calls: Optional[...] # Add if you support tool/function calling
    # tool_call_id: Optional[...] # Add if you support tool/function calling

class ChatCompletionRequest(BaseModel):
    """ x """
    model: str  # The model name you want your service to expose
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1 # How many chat completion choices to generate for each input message.
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = 2048 # Adjusted default for flexibility
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    # Add other parameters if your model supports them (e.g., seed, tool_choice)

# --- Response Models (Non-Streaming) ---

class ChatCompletionMessage(BaseModel):
    """ x """
    role: Literal["assistant", "tool"] # Usually assistant
    content: Optional[str] = None
    # tool_calls: Optional[...]

class Choice(BaseModel):
    """ x """
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[Literal["stop", "length", "tool_calls",
                                    "content_filter", "function_call"]] = "stop"
    # logprobs: Optional[...]

class UsageInfo(BaseModel):
    """ x """
    prompt_tokens: int = 0 # You might need to implement token counting
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    """ x """
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}")
    object: Literal["chat.completion"] = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str # Echo back the model requested or the one used
    choices: List[Choice]
    usage: UsageInfo = Field(default_factory=UsageInfo)
    # system_fingerprint: Optional[str] = None

# --- Response Models (Streaming) ---

class DeltaMessage(BaseModel):
    """ x """
    role: Optional[Literal["system", "user", "assistant", "tool"]] = None
    content: Optional[str] = None
    # tool_calls: Optional[...]

class ChunkChoice(BaseModel):
    """ x """
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length", "tool_calls",
                                    "content_filter", "function_call"]] = None
    # logprobs: Optional[...]

class ChatCompletionChunkResponse(BaseModel):
    """ x """
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}")
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChunkChoice]
    # system_fingerprint: Optional[str] = None
    # usage: Optional[UsageInfo] = None

# --- FastAPI App ---

app = FastAPI(
    title="LLM Service",
    description="Provides an OpenAI-compatible API for custom large language models.",
    version="1.0.1",
)

# --- Configure CORS ---
# ! Add this section !
# Define allowed origins. Be specific in production!
# Example: origins = ["http://localhost:3000", "https://your-frontend-domain.com"]
origins = [
    "*", # Allows all origins (convenient for development, insecure for production)
    # Add the specific origin of your "别的调度" tool/frontend if known
    # e.g., "http://localhost:5173" for a typical Vite frontend dev server
    # e.g., "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specifies the allowed origins
    allow_credentials=True, # Allows cookies/authorization headers
    allow_methods=["*"],    # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],    # Allows all headers (Content-Type, Authorization, etc.)
)
# --- End CORS Configuration ---



def load_config():
    """ load_config """
    with importlib.resources.open_text('clientz', 'config.yaml') as f:
        return yaml.safe_load(f)


dicts = load_config()
ModelCards = dicts.get("ModelCards")
Custom = dicts.get("Custom")

chatbox = ChatBox()


# --- (Optional) Authentication Dependency ---
async def verify_api_key(authorization: Optional[str] = Header(None)):
    """
    Placeholder for API key verification.
    In a real application, you'd compare this to a stored list of valid keys.
    """
    if not authorization:
        # Allow requests without Authorization for local testing/simplicity
        # OR raise HTTPException for stricter enforcement
        # raise HTTPException(status_code=401, detail="Authorization header missing")
        print("Warning: Authorization header missing.")
        return None # Or a default principal/user if needed

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")

    token = authorization.split(" ")[1]
    # --- Replace this with your actual key validation logic ---
    # Example:
    # valid_keys = {"your-secret-key-1", "your-secret-key-2"}
    # if token not in valid_keys:
    #     raise HTTPException(status_code=401, detail="Invalid API Key")
    # print(f"Received valid API Key (last 4 chars): ...{token[-4:]}")
    # --- End Replace ---
    print(f"Received API Key (placeholder validation): ...{token[-4:]}")
    return token # Return the token or an identifier associated with it

# --- Mock LLM Call ---
async def generate_mock_llm_response(prompt: str, stream: bool, model: str):
    """
    Replace this with your actual LLM call logic.
    This mock function simulates generating text.
    """
    response_id = f"chatcmpl-{uuid.uuid4().hex}"
    created_time = int(time.time())

    if not stream:
        full_response = chatbox.product(prompt_with_history = prompt,model=model)
        # full_response = " ".join(words)
        words = full_response.split(' ')
        choice = Choice(
            index=0,
            message=ChatCompletionMessage(role="assistant", content=full_response),
            finish_reason="stop"
        )
        # Simulate token counts (highly inaccurate)
        usage = UsageInfo(prompt_tokens=len(prompt.split()),
                          completion_tokens=len(words),
                          total_tokens=len(prompt.split()) + len(words))
        return ChatCompletionResponse(
            id=response_id,
            model=model,
            choices=[choice],
            usage=usage,
            created=created_time
        )
    else:
        async def stream_generator():
            # First chunk: Send role
            first_chunk_choice = ChunkChoice(index=0, delta=DeltaMessage(role="assistant"),
                                                                finish_reason=None)
            yield ChatCompletionChunkResponse(
                id=response_id, model=model, choices=[first_chunk_choice], created=created_time
            ).model_dump_json() # Use model_dump_json() for Pydantic v2

            # Subsequent chunks: Send content word by word

            for i, word in enumerate(chatbox.stream_product(prompt_with_history = prompt,
                                                            model=model)):
                chunk_choice = ChunkChoice(index=0,
                                           delta=DeltaMessage(content=f"{word}"),
                                                                finish_reason=None)
                yield ChatCompletionChunkResponse(
                    id=response_id, model=model, choices=[chunk_choice], created=created_time
                ).model_dump_json()
                await asyncio.sleep(0.05) # Simulate token generation time

            # Final chunk: Send finish reason
            final_chunk_choice = ChunkChoice(index=0, delta=DeltaMessage(), finish_reason="stop")
            yield ChatCompletionChunkResponse(
                id=response_id, model=model, choices=[final_chunk_choice], created=created_time
            ).model_dump_json()

            # End of stream marker (specific to SSE)
            yield "[DONE]"

        # Need to wrap the generator for EventSourceResponse
        async def event_publisher():
            try:
                async for chunk in stream_generator():
                    yield {"data": chunk}
                    await asyncio.sleep(0.01) # Short delay between sending chunks is good practice
            except asyncio.CancelledError as e:
                print("Streaming connection closed by client.")
                raise e

        return EventSourceResponse(event_publisher())


# --- API Endpoint Implementation ---

@app.post(
    "/v1/chat/completions",
    response_model=None, # Response model needs dynamic handling (stream vs non-stream)
    summary="Chat Completions",
    description="Creates a model response for the given chat conversation.",
    tags=["Chat"],
)
async def create_chat_completion(
    request: ChatCompletionRequest,
    # token: str = Depends(verify_api_key) # Uncomment to enable authentication
):
    """ use """
    # --- 1. Prepare Prompt for your LLM ---
    # This is highly dependent on your specific model.
    # You might concatenate messages, add special tokens, etc.
    # Example simplistic prompt concatenation:
    prompt_for_llm = "\n".join([f"{msg.role}: {msg.content}"
                                for msg in request.messages if msg.content])
    print("-" * 20)
    print(f"Received Request for model: {request.model}")
    print(f"Streaming: {request.stream}")
    # print(f"Prompt for LLM:\n{prompt_for_llm}") # Be careful logging prompts with sensitive data
    print("-" * 20)

    # --- 2. Call your LLM Backend ---
    # Replace `generate_mock_llm_response` with your actual LLM call
    # Pass necessary parameters like temperature, max_tokens etc. from the request
    try:
        response_data = await generate_mock_llm_response(
            prompt=prompt_for_llm,
            stream=request.stream,
            model=request.model # Echo back the requested model
        )
    except Exception as e:
        print(f"Error calling LLM backend: {e}")
        raise HTTPException(status_code=500, detail=f"LLM backend error: {str(e)}") from e


    # --- 3. Format and Return Response ---
    if request.stream:
        if not isinstance(response_data, EventSourceResponse):
            raise HTTPException(status_code=500, detail=
                                 "Streaming response was not generated correctly.")
        return response_data # Return the SSE stream directly
    else:
        if not isinstance(response_data, ChatCompletionResponse):
            raise HTTPException(status_code=500,
                                 detail="Non-streaming response was not generated correctly.")
        return response_data # FastAPI automatically converts Pydantic model to JSON

# --- Add Root Endpoint for Health Check/Info ---
@app.get("/")
async def root():
    """ x """
    return {"message": "LLM Service is running."}

# --- (Optional) Add other OpenAI-like endpoints if needed ---
# For example, /v1/models to list available models
class ModelCard(BaseModel):
    """ x """
    id: str
    object: Literal["model"] = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "zhaoxuefeng" # Customize as needed

class ModelList(BaseModel):
    """ x """
    object: Literal["list"] = "list"
    data: List[ModelCard] = []

@app.get("/v1/models", response_model=ModelList,  tags=["Models"])
async def list_models():
    """ x """
    # Replace with your actual list of models
    available_models = [ModelCard(id=ModelCardName) for ModelCardName in ModelCards + Custom]
    return ModelList(data=available_models)


if __name__ == "__main__":
    # 这是一个标准的 Python 入口点惯用法
    # 当脚本直接运行时 (__name__ == "__main__")，这里的代码会被执行
    # 当通过 python -m YourPackageName 执行 __main__.py 时，__name__ 也是 "__main__"
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        'port',
        metavar='PORT',
        type=int,
        nargs='?', # 端口是可选的
        default=8000,
        help='Specify alternate port [default: 8000]'
    )

    args = parser.parse_args()

    # 使用 uvicorn.run() 来启动服务器
    # 参数对应于命令行选项
    uvicorn.run(
        app, # 要加载的应用，格式是 "module_name:variable_name"
        host="0.0.0.0",
        port=args.port,
        reload=False  # 启用热重载
    )
