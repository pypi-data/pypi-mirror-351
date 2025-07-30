<a href="https://mono-wireless.com/jp/index.html">
    <img src="https://twelite.net/files/logo-land.svg" alt="mono wireless logo" title="MONO WIRELESS" align="right" height="60" />
</a>

# MWings (Lite edition)

A library that communicate with TWELITE wireless modules (Lite edition).

[![Lint with mypy / black / ruff](https://github.com/monowireless/mwings_python_lite/actions/workflows/lint.yml/badge.svg)](https://github.com/monowireless/mwings_python_lite/actions/workflows/lint.yml)
[![MW-OSSLA](https://img.shields.io/badge/License-MW--OSSLA-e4007f)](LICENSE)

## Overview

Receive packets from and send commands to TWELITE child devices through the connected TWELITE parent device.

The `App_Wings` firmware must be written to the TWELITE parent device connected to the host.

Built for Python 3.11+.

### Differences between `mwings` and `mwingslite`

- Renamed module to `mwingslite` from `mwings`
- Removed some heavy dependencies (pandas and its deps like numpy, pyarrow, etc.)
  - `to_df()` is not available, raises `EnvironmentError`
- Built for Python 3.11+ (not 3.12+)

Scripts are same as [original](https://github.com/monowireless/mwings_python). Only configs or docs are different.

### Receive packets from

  - `App_Twelite`
  - `App_IO`
  - `App_ARIA`
    - ARIA mode
  - `App_CUE`
    - CUE mode
    - PAL Event (Move/Dice) mode
  - `App_PAL`
    - AMBIENT
    - OPENCLOSE (CUE/ARIA OPENCLOSE mode)
    - MOTION
  - `App_Uart` (Mode A)
    - Simple
    - Extended
  - act

### Send commands to

  - `App_Twelite` (Signals)
  - `App_IO` (Digital Signals)
  - `App_PAL` (NOTICE)
    - Simple
    - Detailed
    - Event
  - `App_Uart` (Mode A)
    - Simple

## Installation

The package is available on [PyPI](https://pypi.org/project/mwingslite/).

Use `pip`

```
pip install mwingslite
```

Or `poetry`

```
poetry add mwingslite
```

## Features

### Written with modern python

*Modules of the modern python, by the modern python, for the modern python.*

- Fully typed; passes `mypy --strict`
- PEP8 compliance; formatted with `black` and passes `ruff check`
- Built with `poetry` and `pyproject.toml`
- numpy-style docstring, everywhere

### Great data portability

Received data can be exported easily.

- [`to_dict()`](https://monowireless.github.io/mwings_python_lite/mwingslite.html#mwingslite.common.ParsedPacketBase.to_dict) for dictionary
- [`to_json()`](https://monowireless.github.io/mwings_python_lite/mwingslite.html#mwingslite.common.ParsedPacketBase.to_json) for JSON string

> Data classes are derived from `pydantic.BaseModel`.

## Examples

### Receive App_Twelite packets

#### Using `Twelite.receive()`

Simplest way to receive some parsed packets.

Below script shows how to receive App_Twelite packets in blocking operations.

```python
import mwingslite as mw


def main() -> None:
    # Create twelite object
    twelite = mw.Twelite(mw.utils.ask_user_for_port())

    # Attach handlers
    @twelite.on(mw.Twelite.Packet.APP_TWELITE)
    def on_app_twelite(packet: mw.parsers.app_twelite.ParsedPacket) -> None:
        print(packet.to_json())

    # Receive packets
    while True:
        print(twelite.receive())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("...Aborting")
```

#### Using `Twelite.start()`

Practical way to receive some parsed packets.

The `Twelite` class is a subclass of the [`threading.Thread`](https://docs.python.org/3/library/threading.html#threading.Thread).

Below script shows how to receive packets in another thread.

```python
import mwingslite as mw


def main() -> None:
    # Create twelite object
    twelite = mw.Twelite(mw.utils.ask_user_for_port())

    # Attach handlers
    @twelite.on(mw.Twelite.Packet.APP_TWELITE)
    def on_app_twelite(packet: mw.parsers.app_twelite.ParsedPacket) -> None:
        print(packet.to_json())

    # Start receiving
    try:
        twelite.daemon = True
        twelite.start()
        print("Started receiving")
        while True:
            twelite.join(0.5)
    except KeyboardInterrupt:
        print("...Stopping")
        twelite.stop()
        print("Stopped")


if __name__ == "__main__":
    main()
```

> Note that event handlers are not called from the main thread.
> When you have to use parsed data from the main thread, data should be passed by `queue` or something.

### Send App_Twelite packets

To send packets, just create a command and send it.

Below script shows how to blink an LED on the DO1 port.

```python
from time import sleep
from typing import Any

import mwingslite as mw


def main() -> None:
    # Create twelite objec
    twelite = mw.Twelite(mw.utils.ask_user_for_port())

    # Create command (initialize in pydantic style)
    initial: dict[str, Any] = {
        "destination_logical_id": 0x78,
        "di_to_change": [True, False, False, False],
        "di_state": [False, False, False, False],
    }
    command = mw.serializers.app_twelite.Command(**initial)

    # Blinking
    while True:
        command.di_state[0] = not command.di_state[0]
        twelite.send(command)
        print(f"Flip DO1: {command.di_state[0]}")
        sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("...Aborting")
```

> Note that command data classes (such as `mw.serializers.app_twelite.Command`) are derived from [`pydantic.BaseModel`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.

**See more advanced examples at [mwings_python_lite/examples at main](https://github.com/monowireless/mwings_python_lite/tree/main/examples).**

## LICENSE

MW-OSSLA
