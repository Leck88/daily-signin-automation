from __future__ import annotations

import argparse

from .config import load_config
from .device import connect_device
from .logger import setup_logger
from .runner import TaskRunner
from .scheduler import SimpleScheduler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Android daily sign-in automation service")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("run", "schedule"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--config", default="config/tasks.yaml")
        sub.add_argument("--device", default=None)
        sub.add_argument("--only", default=None, help="Run one task by exact name")
        mode = sub.add_mutually_exclusive_group()
        mode.add_argument("--dry-run", action="store_true", help="Match steps without clicking")
        mode.add_argument("--execute", action="store_true", help="Actually click on the device")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    logger = setup_logger()
    dry_run = not args.execute
    if dry_run:
        logger.warning("Running in dry-run mode. Use --execute to click on device.")

    config = load_config(args.config)
    serial = args.device or config.device
    handle = connect_device(serial)
    logger.info("Connected device: %s", handle.serial)

    runner = TaskRunner(config, handle.client, dry_run=dry_run, logger=logger)
    if args.command == "run":
        runner.run_all(only=args.only)
    elif args.command == "schedule":
        SimpleScheduler(runner, logger).run_forever()


if __name__ == "__main__":
    main()

