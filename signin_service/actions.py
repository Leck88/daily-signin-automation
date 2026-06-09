from __future__ import annotations

import time
from pathlib import Path
from time import strftime
from typing import Any

from .config import SafetyConfig


class ActionRunner:
    def __init__(self, device: Any, safety: SafetyConfig, dry_run: bool, logger: Any) -> None:
        # self.d 是 uiautomator2 连接后的设备对象，所有点击、滑动、截图都从这里发给手机。
        self.d = device
        # safety 负责拦截“支付、下单、充值、授权”等高风险按钮，避免签到脚本误触敏感操作。
        self.safety = safety
        # dry_run=True 时只查找控件，不真正点击，适合第一次适配某个 App 时预演。
        self.dry_run = dry_run
        self.logger = logger

    def run_step(self, action: str, params: dict[str, Any], task_name: str) -> None:
        # YAML 里的 action 会映射到 action_xxx 方法，例如 click_text -> action_click_text。
        handler = getattr(self, f"action_{action}", None)
        if handler is None:
            raise ValueError(f"Unsupported action: {action}")
        self.logger.info("Step %s %s", action, params)
        handler(task_name=task_name, **params)

    def _guard_click(self, label: str | None) -> bool:
        # 所有点击统一经过这里，后续要加更严格的白名单/黑名单也只需要改这一处。
        if self.safety.is_blocked(label):
            self.logger.warning("Blocked risky click target: %s", label)
            return False
        return True

    def _click_selector(self, selector: Any, label: str | None, timeout: float = 5) -> bool:
        # wait 会等待控件出现；网络慢或 App 冷启动时可在 YAML 里调大 timeout。
        if not selector.wait(timeout=timeout):
            self.logger.info("Target not found: %s", label)
            return False
        if not self._guard_click(label):
            return False
        if self.dry_run:
            self.logger.info("Dry-run matched target: %s", label)
            return True
        selector.click()
        return True

    def action_open_app(self, task_name: str, app: str | None = None, stop: bool = False, wait: float = 3) -> None:
        # app 是安卓包名，例如支付宝是 com.eg.android.AlipayGphone。
        if not app:
            raise ValueError("open_app requires app")
        if self.dry_run:
            self.logger.info("Dry-run open app: %s", app)
        else:
            self.d.app_start(app, stop=stop, use_monkey=True)
        time.sleep(wait)

    def action_click_text(self, task_name: str, text: str, timeout: float = 5, wait: float = 1) -> None:
        selector = self.d(text=text)
        clicked = self._click_selector(selector, text, timeout=timeout)
        if clicked:
            time.sleep(wait)

    def action_click_text_any(self, task_name: str, texts: list[str], timeout: float = 3, wait: float = 1) -> None:
        # 适合一个按钮有多种文案的场景，例如“签到 / 立即签到 / 领积分”。
        for text in texts:
            selector = self.d(text=text)
            if self._click_selector(selector, text, timeout=timeout):
                time.sleep(wait)
                return
        self.logger.info("No candidate text matched: %s", texts)

    def action_click_text_contains(self, task_name: str, text: str, timeout: float = 5, wait: float = 1) -> None:
        # 模糊匹配文案，适合“签到领 10 积分”这类每天可能变化的按钮。
        selector = self.d(textContains=text)
        clicked = self._click_selector(selector, text, timeout=timeout)
        if clicked:
            time.sleep(wait)

    def action_click_text_contains_any(self, task_name: str, texts: list[str], timeout: float = 3, wait: float = 1) -> None:
        # 多候选模糊匹配：只要任一关键词出现在控件文字里就点击。
        for text in texts:
            selector = self.d(textContains=text)
            if self._click_selector(selector, text, timeout=timeout):
                time.sleep(wait)
                return
        self.logger.info("No candidate fuzzy text matched: %s", texts)

    def action_click_desc(self, task_name: str, desc: str, timeout: float = 5, wait: float = 1) -> None:
        # 有些 App 的按钮没有 text，但有 accessibility description，可以用 desc 定位。
        selector = self.d(description=desc)
        clicked = self._click_selector(selector, desc, timeout=timeout)
        if clicked:
            time.sleep(wait)

    def action_swipe(self, task_name: str, direction: str = "up", scale: float = 0.6, wait: float = 1) -> None:
        # direction 支持 uiautomator2 的方向值，常用 up/down/left/right。
        if self.dry_run:
            self.logger.info("Dry-run swipe: %s", direction)
        else:
            self.d.swipe_ext(direction, scale=scale)
        time.sleep(wait)

    def action_back(self, task_name: str, wait: float = 1) -> None:
        if self.dry_run:
            self.logger.info("Dry-run back")
        else:
            self.d.press("back")
        time.sleep(wait)

    def action_wait(self, task_name: str, seconds: float = 1) -> None:
        time.sleep(seconds)

    def action_screenshot(self, task_name: str, name: str | None = None) -> None:
        # 截图统一保存到 logs/screenshots，失败排查时直接看最后一张图。
        Path("logs/screenshots").mkdir(parents=True, exist_ok=True)
        safe_task = "".join(ch if ch.isalnum() else "_" for ch in task_name)
        filename = f"{strftime('%Y%m%d-%H%M%S')}-{safe_task}-{name or 'screen'}.png"
        path = Path("logs/screenshots") / filename
        if self.dry_run:
            self.logger.info("Dry-run screenshot: %s", path)
            return
        self.d.screenshot(str(path))
        self.logger.info("Saved screenshot: %s", path)
