import math
import pygame
import random

from animations.animation_base import Animation, EasingFunctions

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

        progress = self.easing_function(self.get_progress())
        current_x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        current_y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress

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

        if effect_type == "slash":

            self.slash_angle = random.randint(25, 65)
            self.slash_direction = 1 if random.random() > 0.5 else -1
            self.slash_width = 4
            self.slash_colour = (200, 200, 200)

        elif effect_type == "burn":

            for _ in range(20):
                self.particles.append({
                    'x': random.randint(0, target_object.rect.width),
                    'y': random.randint(0, target_object.rect.height),
                    'size': random.randint(3, 8),
                    'speed_y': -random.random() * 2 - 1,
                    'colour': (
                        random.randint(200, 255),
                        random.randint(50, 150),
                        0
                    )
                })

        elif effect_type == "shatter":

            for _ in range(15):
                self.particles.append({
                    'x': random.randint(0, target_object.rect.width),
                    'y': random.randint(0, target_object.rect.height),
                    'size': random.randint(5, 15),
                    'speed_x': (random.random() - 0.5) * 6,
                    'speed_y': (random.random() - 0.5) * 6,
                    'rotation': random.randint(0, 360),
                    'colour': (100, 200, 255)
                })

    def draw(self, surface):
        progress = self.get_progress()

        if self.effect_type == "slash":
            if progress < 0.4:

                self.target_object.draw(surface)

                slash_progress = progress / 0.4
                center_x = self.target_object.rect.centerx
                center_y = self.target_object.rect.centery
                slash_length = self.target_object.rect.width * 1.4

                offset = (slash_progress - 0.5) * self.target_object.rect.width * 1.5

                start_x = center_x - slash_length/2 * math.cos(math.radians(self.slash_angle)) + offset * self.slash_direction
                start_y = center_y - slash_length/2 * math.sin(math.radians(self.slash_angle)) + offset * self.slash_direction * 0.3

                end_x = center_x + slash_length/2 * math.cos(math.radians(self.slash_angle)) + offset * self.slash_direction
                end_y = center_y + slash_length/2 * math.sin(math.radians(self.slash_angle)) + offset * self.slash_direction * 0.3

                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (start_x, start_y),
                    (end_x, end_y),
                    self.slash_width + 2
                )

                pygame.draw.line(
                    surface,
                    self.slash_colour,
                    (start_x, start_y),
                    (end_x, end_y),
                    self.slash_width
                )

                for i in range(5):
                    spark_pos_x = start_x + (end_x - start_x) * (i / 4)
                    spark_pos_y = start_y + (end_y - start_y) * (i / 4)
                    spark_size = random.randint(1, 3)
                    pygame.draw.circle(
                        surface,
                        (255, 255, 255),
                        (int(spark_pos_x), int(spark_pos_y)),
                        spark_size
                    )

            elif progress < 0.55:

                self.target_object.draw(surface)

                center_x = self.target_object.rect.centerx
                center_y = self.target_object.rect.centery
                cut_length = self.target_object.rect.width * 1.2

                start_x = center_x - cut_length/2 * math.cos(math.radians(self.slash_angle))
                start_y = center_y - cut_length/2 * math.sin(math.radians(self.slash_angle))

                end_x = center_x + cut_length/2 * math.cos(math.radians(self.slash_angle))
                end_y = center_y + cut_length/2 * math.sin(math.radians(self.slash_angle))

                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (start_x, start_y),
                    (end_x, end_y),
                    2
                )

            else:

                split_progress = (progress - 0.55) / 0.45
                split_distance = 120 * math.pow(split_progress, 1.5)

                cut_height = self.target_object.rect.height * 0.5

                rotation = 5 * split_progress * self.slash_direction

                top_half = self.target_object.texture.subsurface(
                    (0, 0, self.target_object.rect.width, int(cut_height))
                )

                if rotation != 0:
                    top_half = pygame.transform.rotate(top_half, -rotation)

                surface.blit(
                    top_half,
                    (
                        self.target_object.rect.x - split_distance * math.sin(math.radians(self.slash_angle)) * self.slash_direction,
                        self.target_object.rect.y - split_distance * math.cos(math.radians(self.slash_angle)) * self.slash_direction
                    )
                )

                bottom_half = self.target_object.texture.subsurface(
                    (0, int(cut_height),
                     self.target_object.rect.width, self.target_object.rect.height - int(cut_height))
                )

                if rotation != 0:
                    bottom_half = pygame.transform.rotate(bottom_half, rotation)

                surface.blit(
                    bottom_half,
                    (
                        self.target_object.rect.x + split_distance * math.sin(math.radians(self.slash_angle)) * self.slash_direction,
                        self.target_object.rect.y + cut_height + split_distance * math.cos(math.radians(self.slash_angle)) * self.slash_direction
                    )
                )

                if split_progress < 0.7:
                    center_x = self.target_object.rect.centerx
                    center_y = self.target_object.rect.centery

                    for _ in range(3):
                        particle_x = center_x + (random.random() - 0.5) * 30
                        particle_y = center_y + (random.random() - 0.5) * 10
                        particle_size = random.randint(1, 3)

                        pygame.draw.circle(
                            surface,
                            (220, 220, 220),
                            (int(particle_x), int(particle_y)),
                            particle_size
                        )

        elif self.effect_type == "burn":
            if progress < 0.4:

                scale = 1.0 - progress * 0.2
                self.target_object.update_scale(scale)
                self.target_object.draw(surface)

                for particle in self.particles:
                    size = int(particle['size'] * (1 - progress * 2))
                    if size > 0:
                        pygame.draw.circle(
                            surface,
                            particle['colour'],
                            (
                                int(self.target_object.rect.x + particle['x']),
                                int(self.target_object.rect.y + particle['y'] + progress * 40 * particle['speed_y'])
                            ),
                            size
                        )
            elif progress < 0.7:
                burn_progress = (progress - 0.4) / 0.3

                height = int(self.target_object.rect.height * (1 - burn_progress))
                if height > 0:
                    card_texture = self.target_object.texture.subsurface(
                        (0, 0, self.target_object.rect.width, height)
                    )
                    surface.blit(card_texture, (self.target_object.rect.x, self.target_object.rect.y))

                for particle in self.particles:
                    size = int(particle['size'] * (1 - burn_progress))
                    if size > 0:
                        pygame.draw.circle(
                            surface,
                            particle['colour'],
                            (
                                int(self.target_object.rect.x + particle['x']),
                                int(self.target_object.rect.y + particle['y'] - burn_progress * 60)
                            ),
                            size
                        )

            else:
                fade_progress = (progress - 0.7) / 0.3

                for particle in self.particles:
                    alpha = int(255 * (1 - fade_progress))
                    if alpha > 0:
                        particle_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
                        colour_with_alpha = (particle['colour'][0], particle['colour'][1], particle['colour'][2], alpha)
                        pygame.draw.circle(
                            particle_surface,
                            colour_with_alpha,
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
            if progress < 0.3:
                shake_amount = 3 * math.sin(progress * 20)
                shake_x = self.original_position[0] + shake_amount
                shake_y = self.original_position[1] + shake_amount * 0.5
                self.target_object.update_position((shake_x, shake_y))
                self.target_object.draw(surface)
            else:
                shatter_progress = (progress - 0.3) / 0.7

                if shatter_progress < 0.5:
                    fade_alpha = int(255 * (1 - shatter_progress * 2))
                    if fade_alpha > 0:
                        original_texture = self.target_object.texture.copy()

                        faded_texture = pygame.Surface(original_texture.get_size(), pygame.SRCALPHA)
                        faded_texture.fill((255, 255, 255, fade_alpha))

                        faded_texture.blit(original_texture, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                        surface.blit(faded_texture, self.target_object.rect.topleft)

                for particle in self.particles:

                    current_x = particle['x'] + particle['speed_x'] * 100 * shatter_progress
                    current_y = particle['y'] + particle['speed_y'] * 100 * shatter_progress

                    rotation = particle['rotation'] + shatter_progress * 360
                    scale = 1.0 - shatter_progress * 0.8

                    size = int(particle['size'] * scale)
                    if size > 2:
                        fragment = pygame.Surface((size, size), pygame.SRCALPHA)
                        pygame.draw.rect(
                            fragment,
                            particle['colour'],
                            pygame.Rect(0, 0, size, size)
                        )

                        fragment = pygame.transform.rotate(fragment, rotation)

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

        if completed:
            self.target_object.is_visible = False

        return completed

class MaterialiseAnimation(Animation):
    """Animation for making a card appear at a destination."""

    def __init__(self, target_object, position, effect_type="sparkle", duration=0.3, on_complete=None):
        super().__init__(duration, on_complete)
        self.target_object = target_object
        self.position = position
        self.effect_type = effect_type
        self.particles = []

        self.target_object.update_position(position)
        self.target_object.is_visible = True

        if effect_type == "sparkle":

            for _ in range(20):
                self.particles.append({
                    'x': random.randint(-20, target_object.rect.width + 20),
                    'y': random.randint(-20, target_object.rect.height + 20),
                    'size': random.randint(2, 5),
                    'speed': random.random() * 2 + 1,
                    'angle': random.random() * 360,
                    'colour': (
                        random.randint(200, 255),
                        random.randint(200, 255),
                        random.randint(100, 200)
                    )
                })

    def draw(self, surface):
        progress = self.get_progress()

        if self.effect_type == "sparkle":

            if progress < 0.7:

                scale = 0.2 + progress * 1.1
                if scale > 1.0 and progress > 0.6:
                    scale = 1.0 + (0.7 - progress) * 2

                self.target_object.update_scale(scale)

                alpha = int(min(255, progress * 2 * 255))
                card_texture = self.target_object.texture.copy()
                card_texture.set_alpha(alpha)
                surface.blit(card_texture, self.target_object.rect.topleft)
            else:

                self.target_object.update_scale(1.0)
                self.target_object.draw(surface)

            for particle in self.particles:

                radius = particle['speed'] * progress * 50
                x = self.target_object.rect.centerx + particle['x'] + math.cos(math.radians(particle['angle'])) * radius
                y = self.target_object.rect.centery + particle['y'] + math.sin(math.radians(particle['angle'])) * radius

                if progress < 0.5:
                    size = particle['size'] * progress * 2
                else:
                    size = particle['size'] * (1 - (progress - 0.5) * 2)

                if size > 0:
                    pygame.draw.circle(
                        surface,
                        particle['colour'],
                        (int(x), int(y)),
                        int(size)
                    )

    def update(self, delta_time):
        completed = super().update(delta_time)

        if completed:
            self.target_object.is_visible = True
            self.target_object.update_scale(1.0)

        return completed

class HealthChangeAnimation(Animation):
    """Animation for displaying health changes with effects."""

    def __init__(self, is_damage, amount, position, font, duration=0.8, on_complete=None):
        super().__init__(duration, on_complete)
        self.is_damage = is_damage
        self.amount = amount
        self.position = position
        self.font = font
        self.particles = []

        num_particles = min(20, max(5, abs(amount) * 2))
        for _ in range(num_particles):
            self.particles.append({
                'x': random.randint(-10, 10),
                'y': random.randint(-5, 5),
                'speed_x': (random.random() - 0.5) * 5,
                'speed_y': -random.random() * 8 - 2,
                'size': random.randint(3, 7),
                'fade_speed': random.random() * 0.3 + 0.7
            })

    def draw(self, surface):
        progress = self.get_progress()

        if progress < 0.4:
            scale = 1.0 + progress * 0.5
            alpha = int(255 * min(1.0, progress * 3))

        elif progress < 0.7:
            scale = 1.2
            alpha = 255

        else:
            fade_progress = (progress - 0.7) / 0.3
            scale = 1.2 - fade_progress * 0.2
            alpha = int(255 * (1 - fade_progress))

        if self.is_damage:
            colour = (255, 80, 80)
            text_prefix = "-"
        else:
            colour = (80, 255, 80)
            text_prefix = "+"

        text = self.font.render(f"{text_prefix}{abs(self.amount)}", True, colour)

        if scale != 1.0:
            orig_size = text.get_size()
            text = pygame.transform.scale(
                text,
                (int(orig_size[0] * scale), int(orig_size[1] * scale))
            )

        if alpha < 255:
            text.set_alpha(alpha)

        text_rect = text.get_rect(center=(
            self.position[0],
            self.position[1] - 40 * progress
        ))
        surface.blit(text, text_rect)

        for particle in self.particles:

            particle_x = self.position[0] + particle['x'] + particle['speed_x'] * progress * 60
            particle_y = self.position[1] + particle['y'] + particle['speed_y'] * progress * 60

            particle_alpha = int(255 * (1 - progress * particle['fade_speed']))

            particle_size = max(1, int(particle['size'] * (1 - progress * 0.5)))

            if particle_alpha <= 10 or particle_size <= 0:
                continue

            particle_colour = colour + (particle_alpha,)
            particle_surface = pygame.Surface((particle_size*2, particle_size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_colour, (particle_size, particle_size), particle_size)
            surface.blit(particle_surface, (particle_x - particle_size, particle_y - particle_size))
