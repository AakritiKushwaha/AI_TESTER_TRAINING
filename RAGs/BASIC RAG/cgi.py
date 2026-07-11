"""Minimal compatibility shim for the stdlib cgi module on Python 3.14+."""

from email.message import Message
from typing import Tuple, Dict


def parse_header(line: str) -> Tuple[str, Dict[str, str]]:
    if not line:
        return "", {}
    message = Message()
    message["content-type"] = line
    return message.get_content_type(), dict(message.get_params(header="content-type"))


def parse_multipart(headers, fp, pdict=None):
    raise NotImplementedError("parse_multipart is not required for this local RAG demo")
