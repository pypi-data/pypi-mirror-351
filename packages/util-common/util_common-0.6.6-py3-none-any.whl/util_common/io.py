import base64
import json
from typing import Dict, List, Optional

from util_common.decorator import deprecated
from util_common.path import FileExt, guess_extension_from_mime


@deprecated(src_func="io.json_to_str", replacement="io_util.json2str")
def json_to_str(
    json_: Dict | List | None,
    indent=4,
    ensure_ascii=False,
):
    return json.dumps(json_, indent=indent, ensure_ascii=ensure_ascii)


@deprecated(src_func="io.json_to_bytes", replacement="io_util.json2bytes")
def json_to_bytes(
    json_: Dict | List | None,
    indent=4,
    ensure_ascii=False,
    encoding="utf-8",
) -> bytes:
    return bytes(
        json_to_str(json_, indent=indent, ensure_ascii=ensure_ascii),
        encoding=encoding,
    )


@deprecated(src_func="io.str_to_bytes", replacement="io_util.str2bytes")
def str_to_bytes(text: str, encoding="utf-8") -> bytes:
    return bytes(text, encoding=encoding)


@deprecated(src_func="io.bytes_to_str", replacement="io_util.bytes2str")
def bytes_to_str(content: bytes, encoding="utf-8") -> str:
    return content.decode(encoding=encoding)


@deprecated(src_func="io.bytes_to_b64str", replacement="io_util.bytes2b64str")
def bytes_to_b64str(content: bytes, encoding="utf-8") -> str:
    return base64.b64encode(content).decode(encoding)


@deprecated(src_func="io.b64str_to_bytes", replacement="io_util.b64str2bytes")
def b64str_to_bytes(b64str: str) -> bytes:
    return base64.b64decode(b64str)


@deprecated(src_func="io.guess_file_extension", replacement="io_util.guess_extension")
def guess_file_extension(content: bytes) -> Optional[FileExt]:
    import magic

    mime = magic.from_buffer(content, mime=True).lower()
    ext = guess_extension_from_mime(mime)
    return ext


@deprecated(src_func="io.parse_bool", replacement="io_util.parse_bool")
def parse_bool(value: str | int | bool) -> bool:
    try:
        value = int(value)
    except Exception:
        pass
    if isinstance(value, bool) or isinstance(value, int):
        return bool(value)
    return value.lower().startswith("t") or value.lower().startswith("y")


@deprecated(src_func="io.parse_int", replacement="io_util.parse_int")
def parse_int(value: str | int | float) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except Exception as e:
            raise e
