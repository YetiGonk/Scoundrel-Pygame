""" Animation utilities for the Scoundrel game. """

class Animation:
    """Base class for animations."""
    
    def __init__(self, duration, on_complete=None):
        self.duration = duration
        self.elapsed_time = 0
        self.is_completed = False
        self.on_complete = on_complete
    
    def update(self, delta_time):
        if self.is_completed:
            return True
        
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.duration:
            self.elapsed_time = self.duration
            self.is_completed = True
            if self.on_complete:
                self.on_complete()
        
        return self.is_completed
    
    def reset(self):
        self.elapsed_time = 0
        self.is_completed = False
    
    def get_progress(self):
        return min(1.0, self.elapsed_time / self.duration)


class EasingFunctions:
    """Static class containing various easing functions."""
    
    @staticmethod
    def linear(progress):
        return progress
    
    @staticmethod
    def ease_in_quad(progress):
        return progress * progress
    
    @staticmethod
    def ease_out_quad(progress):
        return 1 - (1 - progress) * (1 - progress)
    
    @staticmethod
    def ease_in_out_quad(progress):
        if progress < 0.5:
            return 2 * progress * progress
        else:
            return 1 - pow(-2 * progress + 2, 2) / 2


class MoveAnimation(Animation):
    """Animation for moving an object from one position to another."""
    
    def __init__(self, target_object, start_pos, end_pos, duration, easing_function=EasingFunctions.ease_out_quad, on_complete=None):
        super().__init__(duration, on_complete)
        self.target_object = target_object
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.easing_function = easing_function
    
    def update(self, delta_time):
        completed = super().update(delta_time)

        print("Updating MoveAnimation for object:", self.target_object)
        
        # Calculate the current position
        progress = self.easing_function(self.get_progress())
        current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress
        
        # Update the target object's position
        self.target_object.update_position((current_x, current_y))
        
        return completed


class AnimationManager:
    """Manager for handling multiple animations."""
    
    def __init__(self):
        self.animations = []
    
    def add_animation(self, animation):
        self.animations.append(animation)
    
    def update(self, delta_time):
        # Update all animations and remove completed ones
        self.animations = [anim for anim in self.animations if not anim.update(delta_time)]
    
    def clear(self):
        self.animations.clear()
    
    def is_animating(self):
        return len(self.animations) > 0