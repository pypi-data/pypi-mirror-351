from .cli import cli
from .processor import LoomxProcessor
from .config import LoomxConfig


def main() -> None:
    cli()


__all__ = ["main", "LoomxProcessor", "LoomxConfig"]
