"""The Command-line Interface (CLI) for writing things with LLMs."""

import logging
from pathlib import Path

import click
from dotenv import load_dotenv

from .writing import write

load_dotenv(dotenv_path=".env")

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("write_a_thing")


@click.command(name="write-a-thing")
@click.argument("prompt", type=str, required=True)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    multiple=True,
    help="Path to a file containing information related to what you want to write.",
)
@click.option(
    "--model",
    type=str,
    default="gemini/gemini-2.5-pro-preview-05-06",
    show_default=True,
    help="The model to use for the agents.",
)
@click.option(
    "--temperature",
    type=float,
    default=0.0,
    show_default=True,
    help="The temperature to use for the model. Use 0.0 for greedy decoding.",
)
def main(prompt: str, file: list[str], model: str, temperature: float) -> None:
    """Write a thing using a prompt and an optional file."""
    write(
        prompt=prompt,
        file_paths=[Path(f) for f in file],
        model=model,
        temperature=temperature,
    )


if __name__ == "__main__":
    main()
