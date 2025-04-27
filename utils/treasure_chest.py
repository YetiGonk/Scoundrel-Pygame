""" Treasure chest animation for the Scoundrel game. """
import pygame
import random
import math
from utils.resource_loader import ResourceLoader
from utils.animation import Animation, EasingFunctions
from roguelike_constants import TREASURE_CHEST_RARITY, TREASURE_FILE_PATHS, TREASURE_CHEST_COLOURS

class TreasureChest:
    """Represents the treasure chest with opening animation."""
    
    def __init__(self, position, floor, scale=1):
        # Sprite dimensions
        self.sprite_width = 48
        self.sprite_height = 40
        
        # Game Context
        self.floor = floor
        
        # Position
        self.position = position
        self.scale = scale
        self.scaled_width = int(self.sprite_width * scale)
        self.scaled_height = int(self.sprite_height * scale)
        
        # Animation properties
        self.current_frame = 0
        self.animation_complete = False
        self.frame_duration = 0.1  # seconds per frame
        self.time_since_last_frame = 0
        self.frames = []  # Will hold all chest animation frames
        self.total_frames = 21  # Total frames in animation
        
        # Time tracking for effects
        self.time_passed = random.random() * 5  # Start at random phase
        
        # Particle system
        self.particles = []
        self.treasure_particles = []
        self.spawn_particle_timer = 0
        self.spawn_particle_interval = 0.05  # Spawn particles frequently
        
        # Glow properties
        self.glow_intensity = 1.0
        self.glow_speed = 4.0  # Speed of glow pulsation
        
        # Select a random rarity based on probabilities
        self.rarity = self.select_rarity()
        self.rarity_index = list(TREASURE_CHEST_RARITY.keys()).index(self.rarity) + 1
        self.rarity_color = TREASURE_CHEST_COLOURS[self.rarity]
        
        # Load the treasure sprite for the selected rarity
        self.load_treasure_sprite()
        
        # Extract animation frames
        self.extract_frames()
    
    def select_rarity(self):
        """Select a random rarity based on probabilities."""
        probabilities = list(TREASURE_CHEST_RARITY.values())
        
        # Normalise probabilities if they don't sum to 1
        total = sum(probabilities)
        if total != 1:
            probabilities = [p/total for p in probabilities]
        
        # Random selection
        roll = random.random()
        cumulative = 0
        for chest, prob in TREASURE_CHEST_RARITY.items():
            cumulative += prob
            if roll <= cumulative:
                return chest
        
        # Fallback to most common
        return TREASURE_CHEST_RARITY.keys()[0]
    
    def load_treasure_sprite(self):
        """Load the treasure sprite for the selected rarity."""
        try:
            sprite_path = f"ui/treasure_sprites/{self.rarity}.png"
            self.sprite = ResourceLoader.load_image(sprite_path)
        except Exception as e:
            print(f"Error loading treasure sprite: {e}")
            # Create a default colored square as fallback
            self.sprite = pygame.Surface((self.sprite_width * self.total_frames, self.sprite_height), pygame.SRCALPHA)

            colour = TREASURE_CHEST_COLOURS[self.rarity]            

            # Draw a simple chest for each frame
            for i in range(self.total_frames):
                x = i * self.sprite_width
                
                # Draw chest base (adjusted for animation)
                if i < 10:  # Closed/opening
                    pygame.draw.rect(self.sprite, colour, 
                                    (x + 5, 20, 38, 15))
                else:  # Open
                    pygame.draw.rect(self.sprite, colour, 
                                    (x + 5, 20, 38, 15))
                    # Add treasure
                    pygame.draw.ellipse(self.sprite, (255, 215, 0),
                                      (x + 15, 15, 20, 10))
    
    def extract_frames(self):
        """Extract animation frames from the sprite."""
        self.frames = []
        
        # Check if sprite is loaded
        if not hasattr(self, 'sprite') or self.sprite is None:
            return
        
        # Extract each frame
        for frame in range(self.total_frames):
            # Create a surface for this frame
            frame_surf = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
            
            # Calculate the source position
            src_x = frame * self.sprite_width
            src_y = 0
            
            # Extract the frame
            frame_surf.blit(self.sprite, (0, 0), 
                (src_x, src_y, self.sprite_width, self.sprite_height)
            )
            
            # Scale the frame if needed
            if self.scale != 1:
                frame_surf = pygame.transform.scale(frame_surf, 
                    (self.scaled_width, self.scaled_height)
                )
            
            # Add to frames
            self.frames.append(frame_surf)
    
    def get_particle_color(self):
        """Get a color for particles based on chest rarity."""
        base_color = self.rarity_color
        
        # Add some variation
        if random.random() < 0.3:
            # Sometimes use white/gold for sparkle effect
            r = random.randint(220, 255)
            g = random.randint(220, 255)
            b = random.randint(100, 200)
            return (r, g, b)
        else:
            # Slight variation on the base color
            r = min(255, max(0, base_color[0] + random.randint(-20, 20)))
            g = min(255, max(0, base_color[1] + random.randint(-20, 20)))
            b = min(255, max(0, base_color[2] + random.randint(-20, 20)))
            return (r, g, b)
    
    def spawn_particles(self, chest_rect):
        """Spawn treasure particles from the chest."""
        # Only spawn particles once chest is opening (frame >= 10)
        if self.current_frame < 10:
            return
            
        # Calculate particle spawn position (top of the chest)
        spawn_x = chest_rect.centerx
        spawn_y = chest_rect.top + (chest_rect.height * 31/40)
        
        # Add variation to spawn position
        spawn_x += random.randint(-int(chest_rect.width * 0.3), int(chest_rect.width * 0.3))
        
        # Determine particle count and properties based on rarity and animation stage
        particle_count = 1
        
        # More particles for higher rarities
        if self.rarity_index >= 6:  # Very high rarity
            particle_count = random.randint(4, 6)
        elif self.rarity >= 2:  # Mid-high rarity
            particle_count = random.randint(1, 3)
            
        # Even more particles during the "pop" of opening (frames 14-16)
        if 14 <= self.current_frame <= 16:
            particle_count *= 3
            
        # Create particles
        for _ in range(particle_count):
            # Basic particle properties
            size = random.uniform(1.5, 4.0) * (1 + (self.rarity_index * 0.1))  # Bigger for higher rarities
            
            # Calculate trajectory
            angle = random.uniform(0.7, 2.44)  # Mostly upward (π/4 to 3π/4)
            speed = random.uniform(30, 90) * (1 + (self.rarity_index * 0.05))
            
            # Calculate velocity components
            vx = math.cos(angle) * speed
            vy = -math.sin(angle) * speed  # Negative for upward movement
            
            # Adjust for sprite timing
            if self.current_frame >= 18:  # Chest fully open
                vy *= 0.7  # Slower upward movement, gentler
            elif 14 <= self.current_frame <= 16:  # Initial burst
                vy *= 1.2  # Faster upward movement
                
            # Get color based on rarity
            color = self.get_particle_color()
            
            # Add random brightness variations for sparkle effect
            alpha = random.randint(180, 255)
            
            # Create the particle
            self.particles.append({
                'x': spawn_x,
                'y': spawn_y,
                'vx': vx,
                'vy': vy,
                'size': size,
                'gravity': random.uniform(50, 100),
                'drag': random.uniform(0.92, 0.98),
                'life': 0,
                'max_life': random.uniform(0.6, 1.5),
                'color': (*color, alpha),
                'glow': random.random() < 0.4,  # Some particles have glow effect
                'sparkle': random.random() < 0.3,  # Some particles sparkle
                'sparkle_timer': 0,
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-180, 180)
            })
    
    def update_particles(self, delta_time):
        """Update all particles."""
        updated_particles = []
        
        for particle in self.particles:
            # Update lifetime
            particle['life'] += delta_time
            if particle['life'] >= particle['max_life']:
                continue  # Particle expired
            
            # Update physics
            particle['vy'] += particle['gravity'] * delta_time  # Apply gravity
            particle['x'] += particle['vx'] * delta_time
            particle['y'] += particle['vy'] * delta_time
            
            # Apply drag (air resistance)
            particle['vx'] *= particle['drag']
            particle['vy'] *= particle['drag']
            
            # Update rotation
            particle['rotation'] += particle['rotation_speed'] * delta_time
            
            # Update sparkle effect
            if particle['sparkle']:
                particle['sparkle_timer'] += delta_time
                
            updated_particles.append(particle)
            
        self.particles = updated_particles
    
    def update(self, delta_time):
        """Update the animation and particle effects."""
        # Update time tracking
        self.time_passed += delta_time
        
        # Update glow intensity
        self.glow_intensity = 1.0 + 0.3 * math.sin(self.time_passed * self.glow_speed)
        
        # Only advance animation if not yet complete
        if not self.animation_complete:
            self.time_since_last_frame += delta_time
            
            # Time to advance to next frame
            if self.time_since_last_frame >= self.frame_duration:
                self.time_since_last_frame = 0
                self.current_frame += 1
                
                # Check if animation is complete
                if self.current_frame >= len(self.frames) - 1:
                    self.current_frame = len(self.frames) - 1  # Stay on last frame
                    self.animation_complete = True
        
        # Calculate chest position
        if self.frames and self.current_frame < len(self.frames):
            current_image = self.frames[self.current_frame]
            chest_rect = current_image.get_rect(bottomleft=self.position)
            
            # Spawn particles at appropriate times
            self.spawn_particle_timer += delta_time
            if (self.current_frame >= 13 and 
                self.spawn_particle_timer >= self.spawn_particle_interval):
                self.spawn_particle_timer = 0
                self.spawn_particles(chest_rect)
        
        # Update all particles
        self.update_particles(delta_time)
    
    def draw(self, surface):
        """Draw the treasure chest at its current animation frame."""
        # Skip if no frames loaded
        if not self.frames or self.current_frame >= len(self.frames):
            return
            
        current_image = self.frames[self.current_frame]
        
        # Draw chest at position (position is the center)
        chest_rect = current_image.get_rect(bottomleft=self.position)
        
        # Draw base glow under chest if it's open
        if self.current_frame >= 17:
            self.draw_base_glow(surface, chest_rect)
            
        # Draw some particles behind the chest
        self.draw_particles(surface, chest_rect, behind=True)
        
        # Draw the chest
        surface.blit(current_image, chest_rect)
        
        # Draw remaining particles in front of chest
        self.draw_particles(surface, chest_rect, behind=False)

    
    def draw_particles(self, surface, chest_rect, behind=False):
        """Draw particles either behind or in front of the chest."""
        for particle in self.particles:
            # Calculate alpha based on life
            life_ratio = particle['life'] / particle['max_life']
            alpha = int(255 * (1 - life_ratio))
            
            # Adjust color alpha
            r, g, b, a = particle['color']
            color = (r, g, b, min(a, alpha))
            
            # Increase brightness for sparkle effect
            if particle['sparkle'] and (particle['sparkle_timer'] * 10) % 1 < 0.5:
                # Make brighter during sparkle
                color = (min(255, r + 40), min(255, g + 40), min(255, b + 40), alpha)
            
            # Draw particle
            if particle['glow']:
                # Draw with glow
                glow_size = particle['size'] * 2
                glow_surf = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
                
                # Draw outer glow (more transparent)
                outer_color = (r, g, b, int(alpha * 0.3))
                pygame.draw.circle(glow_surf, outer_color, (int(glow_size), int(glow_size)), int(glow_size))
                
                # Draw inner particle
                pygame.draw.circle(glow_surf, color, (int(glow_size), int(glow_size)), int(particle['size']))
                
                # Draw at particle position
                glow_pos = (int(particle['x'] - glow_size), int(particle['y'] - glow_size))
                surface.blit(glow_surf, glow_pos)
            else:
                # Simple particle
                if random.random() < 0.7:  # Most particles are circles
                    # Create a temporary surface for the particle with alpha
                    particle_surf = pygame.Surface((int(particle['size']*2), int(particle['size']*2)), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surf, color, (int(particle['size']), int(particle['size'])), int(particle['size']))
                    surface.blit(particle_surf, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))
                else:
                    # Some particles are diamond/star shaped
                    size = int(particle['size'] * 1.2)
                    particle_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    
                    # Create a rotated polygon
                    points = []
                    sides = random.choice([4, 5, 6])
                    for i in range(sides):
                        angle = math.radians(particle['rotation'] + (i * 360 / sides))
                        x = size + int(math.cos(angle) * size)
                        y = size + int(math.sin(angle) * size)
                        points.append((x, y))
                    
                    pygame.draw.polygon(particle_surf, color, points)
                    surface.blit(particle_surf, (int(particle['x'] - size), int(particle['y'] - size)))
    
    def draw_base_glow(self, surface, chest_rect):
        """Draw the base glow under the chest."""
        # Calculate glow position and size
        glow_width = chest_rect.width*0.7
        glow_height = chest_rect.height*0.4
        
        # Create glow surface
        glow_surf = pygame.Surface((int(glow_width), int(glow_height)), pygame.SRCALPHA)
        
        # Get color based on rarity
        rarity_colors = [
            (255, 255, 0),    # Common - yellow/gold
            (0, 255, 0),      # Uncommon - green
            (0, 150, 255),    # Blue
            (255, 0, 255),    # Purple/magenta
            (255, 165, 0),    # Orange
            (255, 0, 0),      # Red
            (255, 255, 255),  # Silver/white
            (180, 0, 255),    # Indigo/purple
            (0, 255, 255),    # Cyan
            (255, 215, 0)     # Legendary - gold
        ]
        glow_color = self.rarity_color
        
        # Animate glow based on time
        alpha = int(50 + 30 * math.sin(self.time_passed * 3.0))
        
        # Draw elliptical glow
        pygame.draw.ellipse(glow_surf, (*glow_color, alpha), 
            (0, 0, int(glow_width), int(glow_height))
        )
        
        # Position and draw
        glow_pos = (chest_rect.centerx-glow_width//2, chest_rect.centery-glow_height//2+100)
        surface.blit(glow_surf, glow_pos, special_flags=pygame.BLEND_ALPHA_SDL2)
