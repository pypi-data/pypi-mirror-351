# Prompt-as-Method

[![PyPI - Version](https://img.shields.io/pypi/v/prompt-as-method)](https://pypi.org/project/prompt-as-method/)
[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FGESIS-Methods-Hub%2Fprompt-as-method%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)](https://github.com/GESIS-Methods-Hub/prompt-as-method)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/GESIS-Methods-Hub/prompt-as-method/test.yml?label=tests)](https://github.com/GESIS-Methods-Hub/prompt-as-method/actions/workflows/test.yml)
[![Static Badge](https://img.shields.io/badge/licence-MIT-%2395c30d)](https://github.com/GESIS-Methods-Hub/prompt-as-method/blob/main/LICENSE)

Run prompts from files.

## Install

```shell
pip install prompt-as-method
```

## Quickstart

If you have an [Ollama](https://ollama.com/download) running on the default port on your local machine:

```shell
ollama pull llama3.1  # download model
python3 -m prompt_as_method \
    --prompt examples/sentiment/prompt.json \
    --data examples/sentiment/data.csv
```

This runs the prompt template [`examples/sentiment/prompt.json`](examples/sentiment/prompt.json) for each row of [`examples/sentiment/data.csv`](examples/sentiment/data.csv) with `{{{text}}}` replaced by the row's value for it.

## Contributing

See the [development notes](https://github.com/GESIS-Methods-Hub/prompt-as-method/blob/main/docs/development.md).
