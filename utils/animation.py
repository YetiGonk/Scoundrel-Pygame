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
    """Animation for moving an object from one position to another with optional rotation and scaling."""
    
    def __init__(self, target_object, start_pos, end_pos, duration, 
            easing_function=EasingFunctions.ease_out_quad, on_complete=None,
            start_rotation=0, end_rotation=0, start_scale=1.0, end_scale=1.0):
        super().__init__(duration, on_complete)
        self.target_object = target_object
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.easing_function = easing_function
        
        # New properties for enhanced animations
        self.start_rotation = start_rotation
        self.end_rotation = end_rotation
        self.start_scale = start_scale
        self.end_scale = end_scale
        
        # Store original texture for scaling
        if hasattr(target_object, 'texture') and hasattr(target_object, 'original_texture'):
            self.original_texture = target_object.original_texture
        else:
            self.original_texture = None
            
        # Set rotation attribute if needed
        if hasattr(target_object, 'rotation'):
            self.target_object.rotation = start_rotation
        
        # Set current scale
        if hasattr(target_object, 'scale'):
            self.target_object.scale = start_scale
    
    def update(self, delta_time):
        completed = super().update(delta_time)
        
        # Calculate the current position
        progress = self.easing_function(self.get_progress())
        
        # Position
        current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress
        
        # Update the target object's position
        self.target_object.update_position((current_x, current_y))
        
        # Rotation
        if self.start_rotation != self.end_rotation and hasattr(self.target_object, 'rotation'):
            current_rotation = self.start_rotation + (self.end_rotation - self.start_rotation) * progress
            self.target_object.rotation = current_rotation
            
            # Apply rotation if the object has a rotate method
            if hasattr(self.target_object, 'rotate'):
                self.target_object.rotate(current_rotation)
        
        # Scale
        if self.start_scale != self.end_scale and self.original_texture is not None:
            current_scale = self.start_scale + (self.end_scale - self.start_scale) * progress
            
            # Update scale attribute
            if hasattr(self.target_object, 'scale'):
                self.target_object.scale = current_scale
            
            # Apply scaling to texture if possible
            if hasattr(self.target_object, 'texture') and hasattr(self.target_object, 'width') and hasattr(self.target_object, 'height'):
                new_width = int(self.target_object.width * current_scale)
                new_height = int(self.target_object.height * current_scale)
                
                # Only scale if dimensions are reasonable
                if new_width > 0 and new_height > 0:
                    import pygame
                    self.target_object.texture = pygame.transform.scale(
                        self.original_texture, 
                        (new_width, new_height)
                    )
        
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