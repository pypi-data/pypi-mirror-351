from __future__ import annotations
import os
import textwrap

from groq import Groq

from .base import LLMProvider

MODEL_NAME = "llama-3.3-70b-versatile"

SYSTEM_MSG = (
    "You are an expert SAP ABAP moderniser. "
    "Convert legacy ABAP to modern ABAP 7.5+ syntax. "
    "Keep comments; return *only* the updated code."
)

PROMPT_TEMPLATE = textwrap.dedent(
    """
    Convert the following legacy ABAP code to modern ABAP syntax compatible with S/4HANA 7.5.

Use inline declarations (DATA(...)), expressions (VALUE, REDUCE, FILTER, etc.), and constructor operators where applicable.

Replace outdated statements like READ TABLE WITH KEY, LOOP AT ... INTO, APPEND, etc. with their modern equivalents.

Do not include any explanation or documentation in the output. Only return the updated ABAP code.

If documentation_required = 'X' is passed, only then include a separate block with explanations after the code.

Input:
    Do not add explanations.

    ```abap
    {legacy}
    ```
    """
)


class GroqProvider(LLMProvider):
    def __init__(self, *, api_key: str | None = None) -> None:
        api_key = api_key or os.getenv("GROQAI_API_KEY")
        if not api_key:
            raise RuntimeError("GROQAI_API_KEY missing in .env")
        self._client = Groq(api_key=api_key)

    # ── synchronous, non-streaming ────────────────────────────────────────
    def modernise_code(self, legacy_code: str) -> str:
        prompt = PROMPT_TEMPLATE.format(legacy=legacy_code.strip())

        resp = self._client.chat.completions.create(
            model=MODEL_NAME,
            stream=False,
            temperature=0.3,
            top_p=1,
            messages=[
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user", "content": prompt},
            ],
        )
        return resp.choices[0].message.content.strip()
