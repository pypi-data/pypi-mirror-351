import argparse

from .method import Method
from .data import read_data


parser = argparse.ArgumentParser(
    prog="prompt-as-method",
    description="Executes a method that is programmed as a prompt for a generative model"
)
parser.add_argument(
    "--prompt", type=str, required=True,
    help="Prompt template file (.json or .mustache; can be a URL) according to OpenAI chat completion API with variables"
    " enclosed in double curly braces (see mustache syntax)"
)
parser.add_argument(
    "--data", type=str, required=True,
    help="File with value assignment for template variables (variable names are column headers for .csv and .tsv files, and"
    " attribute names for .ndjson files; can be a URL), with the model being called separately for the values in each row of"
    " the file (except the header for .csv and .tsv)"
)
parser.add_argument(
    "--model-api", type=str, default="http://localhost:11434/v1/chat/completions",
    help="URL of the chat completion API endpoint (default is local Ollama server)"
)
parser.add_argument(
    "--repetitions", type=int, default=1,
    help="How often each prompt (row in values file) should be repeated (default: 1)"
)
parser.add_argument(
    "--trace", action="store_true",
    help="Whether to add the method trace to the output"
)

opts = parser.parse_args()

method = Method(opts.prompt, opts.model_api)
for data in read_data(opts.data):
    result = method.process(data, repetitions=opts.repetitions)
    if not opts.trace:
        result.trace = None
    print(result.model_dump_json(exclude_none=True), flush=True)
