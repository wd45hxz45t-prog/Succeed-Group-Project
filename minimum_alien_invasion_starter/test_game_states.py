import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import unittest
import pygame

from alien_invasion import AlienInvasion
from bullet import Bullet
from game_state import GameState


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


class GameStateTests(unittest.TestCase):
    def setUp(self):
        self.game = AlienInvasion()

    def tearDown(self):
        pygame.quit()

    def test_game_begins_in_start_state(self):
        self.assertEqual(self.game.game_state, GameState.START)

    def test_enter_starts_the_game(self):
        self.game._check_keydown_events(key(pygame.K_RETURN))
        self.assertEqual(self.game.game_state, GameState.PLAYING)

    def test_space_does_not_fire_before_start(self):
        """[INTERACTION] original firing is blocked until the game starts."""
        self.game._check_keydown_events(key(pygame.K_SPACE))
        self.assertEqual(len(self.game.bullets), 0)
        self.game._check_keydown_events(key(pygame.K_RETURN))
        self.game._check_keydown_events(key(pygame.K_SPACE))
        self.assertEqual(len(self.game.bullets), 1)

    def test_alien_reaching_bottom_ends_the_game(self):
        """[INTERACTION] original _update_aliens now triggers Game Over."""
        self.game._start_new_game()
        alien = self.game.aliens.sprites()[0]
        alien.rect.bottom = self.game.screen.get_rect().bottom
        self.game._update_aliens()
        self.assertEqual(self.game.game_state, GameState.GAME_OVER)

    def test_r_does_nothing_on_start_screen(self):
        self.game._check_keydown_events(key(pygame.K_r))
        self.assertEqual(self.game.game_state, GameState.START)

    def test_enter_does_not_restart_while_playing(self):
        self.game._start_new_game()
        self.game.bullets.add(Bullet(self.game))
        self.game._check_keydown_events(key(pygame.K_RETURN))
        self.assertEqual(len(self.game.bullets), 1)

    def test_restart_resets_speeds_ship_and_fleet(self):
        """[INTERACTION] Restart undoes the speed-ups from the modified fleet-cleared logic."""
        self.game._start_new_game()
        for _ in range(3):
            self.game.settings.increase_speed()
        self.game.ship.rect.x = 0
        self.game.bullets.add(Bullet(self.game))
        self.game.game_state = GameState.GAME_OVER

        self.game._check_keydown_events(key(pygame.K_r))

        s = self.game.settings
        self.assertEqual(self.game.game_state, GameState.PLAYING)
        self.assertEqual((s.ship_speed, s.bullet_speed, s.alien_speed), (4.0, 7.0, 1.2))
        self.assertEqual(len(self.game.bullets), 0)
        self.assertGreater(len(self.game.aliens), 0)
        self.assertEqual(self.game.ship.rect.midbottom,
                         self.game.screen.get_rect().midbottom)

    def test_clearing_the_fleet_speeds_up_the_game(self):
        self.game._start_new_game()
        self.game.aliens.empty()
        self.game._update_bullets()
        self.assertAlmostEqual(self.game.settings.alien_speed, 1.2 * 1.1)
        self.assertGreater(len(self.game.aliens), 0)

    def test_clicking_play_button_starts_the_game(self):
        self.game._check_button_click(self.game.start_button.rect.center)
        self.assertEqual(self.game.game_state, GameState.PLAYING)

    def test_clicking_play_again_button_restarts(self):
        """[INTERACTION] the new button triggers the same reset as the R key."""
        self.game._start_new_game()
        self.game.settings.increase_speed()
        self.game.game_state = GameState.GAME_OVER
        self.game._check_button_click(self.game.restart_button.rect.center)
        self.assertEqual(self.game.game_state, GameState.PLAYING)
        self.assertEqual(self.game.settings.alien_speed, 1.2)


if __name__ == "__main__":
    unittest.main(exit=False)