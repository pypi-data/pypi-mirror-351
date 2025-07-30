import base64
import json
import re
from io import StringIO
from typing import Dict, List, Optional

from util_common.path import FileExt, guess_extension_from_mime


def json2str(
    json_: Dict | List | None,
    indent=4,
    ensure_ascii=False,
):
    return json.dumps(json_, indent=indent, ensure_ascii=ensure_ascii)


def json2bytes(
    json_: Dict | List | None,
    indent=4,
    ensure_ascii=False,
    encoding="utf-8",
) -> bytes:
    return bytes(
        json2str(json_, indent=indent, ensure_ascii=ensure_ascii),
        encoding=encoding,
    )


def str2bytes(text: str, encoding="utf-8") -> bytes:
    return bytes(text, encoding=encoding)


def bytes2str(content: bytes, encoding="utf-8") -> str:
    return content.decode(encoding=encoding)


def bytes2b64str(content: bytes, encoding="utf-8") -> str:
    return base64.b64encode(content).decode(encoding)


def b64str2bytes(b64str: str) -> bytes:
    return base64.b64decode(b64str)


def guess_extension(content: bytes) -> Optional[FileExt]:
    import magic

    mime = magic.from_buffer(content, mime=True).lower()
    ext = guess_extension_from_mime(mime)
    return ext


def parse_format(
    text: str, type_hint="json"
):  # Renamed 'type' to 'type_hint' to avoid conflict with built-in
    # Try to find a block like ```type\nCONTENT```
    pattern_typed_block = (
        rf"```{type_hint}\s*\n(.*?)(?:\n```|\Z)"  # Matches until \n``` or end of string
    )
    match = re.search(pattern_typed_block, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: try to find any block like ```\nCONTENT```
    pattern_any_block = r"```\s*\n(.*?)(?:\n```|\Z)"
    match = re.search(pattern_any_block, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: if text STARTS with ```type\n (e.g. from a direct LLM response with no preamble)
    pattern_starts_with_typed = rf"^\s*```{type_hint}\s*\n(.*?)(?:\n```|\Z)"
    match = re.search(pattern_starts_with_typed, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: if text STARTS with ```\n
    pattern_starts_with_any = r"^\s*```\s*\n(.*?)(?:\n```|\Z)"
    match = re.search(pattern_starts_with_any, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # If no ``` block is found at all, but there's a preamble ending with ```<type>
    # This is closer to your original logic if closing ``` is missing
    pattern_opening_only = rf"```{type_hint}\s*\n(.*)"
    match = re.search(pattern_opening_only, text, re.DOTALL)
    if match:
        # This might grab too much if there's trailing text after the intended CSV
        # and no closing ```. Careful with this one.
        return match.group(1).strip()

    return text.strip()  # Default to returning the stripped original text if no patterns match well


def parse_json(text: str):
    import json_repair

    code_text = parse_format(text, type_hint="json")
    try:
        return json_repair.loads(code_text)
    except Exception:
        return None


def parse_csv2json(text: str):
    import csv

    import pandas as pd

    code_text = parse_format(text, type_hint="csv")

    try:
        df = pd.read_csv(
            StringIO(code_text),
            dtype=str,
            escapechar="\\",
        ).astype(str)
        df = df.replace("nan", "")
        return df.to_dict(orient="records")
    except Exception:
        try:
            lines = code_text.strip().split("\n")
            if not lines:
                return None
            headers = next(csv.reader([lines[0]]))
            data_rows = []

            for line in lines[1:]:
                try:
                    row = next(csv.reader([line]))
                    if len(row) == len(headers):
                        data_rows.append(row)
                    elif len(row) > len(headers):
                        data_rows.append(row[: len(headers)])
                    elif len(row) < len(headers):
                        row.extend([""] * (len(headers) - len(row)))
                        data_rows.append(row)
                except Exception:
                    continue

            if data_rows:
                df = pd.DataFrame(data_rows, columns=pd.Index(headers)).astype(str)
                df = df.replace("nan", "")
                return df.to_dict(orient="records")
            else:
                return None

        except Exception:
            return None
