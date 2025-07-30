import dataclasses

from .enums import DirectionControlEnum


@dataclasses.dataclass
class Settings:
    loom_name: str
    direction_control: DirectionControlEnum
    thread_left_to_right: bool
    thread_back_to_front: bool
