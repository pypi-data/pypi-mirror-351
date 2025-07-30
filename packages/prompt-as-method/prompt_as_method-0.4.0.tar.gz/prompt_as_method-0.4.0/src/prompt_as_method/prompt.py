from typing import Annotated, Literal, Union
from pydantic import AfterValidator, BaseModel, Field


class BaseMessage(BaseModel):
    content: str


class AssistantMessage(BaseMessage):
    role: Literal["assistant"] = "assistant"


class SystemMessage(BaseMessage):
    role: Literal["system"] = "system"


class UserMessage(BaseMessage):
    role: Literal["user"] = "user"


Message = Annotated[Union[AssistantMessage, SystemMessage, UserMessage], Field(discriminator="role")]


def last_message_is_of_user(value: list[Message]) -> list[Message]:
    if len(value) < 1:
        raise ValueError("messages list must contain at least one message")
    if type(value[-1]) is not UserMessage:
        raise ValueError("last message must be a user message")
    return value


Messages = Annotated[list[Message], AfterValidator(last_message_is_of_user)]


temperature_min = 0
temperature_max = 2
temperature_default = 1
top_p_min = 0
top_p_max = 2
top_p_default = 1


class PromptParameters(BaseModel):
    model: str
    max_completion_tokens: int | None = None
    temperature: Annotated[float, Field(ge=temperature_min, le=temperature_max)] = temperature_default
    top_p: Annotated[float, Field(ge=top_p_min, le=top_p_max)] = top_p_default


class PromptBase(PromptParameters):
    messages: Messages


class Prompt(PromptBase):
    task: str | None = None
