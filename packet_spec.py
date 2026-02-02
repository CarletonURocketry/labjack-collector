"""
packet_spec.py

This file contains dataclass definitions of the packet header and packets from the packet specification
"""

from dataclasses import dataclass
from abc import ABC
from enum import Enum
import struct


class PacketType(Enum):
    CONTROL = 0
    TELEMETRY = 1


class ControlPacketSubType(Enum):
    ACT_REQ = 0
    ACT_ACK = 1
    ARM_REQ = 2
    ARM_ACK = 3


class TelemetryPacketSubType(Enum):
    TEMPERATURE = 0
    PRESSURE = 1
    MASS = 2
    THRUST = 3
    ARMING_STATE = 4
    ACT_STATE = 5
    WARNING = 6
    CONTINUITY = 7
    CONN_STATUS = 8


class ActuationResponse(Enum):
    ACT_OK = 0
    ACT_DENIED = 1
    ACT_DNE = 2
    ACT_INV = 3


class ArmingResponse(Enum):
    ARM_OK = 0
    ARM_DENIED = 1
    ARM_INV = 2


class ArmingState(Enum):
    ARMED_PAD = 0
    ARMED_VALVES = 1
    ARMED_IGNITION = 2
    ARMED_DISCONNECTED = 3
    ARMED_LAUNCH = 4
    NOT_AVAILABLE = 5


class ActuatorState(Enum):
    OFF = 0
    ON = 1


class Warning(Enum):
    HIGH_PRESSURE = 0
    HIGH_TEMP = 1


class ContinuityState(Enum):
    OPEN = 0
    CLOSED = 1
    NOT_AVAILABLE = 2


class IPConnectionStatus(Enum):
    CONNECTED = 0  # Connected
    RECONNECTING = 1  # Had connection, trying to restablish
    DISCONNECTED = 2  # Had connection, lost it
    NOT_CONNECTED = 3  # Not yet connected


@dataclass
class PacketHeader:
    type: PacketType
    sub_type: TelemetryPacketSubType


@dataclass
class PacketMessage(ABC):
    time_since_power: int


@dataclass
class TemperaturePacket(PacketMessage):
    temperature: int
    id: int

@dataclass
class PressurePacket(PacketMessage):
    pressure: int
    id: int

@dataclass
class MassPacket(PacketMessage):
    mass: int
    id: int

@dataclass
class ThrustPacket(PacketMessage):
    thrust: int
    id: int

@dataclass
class ArmingStatePacket(PacketMessage):
    state: ArmingState

@dataclass
class ConnectionStatusPacket(PacketMessage):
    status: IPConnectionStatus


def parse_packet_header(header_bytes: bytes) -> PacketHeader:
    packet_type: int
    packet_sub_type: int
    packet_type, packet_sub_type = struct.unpack("<BB", header_bytes)
    return PacketHeader(
        PacketType(packet_type), TelemetryPacketSubType(packet_sub_type)
    )