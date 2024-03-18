from pydantic import BaseModel


class OllamaChatMessage(BaseModel):
    role: str
    content: str
    images: list[str] | None = None


class OllamaChat(BaseModel):
    messages: list[OllamaChatMessage]


class OllamaCompletionResponseChunk(BaseModel):
    """
    Segment of the completion response
    """

    # True if completion was generated and this is final chunk
    done: bool

    created_at: str
    model: str
    message: OllamaChatMessage


class OllamaCompletionFinalChunk(OllamaCompletionResponseChunk):
    context: list[str] | None = None
    total_duration: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int


class OllamaModelTagDetails(BaseModel):
    format: str
    family: str
    families: None | list[str] = None
    parameter_size: str
    quantization_level: str


class OllamaModelTag(BaseModel):
    name: str
    modified_at: str
    size: int
    digest: str
    details: OllamaModelTagDetails
