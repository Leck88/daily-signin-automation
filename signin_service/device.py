from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

import uiautomator2 as u2


@dataclass
class DeviceHandle:
    serial: str
    client: object


def list_adb_devices() -> list[str]:
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
    devices: list[str] = []
    for line in result.stdout.splitlines():
        match = re.match(r"^([^\s]+)\s+device$", line.strip())
        if match:
            devices.append(match.group(1))
    return devices


def choose_device(configured_serial: str | None = None) -> str:
    devices = list_adb_devices()
    if configured_serial:
        if configured_serial not in devices:
            raise RuntimeError(f"Configured device {configured_serial} is not connected")
        return configured_serial
    if not devices:
        raise RuntimeError("No Android device found. Run `adb devices` first.")
    if len(devices) == 1:
        return devices[0]
    raise RuntimeError(f"Multiple devices found, set `device` in config: {', '.join(devices)}")


def connect_device(configured_serial: str | None = None) -> DeviceHandle:
    serial = choose_device(configured_serial)
    return DeviceHandle(serial=serial, client=u2.connect(serial))

