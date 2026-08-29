"""Optional Qwen adapter. Nothing imports or calls this module in offline lessons."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class QwenConfig:
    api_key: str
    base_url: str
    model: str
    enable_thinking: bool = False

    @classmethod
    def from_env(cls) -> "QwenConfig":
        api_key = (os.getenv("QWEN_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError("QWEN_API_KEY is not configured; offline lessons need no key")
        return cls(
            api_key=api_key,
            base_url=os.getenv(
                "QWEN_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
            model=os.getenv("QWEN_MODEL", "qwen3-vl-flash"),
            enable_thinking=os.getenv("QWEN_ENABLE_THINKING", "false").lower() == "true",
        )


def call_qwen(prompt: str, config: QwenConfig) -> str:
    """Make one explicit optional call; never used by tests or run_all_lessons.py."""

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError('Install the optional dependency with: pip install -e ".[qwen]"') from exc

    client = OpenAI(api_key=config.api_key, base_url=config.base_url)
    response = client.chat.completions.create(
        model=config.model,
        messages=[{"role": "user", "content": prompt}],
        extra_body={"enable_thinking": config.enable_thinking},
    )
    return response.choices[0].message.content or ""

