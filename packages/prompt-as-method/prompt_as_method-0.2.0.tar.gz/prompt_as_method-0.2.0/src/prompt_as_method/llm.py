import abc
from enum import Enum
import json
from typing import Iterator
from json_repair import repair_json
import requests

from pydantic import HttpUrl

from .data import DataFormat
from .prompt import PromptBase


class LLM(object):
    __metaclass__ = abc.ABCMeta

    def generate(
            self,
            prompt: PromptBase,
            response_format: DataFormat | None = None,
            repetitions: int = 1) -> Iterator[dict]:
        for _ in range(repetitions):
            yield self._generate_response(prompt, response_format)

    @abc.abstractmethod
    def _generate_response(
            self,
            prompt: PromptBase,
            response_format: DataFormat | None = None) -> dict:
        pass


class LLMType(Enum):
    openai = "OpenAI"

    def __str__(self):
        return self.value


class HttpLLM(LLM):

    def __init__(self, url: str):
        self._url = HttpUrl(url)

    @abc.abstractmethod
    def _prompt_to_request_data(
            self,
            prompt: PromptBase,
            response_format: DataFormat | None = None) -> dict:
        return {}

    def _generate_response(
            self,
            prompt: PromptBase,
            response_format: DataFormat | None = None) -> dict:
        request_data = json.dumps(self._prompt_to_request_data(prompt, response_format))
        response = requests.post(
            url=self._url.__str__(),
            headers={
                "Content-Type": "application/json"
            },
            data=request_data)
        if response.status_code != 200:
            raise ValueError(f"Error returned from {self._url}: {response.text}")
        response_dict = response.json()
        if response_format is not None:
            for choice in response_dict["choices"]:
                choice["message"]["content"] = repair_json(choice["message"]["content"])
        return response_dict

    @staticmethod
    def init(url: str, llm_type: LLMType = LLMType.openai) -> "HttpLLM":
        match llm_type:
            case LLMType.openai:
                return OpenAI(url)
            case _:
                raise ValueError(f"Invalid LLMType: {type(llm_type)}")


class ChatCompletion(PromptBase):
    stream: bool = False
    response_format: DataFormat | None = None


class OpenAI(HttpLLM):

    def __init__(self, url: str):
        super().__init__(url)

    def _prompt_to_request_data(
            self,
            prompt: PromptBase,
            response_format: DataFormat | None = None) -> dict:
        data = prompt.model_dump()
        if response_format is not None:
            data["response_format"] = response_format
        chat_completion = ChatCompletion.model_validate(data)
        return chat_completion.model_dump(exclude_none=True)
