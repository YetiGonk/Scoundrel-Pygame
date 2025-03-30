""" Animation utilities for the Scoundrel game. """
import pygame
import math
import random

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
            return True
        
        return False
    
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
        
        # Calculate the current position
        progress = self.easing_function(self.get_progress())
        current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress
        
        # Update the target object's position
        self.target_object.update_position((current_x, current_y))
        
        return completed


class DestructionAnimation(Animation):
    """Animation for making a card disappear with effects."""
    
    def __init__(self, target_object, effect_type, duration=0.3, on_complete=None):
        super().__init__(duration, on_complete)
        self.target_object = target_object
        self.effect_type = effect_type
        self.original_scale = 1.0
        self.original_position = target_object.rect.topleft
        self.particles = []
        
        # Based on effect type, setup initial animation state
        if effect_type == "slash":
            # Create slash line data
            self.slash_angle = random.randint(15, 75)
            self.slash_direction = 1 if random.random() > 0.5 else -1
            self.slash_width = 5
            self.slash_color = (255, 0, 0)  # Red color for slash
            
        elif effect_type == "burn":
            # Create particles for burning effect
            for _ in range(20):
                self.particles.append({
                    'x': random.randint(0, target_object.rect.width),
                    'y': random.randint(0, target_object.rect.height),
                    'size': random.randint(3, 8),
                    'speed_y': -random.random() * 2 - 1,
                    'color': (
                        random.randint(200, 255),  # Red
                        random.randint(50, 150),   # Green
                        0                          # Blue
                    )
                })
                
        elif effect_type == "shatter":
            # Create particles for shatter effect
            for _ in range(15):
                self.particles.append({
                    'x': random.randint(0, target_object.rect.width),
                    'y': random.randint(0, target_object.rect.height),
                    'size': random.randint(5, 15),
                    'speed_x': (random.random() - 0.5) * 6,
                    'speed_y': (random.random() - 0.5) * 6,
                    'rotation': random.randint(0, 360),
                    'color': (100, 200, 255)  # Light blue for shatter
                })
    
    def draw(self, surface):
        progress = self.get_progress()
        
        if self.effect_type == "slash":
            if progress < 0.5:  # First half: slash appears
                # Draw the card
                self.target_object.draw(surface)
                
                # Draw slash line
                slash_progress = progress * 2  # Scale to 0-1 range in first half
                center_x = self.target_object.rect.centerx
                center_y = self.target_object.rect.centery
                slash_length = self.target_object.rect.width * 1.2
                
                # Start position
                start_x = center_x - slash_length/2 * math.cos(math.radians(self.slash_angle))
                start_y = center_y - slash_length/2 * math.sin(math.radians(self.slash_angle))
                
                # End position
                end_x = center_x + slash_length/2 * math.cos(math.radians(self.slash_angle))
                end_y = center_y + slash_length/2 * math.sin(math.radians(self.slash_angle))
                
                # Draw the slash line
                pygame.draw.line(
                    surface, 
                    self.slash_color,
                    (start_x, start_y),
                    (end_x, end_y),
                    self.slash_width
                )
            else:  # Second half: card splits
                # Calculate split distance
                split_distance = (progress - 0.5) * 2 * 100  # Scale to 0-100px in second half
                
                # Draw top half
                top_half = self.target_object.texture.subsurface(
                    (0, 0, self.target_object.rect.width, self.target_object.rect.height // 2)
                )
                surface.blit(
                    top_half, 
                    (
                        self.target_object.rect.x - split_distance * math.sin(math.radians(self.slash_angle)) * self.slash_direction,
                        self.target_object.rect.y - split_distance * math.cos(math.radians(self.slash_angle)) * self.slash_direction
                    )
                )
                
                # Draw bottom half
                bottom_half = self.target_object.texture.subsurface(
                    (0, self.target_object.rect.height // 2, 
                     self.target_object.rect.width, self.target_object.rect.height // 2)
                )
                surface.blit(
                    bottom_half, 
                    (
                        self.target_object.rect.x + split_distance * math.sin(math.radians(self.slash_angle)) * self.slash_direction,
                        self.target_object.rect.y + self.target_object.rect.height // 2 + split_distance * math.cos(math.radians(self.slash_angle)) * self.slash_direction
                    )
                )
        
        elif self.effect_type == "burn":
            if progress < 0.4:  # First phase: show card
                # Scale card based on progress (slight shrinking)
                scale = 1.0 - progress * 0.2
                self.target_object.update_scale(scale)
                self.target_object.draw(surface)
                
                # Draw fire particles
                for particle in self.particles:
                    size = int(particle['size'] * (1 - progress * 2))
                    if size > 0:
                        pygame.draw.circle(
                            surface,
                            particle['color'],
                            (
                                int(self.target_object.rect.x + particle['x']),
                                int(self.target_object.rect.y + particle['y'] + progress * 40 * particle['speed_y'])
                            ),
                            size
                        )
            elif progress < 0.7:  # Second phase: card burns away
                burn_progress = (progress - 0.4) / 0.3  # Normalize to 0-1
                # Draw partially burned card (decreasing height)
                height = int(self.target_object.rect.height * (1 - burn_progress))
                if height > 0:
                    card_texture = self.target_object.texture.subsurface(
                        (0, 0, self.target_object.rect.width, height)
                    )
                    surface.blit(card_texture, (self.target_object.rect.x, self.target_object.rect.y))
                
                # Draw more fire particles
                for particle in self.particles:
                    size = int(particle['size'] * (1 - burn_progress))
                    if size > 0:
                        pygame.draw.circle(
                            surface,
                            particle['color'],
                            (
                                int(self.target_object.rect.x + particle['x']),
                                int(self.target_object.rect.y + particle['y'] - burn_progress * 60)
                            ),
                            size
                        )
            # In final phase: card is completely gone, just some lingering particles
            else:
                fade_progress = (progress - 0.7) / 0.3  # Normalize to 0-1
                # Draw fading particles
                for particle in self.particles:
                    alpha = int(255 * (1 - fade_progress))
                    if alpha > 0:
                        particle_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
                        color_with_alpha = (particle['color'][0], particle['color'][1], particle['color'][2], alpha)
                        pygame.draw.circle(
                            particle_surface,
                            color_with_alpha,
                            (particle['size'], particle['size']),
                            particle['size']
                        )
                        surface.blit(
                            particle_surface,
                            (
                                int(self.target_object.rect.x + particle['x'] - particle['size']),
                                int(self.target_object.rect.y + particle['y'] - 80 * fade_progress - particle['size'])
                            )
                        )
        
        elif self.effect_type == "shatter":
            if progress < 0.3:  # First phase: card shakes
                shake_amount = 3 * math.sin(progress * 20)
                shake_x = self.original_position[0] + shake_amount
                shake_y = self.original_position[1] + shake_amount * 0.5
                self.target_object.update_position((shake_x, shake_y))
                self.target_object.draw(surface)
            else:  # Second phase: card shatters
                shatter_progress = (progress - 0.3) / 0.7  # Normalize to 0-1
                
                # Draw fading original card
                if shatter_progress < 0.5:
                    fade_alpha = int(255 * (1 - shatter_progress * 2))
                    if fade_alpha > 0:
                        original_texture = self.target_object.texture.copy()
                        # Create surface with alpha
                        faded_texture = pygame.Surface(original_texture.get_size(), pygame.SRCALPHA)
                        faded_texture.fill((255, 255, 255, fade_alpha))
                        # Use blend mode to apply alpha
                        faded_texture.blit(original_texture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        surface.blit(faded_texture, self.target_object.rect.topleft)
                
                # Draw particles
                for particle in self.particles:
                    # Apply velocity to position
                    current_x = particle['x'] + particle['speed_x'] * 100 * shatter_progress
                    current_y = particle['y'] + particle['speed_y'] * 100 * shatter_progress
                    
                    # Rotate and scale
                    rotation = particle['rotation'] + shatter_progress * 360
                    scale = 1.0 - shatter_progress * 0.8
                    
                    # Create a small card-like fragment
                    size = int(particle['size'] * scale)
                    if size > 2:
                        fragment = pygame.Surface((size, size), pygame.SRCALPHA)
                        pygame.draw.rect(
                            fragment,
                            particle['color'],
                            pygame.Rect(0, 0, size, size)
                        )
                        
                        # Rotate fragment
                        fragment = pygame.transform.rotate(fragment, rotation)
                        
                        # Draw with fade out
                        alpha = int(255 * (1 - shatter_progress))
                        if alpha > 0:
                            fragment.set_alpha(alpha)
                            surface.blit(
                                fragment,
                                (
                                    int(self.target_object.rect.x + current_x - size/2),
                                    int(self.target_object.rect.y + current_y - size/2)
                                )
                            )
    
    def update(self, delta_time):
        completed = super().update(delta_time)
        
        # Make the card invisible when animation is completed
        if completed:
            self.target_object.is_visible = False
            
        return completed


class MaterializeAnimation(Animation):
    """Animation for making a card appear at a destination."""
    
    def __init__(self, target_object, position, effect_type="sparkle", duration=0.3, on_complete=None):
        super().__init__(duration, on_complete)
        self.target_object = target_object
        self.position = position
        self.effect_type = effect_type
        self.particles = []
        
        # Set initial card position
        self.target_object.update_position(position)
        self.target_object.is_visible = True
        
        # Initialize effect
        if effect_type == "sparkle":
            # Create sparkle particles
            for _ in range(20):
                self.particles.append({
                    'x': random.randint(-20, target_object.rect.width + 20),
                    'y': random.randint(-20, target_object.rect.height + 20),
                    'size': random.randint(2, 5),
                    'speed': random.random() * 2 + 1,
                    'angle': random.random() * 360,
                    'color': (
                        random.randint(200, 255),  # R
                        random.randint(200, 255),  # G
                        random.randint(100, 200)   # B
                    )
                })
    
    def draw(self, surface):
        progress = self.get_progress()
        
        if self.effect_type == "sparkle":
            # Draw card with increasing opacity
            if progress < 0.7:
                # Scale from small to full size
                scale = 0.2 + progress * 1.1  # Start small and grow slightly bigger than 1.0
                if scale > 1.0 and progress > 0.6:  # Then shrink back to 1.0
                    scale = 1.0 + (0.7 - progress) * 2
                
                self.target_object.update_scale(scale)
                
                # Draw with increasing opacity
                alpha = int(min(255, progress * 2 * 255))
                card_texture = self.target_object.texture.copy()
                card_texture.set_alpha(alpha)
                surface.blit(card_texture, self.target_object.rect.topleft)
            else:
                # Card is fully visible
                self.target_object.update_scale(1.0)
                self.target_object.draw(surface)
            
            # Draw particles
            for particle in self.particles:
                # Calculate current position based on progress
                radius = particle['speed'] * progress * 50
                x = self.target_object.rect.centerx + particle['x'] + math.cos(math.radians(particle['angle'])) * radius
                y = self.target_object.rect.centery + particle['y'] + math.sin(math.radians(particle['angle'])) * radius
                
                # Calculate size (grows then shrinks)
                if progress < 0.5:
                    size = particle['size'] * progress * 2
                else:
                    size = particle['size'] * (1 - (progress - 0.5) * 2)
                
                if size > 0:
                    pygame.draw.circle(
                        surface,
                        particle['color'],
                        (int(x), int(y)),
                        int(size)
                    )
    
    def update(self, delta_time):
        completed = super().update(delta_time)
        
        # Make sure card is fully visible when animation completes
        if completed:
            self.target_object.is_visible = True
            self.target_object.update_scale(1.0)
            
        return completed


class AnimationManager:
    """Manager for handling multiple animations."""
    
    def __init__(self):
        self.animations = []
        self.effect_animations = []  # Separate list for visual effects that need to be drawn
    
    def add_animation(self, animation):
        self.animations.append(animation)
        
        # Check if this is a visual effect animation that needs to be drawn
        if isinstance(animation, (DestructionAnimation, MaterializeAnimation)):
            self.effect_animations.append(animation)
    
    def update(self, delta_time):
        # Update all animations and remove completed ones
        self.animations = [anim for anim in self.animations if not anim.update(delta_time)]
        
        # Also update effect animations list
        self.effect_animations = [anim for anim in self.effect_animations if not anim.is_completed]
    
    def draw_effects(self, surface):
        # Draw all effect animations
        for animation in self.effect_animations:
            animation.draw(surface)
    
    def clear(self):
        self.animations.clear()
        self.effect_animations.clear()
    
    def is_animating(self):
        return len(self.animations) > 0