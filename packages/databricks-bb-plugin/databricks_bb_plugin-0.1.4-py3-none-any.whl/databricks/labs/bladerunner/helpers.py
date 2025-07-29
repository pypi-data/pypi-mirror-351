import json

from json.decoder import WHITESPACE  # type: ignore[attr-defined]
from pathlib import Path
from typing import Any

from lsprotocol.types import Range, Position


def full_range(source_code: str) -> Range:
    source_lines = source_code.split("\n")
    return Range(
        start=Position(0, 0), end=Position(len(source_lines), len(source_lines[-1]))
    )


def map_dialect_to_source_tech(dialect: str) -> str:
    dialect = dialect.upper()
    if "INFORMATICA" in dialect:
        if "DESKTOP" in dialect:
            return "INFAPC"
        if "BIG DATA EDITION" in dialect:
            return "INFACLOUD"
    return dialect


class _JsonDecoder(json.JSONDecoder):

    def decode(self, s: str, _w=WHITESPACE.match) -> Any:
        s = "\n".join(self._strip_comments(line) for line in s.split("\n"))
        return super().decode(s, _w)

    @classmethod
    def _strip_comments(cls, line: str) -> str:
        idx = line.find("//")
        if idx < 0:
            return line
        if idx == 0:
            return ""
        # assume the '//' is not within a literal
        return line[0:idx]


# pylint: disable=too-few-public-methods
class JSONReader:

    @staticmethod
    def load(path: Path) -> Any:
        with open(path, encoding="utf-8") as f:
            return json.load(f, cls=_JsonDecoder)
