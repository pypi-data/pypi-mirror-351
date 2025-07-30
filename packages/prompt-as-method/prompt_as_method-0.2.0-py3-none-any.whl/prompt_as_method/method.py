from pydantic import BaseModel, FilePath

from .task import Task
from .prompt import Prompt
from .prompt_template import PromptTemplate
from .llm import LLM, HttpLLM


class MethodResult(BaseModel):
    task: Task | None = None
    data: dict
    prompt: Prompt
    responses: list[dict]


class Method:

    def __init__(self, prompt_template: FilePath | PromptTemplate, llm: LLM | str):
        if isinstance(llm, LLM):
            self._llm: LLM = llm
        else:
            self._llm = HttpLLM.init(llm)
        if isinstance(prompt_template, PromptTemplate):
            self._prompt_template = prompt_template
        else:
            self._prompt_template = PromptTemplate(prompt_template)

    def process(self, data: dict, repetitions: int = 1) -> MethodResult:
        task = self._prompt_template.task
        response_format = None if task is None else task.output_format
        prompt = self._prompt_template.render(data)
        responses = self._llm.generate(prompt, response_format=response_format, repetitions=repetitions)
        return MethodResult(task=task, data=data, prompt=prompt, responses=list(responses))
