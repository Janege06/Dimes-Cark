import pygame
import math

from game_state import GameState


class QuestionTimer:
    def __init__(self, font: pygame.font.Font, center: tuple[int, int], radius: int = 40):
        self.font = font
        self.center = center
        self.radius = radius
        self.stroke_width = 8
        self.circ = 2 * math.pi * self.radius

    def start_question_timer(self, game_state: GameState):
        game_state.time_left = GameState.Q_TIME
        game_state.is_answered = False

    def update(self, game_state: GameState, dt: float):
        if game_state.is_answered or game_state.time_left <= 0:
            return

        game_state.time_left -= dt
        if game_state.time_left <= 0:
            game_state.time_left = 0
            self.on_time_up(game_state)

    def on_time_up(self, game_state: GameState):
        game_state.is_answered = True
        game_state.streak = 0
        game_state.lives -= 1

        while len(game_state.round_results) <= game_state.round:
            game_state.round_results.append(None)

        game_state.round_results[game_state.round] = 'bad'

        # In a real app, we'd trigger UI feedback here
        print("Süre doldu!")

    def draw(self, surface: pygame.Surface, game_state: GameState):
        pct = max(0.0, game_state.time_left / GameState.Q_TIME)

        if pct > 0.5:
            color = "#fbbf24"  # Amber
        elif pct > 0.25:
            color = "#f97316"  # Orange
        else:
            color = "#ef4444"  # Red

        # Draw background ring (optional, for better visual)
        pygame.draw.circle(surface, (50, 50, 50), self.center, self.radius, self.stroke_width)

        # Draw the progress arc
        # rect: (left, top, width, height)
        rect = pygame.Rect(
            self.center[0] - self.radius,
            self.center[1] - self.radius,
            self.radius * 2,
            self.radius * 2
        )

        # Pygame draw.arc uses radians. 0 is at 3 o'clock. 
        # We want to start at the top (12 o'clock, which is -pi/2 or 3*pi/2) 
        # and go clockwise.
        start_angle = -math.pi / 2
        # Pygame draws clockwise if start > stop? No, it's always counter-clockwise.
        # To draw clockwise, we need to adjust start and stop.
        # Or just draw from (start - diff) to start.
        stop_angle = start_angle
        actual_start_angle = start_angle - (2 * math.pi * pct)

        if pct > 0:
            pygame.draw.arc(surface, pygame.Color(color), rect, actual_start_angle, stop_angle, self.stroke_width)

        # Draw the numeric time
        time_text = str(math.ceil(max(0, game_state.time_left)))
        text_surf = self.font.render(time_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.center)
        surface.blit(text_surf, text_rect)
