import abc
from enum import Enum
import json
from json_repair import repair_json
import requests

from pydantic import HttpUrl

from .data import DataFormat
from .prompt import PromptBase


class LLM(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def generate(
            self,
            prompt: PromptBase,
            response_format: DataFormat | None = None) -> tuple[str | dict, dict]:
        pass


class LLMType(Enum):
    openai = "OpenAI"

    def __str__(self):
        return self.value


class HttpLLM(LLM):

    def __init__(self, url: str):
        self._url = HttpUrl(url)

    def generate(
            self,
            prompt: PromptBase,
            response_format: DataFormat | None = None) -> tuple[str | dict, dict]:
        request_data = json.dumps(self._prompt_to_request_data(prompt, response_format))
        response = requests.post(
            url=self._url.__str__(),
            headers={
                "Content-Type": "application/json"
            },
            data=request_data)
        if response.status_code != 200:
            raise ValueError(f"Error returned from {self._url}: {response.text}")
        response_text, response_data = self._get_response_data(response)
        if response_format is None:
            return response_text, response_data
        else:
            return json.loads(repair_json(response_text)), response_data

    @staticmethod
    def init(url: str, llm_type: LLMType = LLMType.openai) -> "HttpLLM":
        match llm_type:
            case LLMType.openai:
                return OpenAI(url)
            case _:
                raise ValueError(f"Invalid LLMType: {type(llm_type)}")

    @abc.abstractmethod
    def _prompt_to_request_data(
            self,
            prompt: PromptBase,
            response_format: DataFormat | None = None) -> dict:
        pass

    @abc.abstractmethod
    def _get_response_data(self, response: requests.Response) -> tuple[str, dict]:
        pass


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

    def _get_response_data(self, response: requests.Response) -> tuple[str, dict]:
        response_dict = response.json()
        return response_dict["choices"][0]["message"]["content"], response_dict
