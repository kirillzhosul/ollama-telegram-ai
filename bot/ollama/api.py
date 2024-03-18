"""
    API wrapper around ollama

    TODO: Plain (non-chat) implementation
    TODO: Async HTTP
"""

from json import loads
from logging import getLogger
from typing import Any, Final, Generator

from requests import Response, get, post

from bot.settings import OLLAMA_API_HOST

from .dto import (
    OllamaChatMessage,
    OllamaCompletionFinalChunk,
    OllamaCompletionResponseChunk,
    OllamaModelTag,
)

logger = getLogger("ollama.api")


def get_installed_models() -> list[OllamaModelTag]:
    return [
        OllamaModelTag.model_validate(tag)
        for tag in (
            get(f"{OLLAMA_API_HOST}/api/tags", allow_redirects=False)
            .json()
            .get("models", [])
        )
    ]


def model_is_installed(model_id: str) -> bool:
    for model in get_installed_models():
        if model.name in (model_id, f"{model_id}:latest"):
            return True
    return False


def request_chat_completion(
    messages: list[OllamaChatMessage],
    model: str,
    stream: bool = True,
    **ollama_options: Any,
) -> Response:
    """
    Returns streaming response that does generates response from the model
    """
    ollama_params = {
        "model": model,
        "messages": [message.model_dump() for message in messages],
        "stream": stream,
        "options": ollama_options,
    }
    logger.debug(f"Requesting chat completion with {model=}, {stream=}...")
    return post(
        f"{OLLAMA_API_HOST}/api/chat",
        json=ollama_params,
        stream=stream,
        allow_redirects=False,
        timeout=None,
    )


def generate_raw_chat_completion(
    messages: list[OllamaChatMessage],
    model: str,
    **ollama_options: Any,
) -> Generator[dict[str, Any], Any, None]:
    """
    Generates chunked chat response and returns it as-is (raw)
    """
    RESPONSE_SEGMENT_ENCODING: Final[str] = "utf-8"

    for segment in request_chat_completion(
        messages, model, **ollama_options, stream=True
    ).iter_lines():
        if not segment:
            continue

        raw_segment: dict[str, Any] = loads(segment.decode(RESPONSE_SEGMENT_ENCODING))
        if "done" not in raw_segment:
            continue

        yield raw_segment


def generate_chat_completion(
    messages: list[OllamaChatMessage],
    model: str,
    **ollama_options: Any,
) -> Generator[tuple[bool, OllamaCompletionResponseChunk], Any, None]:
    """
    Generates chunked chat response
    """
    for raw_segment in generate_raw_chat_completion(messages, model, **ollama_options):
        segment_dto = OllamaCompletionResponseChunk
        if is_done := raw_segment.get("done", False):
            segment_dto = OllamaCompletionFinalChunk
        yield is_done, segment_dto.model_validate(raw_segment)
