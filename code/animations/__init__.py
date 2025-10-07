"""
Animation system and specific animations
"""

from .animation_base import Animation, EasingFunctions
from .specific_animations import (
    MoveAnimation,
    DestructionAnimation,
    MaterialiseAnimation,
    HealthChangeAnimation
)
from .animation_controller import AnimationController

__all__ = [
    'Animation',
    'EasingFunctions',
    'MoveAnimation',
    'DestructionAnimation',
    'MaterialiseAnimation',
    'HealthChangeAnimation',
    'AnimationController',
]