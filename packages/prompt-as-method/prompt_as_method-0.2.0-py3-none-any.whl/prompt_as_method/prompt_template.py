from pathlib import Path
import chevron
from pydantic import FilePath

from .prompt import Prompt
from .task import get_task


# https://stackoverflow.com/a/33900452
def sanitize(value):
    if isinstance(value, dict):
        value = {sanitize(k): sanitize(v) for k, v in value.items()}
    elif isinstance(value, list):
        value = [sanitize(v) for v in value]
    elif isinstance(value, str):
        value = value.replace('"', '\\"')
    return value


class PromptTemplate:

    def __init__(
            self,
            template_file_name: FilePath | None = None,
            template_string: str | None = None):
        if template_string is not None:
            if template_file_name is None:
                self._template_string = template_string
            else:
                raise ValueError("Both file_name and template_string were provided")
        elif template_file_name is not None:
            with open(template_file_name) as template_file:
                self._template_string = template_file.read()
        else:
            raise ValueError("Neither file_name nor template_string were provided")
        base_prompt = self._render()
        self._task_id = base_prompt.task
        self._base_prompt = base_prompt.model_dump()
        del self._base_prompt["messages"]
        if self._task_id is not None:
            base_path = None if template_file_name is None else Path(template_file_name).parent
            self.task = get_task(self._task_id, base_path=base_path)

    def render(self, data: dict) -> Prompt:
        # TODO check against input format
        prompt = self._render(data)
        # assert that the base prompt did not change
        prompt_dumped = prompt.model_dump()
        del prompt_dumped["messages"]
        assert self._base_prompt == prompt_dumped
        return prompt

    def _render(self, data: dict = {}) -> Prompt:
        rendered: str = chevron.render(self._template_string, sanitize(data))  # type: ignore
        return Prompt.model_validate_json(rendered)
