import pygame
import numpy as np
import random
import math

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

class TVFilter:
    """Old CRT TV filter"""
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # effect toggles
        self.scanlines_enabled = True
        self.grain_enabled = True
        self.chromatic_aberration_enabled = True
        self.vignette_enabled = True
        self.screen_curve_enabled = True
        self.flicker_enabled = True
        
        # effect parameters
        self.scanline_intensity = 0.3
        self.grain_intensity = 0.16
        self.grain_freq = 4
        self.chromatic_aberration_amount = 4
        self.vignette_intensity = 0.1
        self.curve_amount = 0.06  # 0.1-0.3 recommended
        self.flicker_intensity = 0.08
        
        # create effect surfaces
        self._create_scanlines()
        self._create_vignette()
        
        # Pre-compute barrel distortion mapping
        self._create_barrel_distortion_map()
        
        # flicker state
        self.flicker_offset = 0
        self.time = 0
        
        # Performance optimizations
        self.frame_counter = 0
        self.grain_cache = []
        self._regenerate_grain_cache()
    
    def _create_scanlines(self):
        """Create scanline overlay"""
        self.scanline_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        for y in range(0, self.height, 2):
            pygame.draw.line(self.scanline_surface, (0, 0, 0, int(255 * self.scanline_intensity)), (0, y), (self.width, y))
    
    def _create_vignette(self):
        """Create vignette overlay with numpy"""
        self.vignette_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        center_x = self.width // 2
        center_y = self.height // 2
        max_distance = math.sqrt(center_x**2 + center_y**2)
        
        # Use numpy for fast computation
        y_coords, x_coords = np.ogrid[:self.height, :self.width]
        
        distance = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
        darkness = np.clip((distance / max_distance) * self.vignette_intensity, 0, 1)
        
        # Create alpha channel
        alpha_array = (darkness * 255).astype(np.uint8)
        
        # Apply to surface using surfarray
        alpha_surf = pygame.surfarray.pixels_alpha(self.vignette_surface)
        alpha_surf[:] = alpha_array.T
        del alpha_surf
    
    def _create_barrel_distortion_map(self):
        """Pre-compute barrel distortion coordinate mapping"""
        # Create coordinate grids
        y_coords, x_coords = np.meshgrid(
            np.arange(self.height, dtype=np.float32),
            np.arange(self.width, dtype=np.float32),
            indexing='ij'
        )
        
        # Normalize coordinates to -1 to 1
        center_x = self.width / 2
        center_y = self.height / 2
        
        x_norm = (x_coords - center_x) / center_x
        y_norm = (y_coords - center_y) / center_y
        
        # Calculate distance from center
        r = np.sqrt(x_norm**2 + y_norm**2)
        
        # Apply barrel distortion formula: r' = r * (1 + k * r^2)
        k = self.curve_amount
        r_distorted = r * (1 + k * r**2)
        
        # Prevent division by zero
        r_safe = np.where(r < 0.001, 0.001, r)
        
        # Calculate distorted coordinates
        scale = r_distorted / r_safe
        x_distorted = x_norm * scale
        y_distorted = y_norm * scale
        
        # Convert back to pixel coordinates
        self.map_x = (x_distorted * center_x + center_x).astype(np.float32)
        self.map_y = (y_distorted * center_y + center_y).astype(np.float32)
        
        # Clamp to valid ranges
        self.map_x = np.clip(self.map_x, 0, self.width - 1)
        self.map_y = np.clip(self.map_y, 0, self.height - 1)
    
    def _apply_chromatic_aberration(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply RGB channel separation effect"""
        if not self.chromatic_aberration_enabled:
            return surface
        
        pixels = pygame.surfarray.array3d(surface)
        
        red_shifted = np.roll(pixels[:, :, 0], self.chromatic_aberration_amount, axis=0)
        blue_shifted = np.roll(pixels[:, :, 2], -self.chromatic_aberration_amount, axis=0)
        
        pixels[:, :, 0] = red_shifted
        pixels[:, :, 2] = blue_shifted
        
        result = surface.copy()
        pygame.surfarray.blit_array(result, pixels)
        
        return result
    
    def _regenerate_grain_cache(self):
        """Pre-generate grain positions for reuse"""
        num_grains = int(self.width * self.height * self.grain_intensity * 0.01)
        self.grain_cache = [
            (random.randint(0, self.width - 1), 
             random.randint(0, self.height - 1),
             random.randint(0, 100))
            for _ in range(num_grains)
        ]
    
    def _apply_grain(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply film grain effect"""
        if not self.grain_enabled:
            return surface
        
        self.frame_counter += 1
        if self.frame_counter % self.grain_freq == 0:
            self._regenerate_grain_cache()
        
        try:
            pixels = pygame.surfarray.pixels3d(surface)
            
            for x, y, brightness in self.grain_cache:
                if x < self.width and y < self.height:
                    pixels[x, y] = np.clip(pixels[x, y] + brightness, 0, 255)
            
            del pixels
        except:
            grain_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            for x, y, brightness in self.grain_cache:
                grain_surface.set_at((x, y), (brightness, brightness, brightness, brightness))
            surface.blit(grain_surface, (0, 0), special_flags=pygame.BLEND_ADD)
        
        return surface
    
    def _apply_barrel_distortion(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply barrel distortion - uses OpenCV if available for 10x+ speed boost"""
        if not self.screen_curve_enabled:
            return surface
        
        if HAS_CV2:
            # Fast path using OpenCV's remap function
            # Convert pygame surface to numpy array
            src_array = pygame.surfarray.array3d(surface)
            # OpenCV expects (height, width, channels) but pygame gives (width, height, channels)
            src_array = np.transpose(src_array, (1, 0, 2))
            
            # Apply remapping
            dst_array = cv2.remap(
                src_array,
                self.map_x,
                self.map_y,
                cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REPLICATE
            )
            
            # Convert back to pygame format
            dst_array = np.transpose(dst_array, (1, 0, 2))
            
            result = pygame.Surface((self.width, self.height))
            pygame.surfarray.blit_array(result, dst_array)
            
            return result
        else:
            # Fallback: numpy-only version (slower but works)
            src_pixels = pygame.surfarray.array3d(surface)
            dst_pixels = np.zeros_like(src_pixels)
            
            # Vectorized nearest-neighbor sampling
            map_x_int = self.map_x.astype(np.int32)
            map_y_int = self.map_y.astype(np.int32)
            
            # This is still slow but better than nested loops
            # Using advanced indexing
            for c in range(3):  # For each color channel
                dst_pixels[:, :, c] = src_pixels[map_x_int.T, map_y_int.T, c]
            
            result = pygame.Surface((self.width, self.height))
            pygame.surfarray.blit_array(result, dst_pixels)
            
            return result
    
    def _apply_flicker(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply screen flicker effect"""
        if not self.flicker_enabled:
            return surface
        
        self.time += 0.1
        flicker = math.sin(self.time * 3) * self.flicker_intensity
        flicker += math.sin(self.time * 7) * self.flicker_intensity * 0.5
        
        if random.random() < 0.01:
            flicker += random.uniform(-0.1, 0.1)
        
        brightness = max(0.5, min(1.5, 1.0 + flicker))
        rgb_value = max(0, min(255, int(255 * brightness)))
        
        flicker_surface = pygame.Surface(surface.get_size())
        flicker_surface.fill((rgb_value, rgb_value, rgb_value))
        
        result = surface.copy()
        result.blit(flicker_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        
        return result
    
    def _apply_scanline_wobble(self):
        """Add subtle horizontal displacement to scanlines (VHS effect)"""
        if random.random() < 0.05:
            return random.randint(-3, 3)
        return 0
    
    def apply_filter(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply all TV filter effects to the surface"""
        filtered = surface.copy()
        
        if filtered.get_bitsize() < 24:
            filtered = filtered.convert()
        
        # Apply effects in order
        filtered = self._apply_flicker(filtered)
        filtered = self._apply_chromatic_aberration(filtered)
        filtered = self._apply_grain(filtered)
        
        # Apply barrel distortion (the actual curved screen!)
        filtered = self._apply_barrel_distortion(filtered)
        
        # Optional scanlines
        if self.scanlines_enabled:
            wobble = self._apply_scanline_wobble()
            if wobble != 0:
                wobble_surface = self.scanline_surface.copy()
                filtered.blit(wobble_surface, (wobble, 0))
            else:
                filtered.blit(self.scanline_surface, (0, 0))
        
        # Finally optional vignette
        if self.vignette_enabled:
            filtered.blit(self.vignette_surface, (0, 0))
        
        return filtered
    
    def add_static_burst(self, surface: pygame.Surface, intensity: float = 0.3):
        """Add a burst of static interference"""
        num_lines = int(self.height * intensity)
        
        try:
            pixels = pygame.surfarray.pixels3d(surface)
            
            for _ in range(num_lines):
                y = random.randint(0, self.height - 1)
                for x in range(self.width):
                    if random.random() < 0.7:
                        brightness = random.randint(150, 255)
                        pixels[x, y] = [brightness, brightness, brightness]
            
            del pixels
        except:
            static_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            for _ in range(num_lines):
                y = random.randint(0, self.height - 1)
                for x in range(self.width):
                    if random.random() < 0.7:
                        brightness = random.randint(150, 255)
                        static_surface.set_at((x, y), (brightness, brightness, brightness, 200))
            surface.blit(static_surface, (0, 0))
    
    def add_tracking_lines(self, surface: pygame.Surface, num_lines: int = 3):
        """Add horizontal tracking interference lines (VHS effect)"""
        try:
            pixels = pygame.surfarray.pixels3d(surface)
            
            for _ in range(num_lines):
                y = random.randint(0, self.height - 1)
                height = random.randint(2, 8)
                
                for dy in range(height):
                    if y + dy < self.height:
                        for x in range(self.width):
                            if random.random() < 0.5:
                                brightness = random.randint(50, 150)
                                pixels[x, y + dy] = np.clip(pixels[x, y + dy] + brightness, 0, 255)
            
            del pixels
        except:
            for _ in range(num_lines):
                y = random.randint(0, self.height - 1)
                height = random.randint(2, 8)
                
                for dy in range(height):
                    if y + dy < self.height:
                        for x in range(self.width):
                            if random.random() < 0.5:
                                brightness = random.randint(50, 150)
                                colour = surface.get_at((x, y + dy))
                                new_colour = (
                                    min(255, colour[0] + brightness),
                                    min(255, colour[1] + brightness),
                                    min(255, colour[2] + brightness)
                                )
                                surface.set_at((x, y + dy), new_colour)
