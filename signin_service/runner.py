from __future__ import annotations

from .actions import ActionRunner
from .config import AppConfig, Task


class TaskRunner:
    def __init__(self, config: AppConfig, device: object, dry_run: bool, logger: object) -> None:
        self.config = config
        self.device = device
        self.dry_run = dry_run
        self.logger = logger
        self.actions = ActionRunner(device, config.safety, dry_run, logger)

    def run_all(self, only: str | None = None) -> None:
        for task in self.config.tasks:
            if only and task.name != only:
                continue
            if not task.enabled:
                self.logger.info("Skip disabled task: %s", task.name)
                continue
            self.run_task(task)

    def run_task(self, task: Task) -> None:
        self.logger.info("Start task: %s", task.name)
        try:
            if task.app:
                self.actions.action_open_app(task.name, app=task.app, stop=False, wait=3)
            for step in task.steps:
                self.actions.run_step(step.action, step.params, task.name)
            self.logger.info("Finished task: %s", task.name)
        except Exception:
            self.logger.exception("Task failed: %s", task.name)
            try:
                self.actions.action_screenshot(task.name, name="error")
            except Exception:
                self.logger.exception("Failed to capture error screenshot")

