from animations.specific_animations import (
    DestructionAnimation,
    MaterialiseAnimation,
    HealthChangeAnimation
)

class AnimationManager:
    """Manager for handling multiple animations."""

    def __init__(self):
        self.animations = []
        self.effect_animations = []
        self.ui_animations = []

    def add_animation(self, animation):
        self.animations.append(animation)

        if isinstance(animation, (DestructionAnimation, MaterialiseAnimation)):
            self.effect_animations.append(animation)
        elif isinstance(animation, (HealthChangeAnimation)):
            self.ui_animations.append(animation)

    def update(self, delta_time):

        self.animations = [anim for anim in self.animations if not anim.update(delta_time)]

        self.effect_animations = [anim for anim in self.effect_animations if not anim.is_completed]
        self.ui_animations = [anim for anim in self.ui_animations if not anim.is_completed]

    def draw_effects(self, surface):

        for animation in self.effect_animations:
            animation.draw(surface)

    def draw_ui_effects(self, surface):

        for animation in self.ui_animations:
            animation.draw(surface)

    def clear(self):
        self.animations.clear()
        self.effect_animations.clear()
        self.ui_animations.clear()

    def is_animating(self):
        return len(self.animations) > 0