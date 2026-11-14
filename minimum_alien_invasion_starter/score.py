import pygame
class Score:

    def __init__(self, ai_game):
        self.screen = ai_game.screen
        self.points_per_alien = ai_game.settings.alien_points
        self.score = 0 
        self.font = pygame.font.SysFont(None, 40)

    def add_points(self, aliens_hit):
        self.score = self.score + self.points_per_alien * aliens_hit

    def reset_score(self):
        self.score = 0 

    def draw_score(self):
        text= "Score: " + str(self.score)
        text_picture = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(text_picture, (20, 20))