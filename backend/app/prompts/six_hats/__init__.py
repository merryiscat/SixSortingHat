"""
6모자 프롬프트 모듈
"""

from .white_hat import WHITE_HAT_SYSTEM_PROMPT
from .red_hat import RED_HAT_SYSTEM_PROMPT
from .black_hat import BLACK_HAT_SYSTEM_PROMPT
from .yellow_hat import YELLOW_HAT_SYSTEM_PROMPT
from .green_hat import GREEN_HAT_SYSTEM_PROMPT
from .blue_hat import BLUE_HAT_SYSTEM_PROMPT

__all__ = [
    "WHITE_HAT_SYSTEM_PROMPT",
    "RED_HAT_SYSTEM_PROMPT",
    "BLACK_HAT_SYSTEM_PROMPT",
    "YELLOW_HAT_SYSTEM_PROMPT",
    "GREEN_HAT_SYSTEM_PROMPT",
    "BLUE_HAT_SYSTEM_PROMPT",
]