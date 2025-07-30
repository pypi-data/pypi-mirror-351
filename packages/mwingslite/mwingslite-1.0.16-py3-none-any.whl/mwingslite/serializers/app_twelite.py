# -*- coding:utf-8 -*-
# Written for Python 3.12
# Formatted with Black

# Packet serializer for App_Twelite

from typing import Any, final

from pydantic import Field
from overrides import override

from .. import common
from .. import utils


@final
class Command(common.CommandBase):
    """Dataclass for App_Twelite command

    Attributes
    ----------
    di_to_change: common.FixedList[bool]
        To enable modification on a specific digital interface, set True
    di_state: common.FixedList[bool]
        Output status for each digital interfaces
    pwm_to_change: common.FixedList[bool]
        To enable modification on a specific PWM interface, set True
    pwm_duty: common.FixedList[bool]
        Duty for each PWM interfaces (0 to 1024, can be disabled with 0xFFFF)
    """

    di_to_change: common.FixedList[bool] = Field(
        default=common.FixedList[bool](4, [True, True, True, True])
    )
    di_state: common.FixedList[bool] = Field(
        default=common.FixedList[bool](4, [False, False, False, False])
    )
    pwm_to_change: common.FixedList[bool] = Field(
        default=common.FixedList[bool](4, [True, True, True, True])
    )
    pwm_duty: common.FixedList[int] = Field(
        default=common.FixedList[int](4, [0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF])
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

        return 0x00 <= self.destination_logical_id <= 0x78 and all(
            duty <= 1024 or duty == 0xFFFF for duty in self.pwm_duty
        )


@final
class CommandSerializer(common.CommandSerializerBase):
    """Command serializer for App_Twelite"""

    @staticmethod
    @override
    def serialize(command: common.SomeCommand) -> common.BarePacket | None:
        """Serialize the given command

        Parameters
        ----------
        command : common.SomeCommand
            App_Twelite command to serialize

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
        payload_to_build.append(
            sum((1 if command.di_state[port] else 0) << port for port in range(4))
        )
        payload_to_build.append(
            sum((1 if command.di_to_change[port] else 0) << port for port in range(4))
        )
        for port in range(4):
            if not (command.pwm_to_change[port]) or command.pwm_duty[port] == 0xFFFF:
                payload_to_build.extend([0xFF, 0xFF])
            else:
                payload_to_build.extend(
                    [
                        (min(command.pwm_duty[port], 1024) >> 8) & 0xFF,
                        (min(command.pwm_duty[port], 1024) >> 0) & 0xFF,
                    ]
                )

        serialized_packet: dict[str, Any] = {
            "payload": bytes(payload_to_build),
            "checksum": utils.lrc8(bytes(payload_to_build)),
        }

        return common.BarePacket(**serialized_packet)
