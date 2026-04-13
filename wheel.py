import math
import random

import pygame

from question_manager import Category


class Wheel:
    CX, CY = 300, 300
    R = 280
    IR = 60
    
    CAT_PROPS = {
        Category.SURDURULEBILIRLIK: {
            "color": "#ff6b1a",
            "light": "rgba(255,107,26,.15)",
            "icon": "🌿",
            "name": "Sürdürüle-bilirlik"
        },
        Category.URUNLER: {
            "color": "#22c55e",
            "light": "rgba(34,197,94,.15)",
            "icon": "🍊",
            "name": "Ürünler"
        },
        Category.GENEL_KULTUR: {
            "color": "#3b82f6",
            "light": "rgba(59,130,246,.15)",
            "icon": "🌍",
            "name": "Genel Kültür"
        },
        Category.BONUS: {
            "color": "#f59e0b",
            "light": "rgba(245,158,11,.15)",
            "icon": "★",
            "name": "BONUS x2"
        }
    }

    wheel_segments: list[Category] = [
        Category.SURDURULEBILIRLIK, # s
        Category.URUNLER,           # u
        Category.GENEL_KULTUR,      # g
        Category.BONUS,             # b
        Category.URUNLER,           # u
        Category.SURDURULEBILIRLIK, # s
        Category.GENEL_KULTUR,      # g
        Category.SURDURULEBILIRLIK  # s
    ]

    def __init__(self, emoji_font=None):
        self.angle = 0
        self.is_spinning = False
        self.start_angle = 0
        self.target_angle = 0
        self.start_time = 0
        self.duration = 0
        self.on_landed_callback = None
        self.emoji_font = emoji_font

    def get_random_category(self) -> Category:
        return random.choice(self.wheel_segments)

    def draw(self, surface: pygame.Surface):
        n_seg = len(self.wheel_segments)
        arc = (2 * math.pi) / n_seg

        for i, cat_enum in enumerate(self.wheel_segments):
            props = self.CAT_PROPS[cat_enum]
            start = self.angle + i * arc
            end = start + arc

            # Segment fill
            points = [(self.CX, self.CY)]
            num_points = 30
            for step in range(num_points + 1):
                theta = start + (step / num_points) * arc
                points.append((
                    self.CX + self.R * math.cos(theta),
                    self.CY + self.R * math.sin(theta)
                ))
            
            pygame.draw.polygon(surface, pygame.Color(props["color"]), points)

            # Darker alternate
            if i % 2 == 1:
                overlay = pygame.Surface((600, 600), pygame.SRCALPHA)
                pygame.draw.polygon(overlay, (0, 0, 0, 46), points) # 0.18 * 255 approx 46
                surface.blit(overlay, (0, 0))

            # Border
            pygame.draw.polygon(surface, (0, 0, 0, 102), points, 3) # 0.4 * 255 approx 102

            # Icon & Label
            mid_angle = start + arc / 2
            
            # Icon at outer part
            icon_r = self.R * 0.72
            ix = self.CX + icon_r * math.cos(mid_angle)
            iy = self.CY + icon_r * math.sin(mid_angle)
            self._draw_rotated_text(surface, props["icon"], ix, iy, mid_angle, is_icon=True)

            # Label at inner part
            label_r = self.R * 0.38
            lx = self.CX + label_r * math.cos(mid_angle)
            ly = self.CY + label_r * math.sin(mid_angle)
            self._draw_rotated_text(surface, props["name"], lx, ly, mid_angle, is_icon=False)

        # Center hub
        pygame.draw.circle(surface, (217, 119, 6), (self.CX, self.CY), self.IR)
        pygame.draw.circle(surface, (0, 0, 0, 76), (self.CX, self.CY), self.IR, 4)

        # DiMES text on hub
        font = pygame.font.SysFont("Arial", 28, bold=True)
        text_surf = font.render("DiMES", True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.CX, self.CY))
        surface.blit(text_surf, text_rect)

    def _draw_rotated_text(self, surface, text, x, y, angle, is_icon=False):
        font_size = 45 if is_icon else 20
        
        if is_icon and self.emoji_font:
            font = self.emoji_font
            # Ensure it's scaled for the wheel if it's the 32px font from main
            # or recreate it with larger size for icons
            if font.get_height() < font_size:
                try:
                    # If we can get the path from main's font loading, we could recreate it
                    # But for now, we'll just scale the rendered surface later
                    pass
                except:
                    pass
        elif is_icon:
            # Emoji fonts might not be available in WASM, using fallback
            font = pygame.font.SysFont("Apple Color Emoji, Segoe UI Emoji, Noto Color Emoji, Android Emoji, EmojiSymbols, symbola, dejavuserif", font_size, bold=True)
        else:
            font = pygame.font.SysFont("dejavusans", font_size, bold=True)
        
        if not is_icon:
            # Split by space and also by hyphen for long words
            words = []
            for part in text.split(' '):
                if '-' in part:
                    words.extend(part.split('-'))
                else:
                    words.append(part)
            
            line_height = 18
            for wi, w in enumerate(words):
                txt_s = font.render(w, True, (255, 255, 255))
                # Rotate
                rot_s = pygame.transform.rotate(txt_s, -math.degrees(angle + math.pi/2))
                
                rad = angle + math.pi/2
                ox = 0
                oy = wi * line_height - (len(words)-1) * line_height / 2
                
                # Rotate (ox, oy) by rad
                rot_ox = ox * math.cos(rad) - oy * math.sin(rad)
                rot_oy = ox * math.sin(rad) + oy * math.cos(rad)
                
                rect = rot_s.get_rect(center=(x + rot_ox, y + rot_oy))
                surface.blit(rot_s, rect)
        else:
            txt_s = font.render(text, True, (255, 255, 255))
            
            # Scale if necessary (if font was smaller than font_size)
            if is_icon and txt_s.get_height() < font_size * 0.8:
                ratio = font_size / txt_s.get_height()
                txt_s = pygame.transform.smoothscale(txt_s, (int(txt_s.get_width() * ratio), font_size))

            rot_s = pygame.transform.rotate(txt_s, -math.degrees(angle + math.pi/2))
            
            # Center icons properly
            rect = rot_s.get_rect(center=(x, y))
            surface.blit(rot_s, rect)

    def spin(self, on_landed_callback):
        if self.is_spinning:
            return
        self.is_spinning = True
        self.on_landed_callback = on_landed_callback
        
        n_seg = len(self.wheel_segments)
        target_seg = random.randint(0, n_seg - 1)
        full_spins = random.randint(3, 5)
        seg_angle = (2 * math.pi) / n_seg
        
        # We calculate the target absolute angle for the segment to land at -PI/2 (top)
        # We want: (wheel_angle + (target_seg + 0.5) * seg_angle) % 2PI == -PI/2
        # So: wheel_angle % 2PI == (-PI/2 - (target_seg + 0.5) * seg_angle) % 2PI
        
        target_base_angle = (-math.pi / 2 - (target_seg + 0.5) * seg_angle)
        
        # Calculate how much to rotate from current angle to get to the base angle
        current_angle_mod = self.angle % (2 * math.pi)
        target_base_angle_mod = target_base_angle % (2 * math.pi)
        
        diff = (target_base_angle_mod - current_angle_mod)
        if diff <= 0:
            diff += 2 * math.pi
        
        self.target_angle = self.angle + diff + full_spins * 2 * math.pi
        self.start_angle = self.angle
        self.start_time = pygame.time.get_ticks()
        self.duration = random.randint(3500, 5000)

    def update(self):
        if not self.is_spinning:
            return

        now = pygame.time.get_ticks()
        t = min((now - self.start_time) / self.duration, 1)
        
        # Ease out quartic: 1 - (1-t)^4
        ease_t = 1 - pow(1 - t, 4)
        self.angle = self.start_angle + (self.target_angle - self.start_angle) * ease_t

        if t >= 1:
            self.is_spinning = False
            self._on_finished()

    def _on_finished(self):
        n_seg = len(self.wheel_segments)
        seg_angle = (2 * math.pi) / n_seg
        
        # JS: const norm = (((-wheelAngle - Math.PI/2) % (2*Math.PI)) + 2*Math.PI) % (2*Math.PI);
        norm = (((-self.angle - math.pi / 2) % (2 * math.pi)) + 2 * math.pi) % (2 * math.pi)
        landed_idx = int(norm / seg_angle) % n_seg
        cat = self.wheel_segments[landed_idx]
        
        if self.on_landed_callback:
            self.on_landed_callback(cat)
