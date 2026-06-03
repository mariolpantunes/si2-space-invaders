import unittest
from server.logic import SpaceInvaders, Laser

class TestSpaceInvadersLogic(unittest.TestCase):
    def setUp(self):
        self.game = SpaceInvaders(width=11, height=11)

    def test_initial_state(self):
        self.assertEqual(self.game.player_x, 5.0)
        self.assertEqual(self.game.player_y, 0.0)
        self.assertEqual(self.game.lives, 3)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.checkpoint_score, 0)
        self.assertFalse(self.game.game_over)
        self.assertEqual(len(self.game.aliens), 10)

    def test_move_bounds(self):
        # Move WEST repeatedly
        for _ in range(10):
            self.game.move_player("WEST")
        self.assertEqual(self.game.player_x, 0.0)

        # Move EAST repeatedly
        for _ in range(20):
            self.game.move_player("EAST")
        self.assertEqual(self.game.player_x, 10.0)

    def test_shoot_cooldown(self):
        self.game.shoot_laser()
        self.assertEqual(len(self.game.lasers), 1)
        
        # Try shooting immediately again (should fail due to cooldown)
        self.game.shoot_laser()
        self.assertEqual(len(self.game.lasers), 1)

        # Fast forward time past cooldown
        self.game.update(0.4)
        self.game.shoot_laser()
        self.assertEqual(len(self.game.lasers), 2)

    def test_laser_alien_collision(self):
        self.game.lasers = [Laser(x=5.0, y=7.5)]
        
        # Position alien exactly at (5.0, 8.3) and make it static
        self.game.aliens[2].base_x = 5.0
        self.game.aliens[2].base_y = 8.3
        self.game.aliens[2].amp_x = 0.0
        self.game.aliens[2].amp_y = 0.0
        self.game.aliens[2].active = True
        
        self.game.update(0.1) # Updates positions, laser flies up to (5.0, 8.3)
        
        self.assertFalse(self.game.aliens[2].active)
        self.assertEqual(self.game.score, 10)
        self.assertEqual(len(self.game.lasers), 0)

    def test_diving_hit_death(self):
        # Advance score and checkpoint
        self.game.score = 50
        self.game.checkpoint_score = 50
        
        # Trigger an alien dive and position it close to player center (5.0, 0.0)
        alien = self.game.aliens[0]
        alien.active = True
        alien.start_dive(self.game.player_x, speed=5.0)
        alien.x = 5.0
        alien.y = 0.5
        
        # Trigger update (should register collision and death)
        self.game.update(0.1)
        
        self.assertEqual(self.game.lives, 2)
        self.assertEqual(self.game.score, 50) # Reset to checkpoint score
        self.assertEqual(self.game.player_x, 5.0) # Reset player center
        self.assertFalse(alien.is_diving)

    def test_diving_miss_penalty(self):
        # Increase score, checkpoint stays 0
        self.game.score = 30
        self.game.checkpoint_score = 0
        
        alien = self.game.aliens[0]
        alien.active = True
        alien.start_dive(self.game.player_x, speed=5.0)
        alien.x = 2.0
        alien.y = 0.05
        
        # Update alien y position so it drops <= 0.0
        alien.update(0.05, 0.0) # Will move y down since dive speed is 5.0 and dy is negative
        
        self.game.update(0.01) # Triggers miss penalty check
        
        self.assertEqual(self.game.score, 20) # Deduced by 10 points
        self.assertFalse(alien.is_diving) # Teleports/resets dive

    def test_wave_cleared(self):
        # Setup all aliens as inactive
        for alien in self.game.aliens:
            alien.active = False
            
        # Update frame (triggers wave cleared checks)
        self.game.update(0.1)
        
        self.assertEqual(self.game.score, 100) # Gets +100 bonus
        self.assertEqual(self.game.checkpoint_score, 100) # Checkpoint updated
        
        # Squad respawned
        self.assertEqual(len([a for a in self.game.aliens if a.active]), 10)

if __name__ == "__main__":
    unittest.main()
