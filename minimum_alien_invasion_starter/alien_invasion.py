import sys
import pygame
from alien import Alien
from bullet import Bullet
from settings import Settings
from ship import Ship
from game_state import GameState 
from alien import Alien, SecondAlien
from score import Score
from button import Button 


class AlienInvasion:
    """Manage the minimum Alien Invasion starter game."""

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Minimum Alien Invasion Starter")
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        self.score = Score(self)
        self.game_state = GameState.START
        self.title_font = pygame.font.SysFont(None, 80)
        self.text_font = pygame.font.SysFont(None, 36)
        self.start_button = Button(self, "Play", 430)
        self.restart_button = Button(self, "Play again", 430)
        
    def run_game(self):
        while True:
            self._check_events()
            if self.game_state == GameState.PLAYING:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._check_button_click(pygame.mouse.get_pos())

    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            if self.game_state == GameState.PLAYING:
                self._fire_bullet()
        elif event.key == pygame.K_RETURN and self.game_state == GameState.START:
            self.game_state = GameState.PLAYING
        elif event.key in (pygame.K_r, pygame.K_RETURN) and self.game_state == GameState.GAME_OVER:
            self._start_new_game()
        elif event.key == pygame.K_q:
            self._quit_game()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
            
            
            
    def _check_button_click(self, mouse_pos):
        if self.game_state == GameState.START and self.start_button.is_clicked(mouse_pos):
            self.game_state = GameState.PLAYING
        elif self.game_state == GameState.GAME_OVER and self.restart_button.is_clicked(mouse_pos):
            self._start_new_game()
    

    def _fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            self.bullets.add(Bullet(self))
            
            
            
    def _start_new_game(self):
        self.settings.initialize_dynamic_settings()
        self.aliens.empty()
        self.bullets.empty()
        self.ship.moving_right = False
        self.ship.moving_left = False
        self.ship.centre_ship()
        self._create_fleet()
        self.score = Score(self)
        self.game_state = GameState.PLAYING 
        

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        #False to check if it is second alien
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, False) 

        if collisions:
            #get list of damaged aliens
            for damaged_aliens in collisions.values():
                #check every damaged alien
                for alien in damaged_aliens:
                    # Check if it is second alien
                    if isinstance(alien, SecondAlien):
                        # minus one health, if return True, kill the alien
                        if alien.take_damage():
                            alien.kill()
                            self.score.add_points(1)
                    else: #is normal alien
                        alien.kill()
                        self.score.add_points(1)

        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        if any(alien.rect.bottom >= self.screen.get_rect().bottom for alien in self.aliens.sprites()):
            self.game_state = GameState.GAME_OVER

    def _create_fleet(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_width = self.settings.screen_width - 2 * alien_width
        number_aliens_x = available_width // (2 * alien_width)
        for row_number in range(3):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number, alien_width, alien_height)

    def _create_alien(self, alien_number, row_number, alien_width, alien_height):
        if row_number == 0:
            alien = SecondAlien(self)
        else:
            alien = Alien(self)

        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = int(alien.x)
        alien.rect.y = alien_height + 2 * alien_height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        self.score.draw_score()
        if self.game_state == GameState.START:
            self._draw_start_screen()
        elif self.game_state == GameState.GAME_OVER:
            self._draw_game_over_screen()
        pygame.display.flip()
        
        
    def _draw_start_screen(self):
        veil = pygame.Surface(self.screen.get_size())
        veil.set_alpha(190)
        veil.fill(self.settings.bg_color)
        self.screen.blit(veil, (0, 0))
        title = self.title_font.render("ALIEN INVASION", True, (40, 40, 40))
        prompt = self.text_font.render("Click Play or press ENTER", True, (40, 40, 40))
        centre_x = self.settings.screen_width // 2
        self.screen.blit(title, title.get_rect(center=(centre_x, 280)))
        self.screen.blit(prompt, prompt.get_rect(center=(centre_x, 360)))
        self.start_button.draw()      



    def _draw_game_over_screen(self):
        veil = pygame.Surface(self.screen.get_size())
        veil.set_alpha(190)
        veil.fill(self.settings.bg_color)
        self.screen.blit(veil, (0, 0))
        title = self.title_font.render("GAME OVER", True, (40, 40, 40))
        prompt = self.text_font.render("Click Play again or press R / ENTER", True, (40, 40, 40))
        centre_x = self.settings.screen_width // 2
        self.screen.blit(title, title.get_rect(center=(centre_x, 280)))
        self.screen.blit(prompt, prompt.get_rect(center=(centre_x, 360)))
        self.restart_button.draw() 
        
        
    @staticmethod
    def _quit_game():
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    AlienInvasion().run_game()
