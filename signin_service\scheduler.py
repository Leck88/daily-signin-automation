from __future__ import annotations

import time
from datetime import datetime

from .runner import TaskRunner


class SimpleScheduler:
    def __init__(self, runner: TaskRunner, logger: object, poll_seconds: int = 30) -> None:
        self.runner = runner
        self.logger = logger
        self.poll_seconds = poll_seconds
        self._ran_keys: set[str] = set()

    def run_forever(self) -> None:
        self.logger.info("Scheduler started")
        while True:
            now = datetime.now()
            minute_key = now.strftime("%Y-%m-%d %H:%M")
            for task in self.runner.config.tasks:
                if not task.enabled or not task.schedule:
                    continue
                run_key = f"{task.name}:{minute_key}"
                if task.schedule == now.strftime("%H:%M") and run_key not in self._ran_keys:
                    self._ran_keys.add(run_key)
                    self.runner.run_task(task)
            time.sleep(self.poll_seconds)

