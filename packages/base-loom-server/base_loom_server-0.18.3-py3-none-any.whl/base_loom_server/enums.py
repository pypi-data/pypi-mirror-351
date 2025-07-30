import enum


class ConnectionStateEnum(enum.IntEnum):
    """Client websocket connection state."""

    DISCONNECTED = 0
    CONNECTED = 1
    CONNECTING = 2
    DISCONNECTING = 3


class DirectionControlEnum(enum.IntEnum):
    BOTH = 1
    LOOM = 2
    SOFTWARE = 3


class MessageSeverityEnum(enum.IntEnum):
    """Severity for text messages"""

    INFO = 1
    WARNING = 2
    ERROR = 3


class ModeEnum(enum.IntEnum):
    WEAVE = 1
    THREAD = 2
    TEST = 3


class ShaftStateEnum(enum.IntEnum):
    """Shaft state"""

    UNKNOWN = 0
    DONE = 1
    MOVING = 2
    ERROR = 3
