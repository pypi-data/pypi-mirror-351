# -*- coding:utf-8 -*-
# Written for Python 3.12
# Formatted with Black

# Packet serializer for App_Io

from typing import Any, final

from pydantic import Field
from overrides import override

from .. import common
from .. import utils


@final
class Command(common.CommandBase):
    """Dataclass for App_Io command

    Attributes
    ----------
    di_to_change: common.FixedList[bool]
        To enable modification on a specific digital interface, set True
    di_state: common.FixedList[bool]
        Output status for each digital interfaces
    """

    di_to_change: common.FixedList[bool] = Field(
        default=common.FixedList[bool](
            12, [True, True, True, True, True, True, True, True, True, True, True, True]
        )
    )
    di_state: common.FixedList[bool] = Field(
        default=common.FixedList[bool](
            12,
            [
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
        )
    )

    @override
    def is_valid(self) -> bool:
        """Check if the command content is valid or not

        Returns
        -------
        bool
            True if valid

        Notes
        -----
        Overridden
        """

        return 0x00 <= self.destination_logical_id <= 0x78


@final
class CommandSerializer(common.CommandSerializerBase):
    """Command serializer for App_Io"""

    @staticmethod
    @override
    def serialize(command: common.SomeCommand) -> common.BarePacket | None:
        """Serialize the given command

        Parameters
        ----------
        command : common.SomeCommand
            App_Io command to serialize

        Returns
        -------
        common.BarePacket | None
            Serialized bytes and its LRC checksum (8bit) if valid

        Notes
        -----
        Static overridden method
        """

        if not (isinstance(command, Command) and command.is_valid()):
            return None

        payload_to_build: bytearray = bytearray()

        payload_to_build.append(min(command.destination_logical_id, 0x78))
        payload_to_build.append(0x80)
        payload_to_build.append(0x01)
        u16_di_state: int = sum(
            (1 if command.di_state[port] else 0) << port for port in range(12)
        )
        u16_di_to_change: int = sum(
            (1 if command.di_to_change[port] else 0) << port for port in range(12)
        )
        payload_to_build.append((u16_di_state >> 8) & 0xFF)
        payload_to_build.append((u16_di_state >> 0) & 0xFF)
        payload_to_build.append((u16_di_to_change >> 8) & 0xFF)
        payload_to_build.append((u16_di_to_change >> 0) & 0xFF)
        payload_to_build.extend([0, 0, 0, 0, 0, 0, 0, 0])

        serialized_packet: dict[str, Any] = {
            "payload": bytes(payload_to_build),
            "checksum": utils.lrc8(bytes(payload_to_build)),
        }

        return common.BarePacket(**serialized_packet)
