import pygame


class Button:
    """A clickable button."""

    def __init__(self, game, text, center_y):
        self.screen = game.screen
        self.rect = pygame.Rect(0, 0, 220, 60)
        self.rect.center = (game.settings.screen_width // 2, center_y)
        self.color = (30, 90, 180)
        self.hover_color = (60, 120, 210)
        font = pygame.font.SysFont(None, 40)
        self.text_image = font.render(text, True, (255, 255, 255))
        self.text_rect = self.text_image.get_rect(center=self.rect.center)

    def draw(self):
        hovering = self.rect.collidepoint(pygame.mouse.get_pos())
        color = self.hover_color if hovering else self.color
        pygame.draw.rect(self.screen, color, self.rect, border_radius=8)
        self.screen.blit(self.text_image, self.text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)