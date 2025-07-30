from pydantic import BaseModel, FilePath

from .task import Task
from .prompt import Prompt
from .prompt_template import PromptTemplate
from .llm import LLM, HttpLLM


class MethodTrace(BaseModel):
    task: Task | None = None
    prompt: Prompt
    responses: list[dict]


class MethodResult(BaseModel):
    input: dict
    outputs: list[dict | str]
    trace: MethodTrace | None = None


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
        outputs, responses = zip(*[self._llm.generate(prompt, response_format) for _ in range(repetitions)])
        trace = MethodTrace(task=task, prompt=prompt, responses=responses)  # type: ignore
        return MethodResult(input=data, outputs=outputs, trace=trace)  # type: ignore
