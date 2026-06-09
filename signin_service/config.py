from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


DEFAULT_BLOCK_KEYWORDS = [
    "支付",
    "付款",
    "购买",
    "立即买",
    "买入",
    "下单",
    "提交订单",
    "确认订单",
    "充值",
    "借款",
    "贷款",
    "授权",
    "开通",
    "免密",
    "邀请",
    "助力",
    "砍价",
]


@dataclass
class SafetyConfig:
    block_keywords: list[str] = field(default_factory=lambda: DEFAULT_BLOCK_KEYWORDS.copy())

    def is_blocked(self, text: str | None) -> bool:
        if not text:
            return False
        return any(keyword in text for keyword in self.block_keywords)


@dataclass
class Step:
    action: str
    params: dict[str, Any]


@dataclass
class Task:
    name: str
    app: str | None
    enabled: bool
    schedule: str | None
    steps: list[Step]


@dataclass
class AppConfig:
    device: str | None
    safety: SafetyConfig
    tasks: list[Task]


def load_config(path: str | Path) -> AppConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    safety_raw = raw.get("safety") or {}
    block_keywords = DEFAULT_BLOCK_KEYWORDS.copy()
    block_keywords.extend(safety_raw.get("extra_block_keywords") or [])
    block_keywords.extend(safety_raw.get("block_keywords") or [])

    tasks: list[Task] = []
    for item in raw.get("tasks") or []:
        steps = []
        for step_raw in item.get("steps") or []:
            action = step_raw.get("action")
            if not action:
                raise ValueError(f"Task {item.get('name')} has a step without action")
            params = {key: value for key, value in step_raw.items() if key != "action"}
            steps.append(Step(action=action, params=params))
        tasks.append(
            Task(
                name=item["name"],
                app=item.get("app"),
                enabled=item.get("enabled", True),
                schedule=item.get("schedule"),
                steps=steps,
            )
        )

    return AppConfig(
        device=raw.get("device"),
        safety=SafetyConfig(block_keywords=sorted(set(block_keywords))),
        tasks=tasks,
    )

