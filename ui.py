import pygame
import re


def render_with_emojis(surface: pygame.Surface, text: str, font: pygame.font.Font, emoji_font: pygame.font.Font,
                       color: pygame.Color, rect: pygame.Rect, align="center"):
    """Renders text mixed with emojis."""
    emoji_pattern = re.compile(r'([\U00010000-\U0010ffff\u2600-\u27ff])')
    parts = emoji_pattern.split(text)
    
    surfaces = []
    total_width = 0
    max_height = 0
    
    for part in parts:
        if not part:
            continue
        if emoji_pattern.match(part):
            s = emoji_font.render(part, True, (255, 255, 255))
            target_h = font.get_height()
            ratio = target_h / s.get_height()
            s = pygame.transform.smoothscale(s, (int(s.get_width() * ratio), target_h))
        else:
            s = font.render(part, True, color)
        
        surfaces.append(s)
        total_width += s.get_width()
        max_height = max(max_height, s.get_height())
        
    if align == "center":
        curr_x = rect.centerx - total_width // 2
        curr_y = rect.centery - max_height // 2
    else: # left
        curr_x = rect.x
        curr_y = rect.centery - max_height // 2
        
    for s in surfaces:
        surface.blit(s, (curr_x, curr_y))
        curr_x += s.get_width()


def draw_text_wrapped(surface: pygame.Surface, text: str, font: pygame.font.Font, color: pygame.Color, 
                      rect: pygame.Rect, align="left", emoji_font: pygame.font.Font = None):
    """Draws wrapped text, with optional emoji support."""
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        # Calculate width of test_line
        if emoji_font:
            # For emoji support, we need a way to measure without rendering
            # Let's use a simplified measurement for now
            w = 0
            emoji_pattern = re.compile(r'([\U00010000-\U0010ffff\u2600-\u27ff])')
            parts = emoji_pattern.split(test_line)
            for part in parts:
                if emoji_pattern.match(part):
                    s = emoji_font.render(part, True, (255, 255, 255))
                    target_h = font.get_height()
                    ratio = target_h / s.get_height()
                    w += int(s.get_width() * ratio)
                else:
                    w += font.size(part)[0]
        else:
            w = font.size(test_line)[0]
            
        if w <= rect.width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    line_height = font.get_linesize()
    total_height = len(lines) * line_height
    
    # Starting Y position
    if align == "center":
        curr_y = rect.centery - total_height // 2
    else:
        curr_y = rect.y
        
    for line in lines:
        line_rect = pygame.Rect(rect.x, curr_y, rect.width, line_height)
        if emoji_font:
            render_with_emojis(surface, line, font, emoji_font, color, line_rect, align)
        else:
            surf = font.render(line, True, color)
            if align == "center":
                r = surf.get_rect(centerx=rect.centerx, y=curr_y)
            else:
                r = surf.get_rect(x=rect.x, y=curr_y)
            surface.blit(surf, r)
        curr_y += line_height


class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font, bg_colors: tuple[pygame.Color, pygame.Color],
                 shadow_color: pygame.Color, text_color: pygame.Color, border_radius: int = 50, emoji_font: pygame.font.Font = None):
        self.rect: pygame.Rect = rect
        self.text: str = text
        self.font: pygame.font.Font = font
        self.emoji_font: pygame.font.Font = emoji_font
        self.bg_colors: tuple[pygame.Color, pygame.Color] = bg_colors
        self.shadow_color: pygame.Color = shadow_color
        self.text_color: pygame.Color = text_color
        self.border_radius: int = border_radius
        self.hovered: bool = False
        self.pressed: bool = False

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            if was_pressed and self.rect.collidepoint(event.pos):
                return True

        return False

    def draw(self, surface: pygame.Surface):
        # Apply transforms based on state
        draw_rect = self.rect.copy()
        shadow_offset = 6
        
        if self.pressed:
            draw_rect.y += 3
            shadow_offset = 2
        elif self.hovered:
            draw_rect.y -= 2
            shadow_offset = 8

        # Draw Shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += shadow_offset
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, self.shadow_color, shadow_surf.get_rect(), border_radius=self.border_radius)
        surface.blit(shadow_surf, shadow_rect)

        # Draw Gradient Button (simplified with two rects for now, or just solid color if too complex)
        # For simplicity, we'll use a slightly lighter color if hovered
        color = self.bg_colors[0]
        if self.hovered and not self.pressed:
            # Brighten color
            color = pygame.Color(min(color.r + 20, 255), min(color.g + 20, 255), min(color.b + 20, 255))
        
        pygame.draw.rect(surface, color, draw_rect, border_radius=self.border_radius)

        if self.emoji_font:
            draw_text_wrapped(surface, self.text, self.font, self.text_color, draw_rect, align="center", emoji_font=self.emoji_font)
        else:
            draw_text_wrapped(surface, self.text, self.font, self.text_color, draw_rect, align="center")


class Panel:
    def __init__(self, rect: pygame.Rect, bg_colors: tuple[pygame.Color, pygame.Color], border_color: pygame.Color, border_width: int = 2, border_radius: int = 24):
        self.rect = rect
        self.bg_colors = bg_colors
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius

    def draw(self, surface: pygame.Surface):
        # Shadow
        shadow_rect = self.rect.move(0, 10)
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 150), shadow_surf.get_rect(), border_radius=self.border_radius)
        surface.blit(shadow_surf, shadow_rect)
        
        # Main Panel
        pygame.draw.rect(surface, self.bg_colors[0], self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, self.border_color, self.rect, width=self.border_width, border_radius=self.border_radius)


class StatBox:
    def __init__(self, rect: pygame.Rect, label: str, font_val: pygame.font.Font, font_lbl: pygame.font.Font):
        self.rect = rect
        self.label = label
        self.value = "0"
        self.font_val = font_val
        self.font_lbl = font_lbl
        self.bg_color = pygame.Color("#122236")
        self.border_color = pygame.Color("#1e3a55")
        self.gold = pygame.Color("#fbbf24")
        self.muted = pygame.Color(226, 232, 240, 115) # 0.45 * 255

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, self.border_color, self.rect, width=1, border_radius=10)
        
        val_surf = self.font_val.render(str(self.value), True, self.gold)
        val_rect = val_surf.get_rect(center=(self.rect.centerx, self.rect.top + 15))
        surface.blit(val_surf, val_rect)
        
        lbl_surf = self.font_lbl.render(self.label, True, self.muted)
        lbl_rect = lbl_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - 10))
        surface.blit(lbl_surf, lbl_rect)


class CategoryTag:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font, color: pygame.Color, emoji_font: pygame.font.Font = None):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color
        self.emoji_font = emoji_font
        self.bg_color = pygame.Color(30, 58, 85) # Dark blue/grey background

    def draw(self, surface: pygame.Surface):
        # Draw Bordered Pill
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=20)
        pygame.draw.rect(surface, self.color, self.rect, width=2, border_radius=20)
        
        # Draw Text with Emojis
        if self.emoji_font:
            draw_text_wrapped(surface, self.text, self.font, self.color, self.rect, align="center", emoji_font=self.emoji_font)
        else:
            surf = self.font.render(self.text, True, self.color)
            r = surf.get_rect(center=self.rect.center)
            surface.blit(surf, r)


class ProgressBar:
    def __init__(self, x, y, total_rounds):
        self.x = x
        self.y = y
        self.total_rounds = total_rounds
        self.results = [] # 'ok', 'bad', or None
        self.current_round = 0

    def draw(self, surface: pygame.Surface):
        dot_radius = 5
        gap = 5
        for i in range(self.total_rounds):
            color = pygame.Color("#122236") # panel
            border_color = pygame.Color("#1e3a55") # border
            
            if i < len(self.results):
                if self.results[i] == 'ok':
                    color = pygame.Color("#22c55e")
                    border_color = color
                elif self.results[i] == 'bad':
                    color = pygame.Color("#ef4444")
                    border_color = color
            elif i == self.current_round:
                color = pygame.Color("#fbbf24")
                border_color = color
                
            pos = (self.x + i * (dot_radius * 2 + gap) + dot_radius, self.y + dot_radius)
            pygame.draw.circle(surface, color, pos, dot_radius)
            pygame.draw.circle(surface, border_color, pos, dot_radius, width=2)


class Ui:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 36)
        self.buttons: list[Button] = []

    def add_button(self, button: Button):
        self.buttons.append(button)

    def handle_event(self, event: pygame.event.Event):
        for button in self.buttons:
            if button.handle_event(event):
                return button.text
        return None

    def draw(self, surface: pygame.Surface):
        for button in self.buttons:
            button.draw(surface)
