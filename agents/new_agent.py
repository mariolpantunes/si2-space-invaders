__author__ = "Mário Antunes"
__version__ = "1.0.0"
__email__ = "mario.antunes@ua.pt"
__status__ = "Development"

import asyncio
import logging
import random
import argparse
import numpy as np
import json
import os
import pickle
import math

from typing import Optional, Dict, Any, Tuple
from agents.base_agent import BaseAgent


ACTIONS = [
    {"action": "move", "direction": "WEST"},
    {"action": "move", "direction": "EAST"},
    {"action": "shoot"},
    None
    ]


class FinalAgent(BaseAgent):
    def __init__(
        self,
        learning_rate: float = 0.1, 
        discount_factor: float = 0.9, 
        epsilon: float = 1.0, 
        epsilon_decay: float = 0.9995,
        mode: str = "train",
        file: str = None,
        server_uri = "ws://localhost:8765/ws"

    ) -> None:

        super().__init__(server_uri)

        self.q_table: Dict[Tuple[bool, bool, int, int], np.ndarray] = {} # Q_table = (player_x ; has_diving_alien ; aligned ;  target_dx ; target_dy)
        self.lr: float = learning_rate
        self.gamma: float = discount_factor
        self.epsilon: float = epsilon
        self.epsilon_decay: float = epsilon_decay
        self.mode: str = mode
        self.file: str = file
        self.start_flag = False

        self.previous_score: float = 0.0
        self.previous_state: Tuple[bool, bool, int, int] = None
        self.previous_action: int = None

    def get_q_values(self, state: Tuple[bool, bool, int, int]) -> np.ndarray:
        if state not in self.q_table:
            self.q_table[state] = np.zeros(len(ACTIONS), dtype=np.float64)
        return self.q_table[state]
    

    def learn(
        self, 
        state: Tuple[bool, bool, int, int], 
        action: int,
        reward: float, 
        next_state: Tuple[bool, bool, int, int],
        done: bool
    ) -> None:
        
        old_value = self.get_q_values(state)[action]
        if done:
            target = reward
        else:
            next_max = np.max(self.get_q_values(next_state))
            target = reward + self.gamma * next_max
        
        new_value = (1 - self.lr) * old_value + self.lr * target
        self.q_table[state][action] = new_value
        self.epsilon *= self.epsilon_decay

        if len(self.q_table) % 10 == 0:
            print(
                f"\nStates: {len(self.q_table)} | epsilon={self.epsilon:.3f}"
            )
        
        if done:
            self.epsilon = max(0.01, self.epsilon * self.epsilon_decay)



    def make_action(self, state: Tuple[bool, bool, int, int]) -> Optional[Dict[str, Any]]:

        if not self.current_state or self.current_state.get("game_over"):
            return None
        
        valid_action_ids = []
        valid_actions = self.current_state.get("valid_actions",[])

        for i, action in enumerate(ACTIONS):
            if action is None:
                valid_action_ids.append(i)
            elif action in valid_actions:
                valid_action_ids.append(i)

        if random.random() < self.epsilon:
            action_id = random.choice(valid_action_ids)

            if action_id:
                logging.info(f"Deliberated action (fallback): {action_id}")
            return action_id, ACTIONS[action_id]

        else:
            q_values = self.get_q_values(state)

            action_id = max(
                valid_action_ids,
                key=lambda i: q_values[i]
            )

            if action_id:
                logging.info(f"Deliberated action (fallback): {action_id}")
            return action_id, ACTIONS[action_id]



    async def deliberate(self) -> Optional[Dict[str, Any]]:

        has_diving_alien = False
        distance_to_alien = 12.0 # Big Value
        reward: float = 0.0


        if not self.start_flag:
            if self.mode == "play":
                try:
                    self.load(self.file)
                    self.epsilon = 0.0   # never explore
                    print(f"Agent loaded from {self.file}")
                except FileNotFoundError:
                    print(f"Error: Agent file {self.file} not found. Run training first.")
                    return

        self.start_flag = True


        player_x = self.current_state.get('player_x')
        player_y = self.current_state.get('player_y')

        alien_x = player_x # No caso de não existirem aliens
        alien_y = player_y

        for alien in self.current_state.get('aliens'):
            if alien.get('is_diving'):
                has_diving_alien = True
                alien_x = round( alien.get('x'))
                alien_y = round ( alien.get('y'))
                break
                
            else:
                has_diving_alien = False
                if math.sqrt( pow((alien.get('x') - player_x),2)) < distance_to_alien:
                    distance_to_alien = math.sqrt( pow((alien.get('x') - player_x),2))
                    alien_x = round( alien.get('x'))
                    alien_y = round ( alien.get('y'))

                
        target_dx = int(alien_x - player_x)
        target_dx = max(-10, min(10, target_dx))

        target_dy = int(alien_y - player_y)
        target_dy = min(10, max(0, target_dy // 2))
        
        aligned = abs(target_dx) <= 1

        current_state = (has_diving_alien, aligned ,target_dx, target_dy)

        result = self.make_action(current_state)

        if result is None:
            return None

        action_id, action = result



        if self.mode == "train": # --------------------------------------------------

            if self.previous_state is not None:
                self.previous_score = self.current_state.get("score", 0)

                if self.current_state.get("game_over"):
                    reward -= 500

                match self.previous_action:
                    case 0:
                        reward -= 0.01
                    case 1:
                        reward -= 0.01
                    case 2:
                        reward -= 0.01
                    case _:
                        reward -= 0.05

                old_dx = abs(self.previous_state[2])
                new_dx = abs(current_state[2])

                if new_dx < old_dx:
                    reward += 0.1

                elif new_dx > old_dx:
                    reward -= 0.1


                score = self.current_state.get("score", 0)
                reward += score - self.previous_score
                self.previous_score = score

                self.learn(
                    state=self.previous_state,
                    action=self.previous_action,
                    reward=reward,
                    next_state=current_state,
                    done=self.current_state.get("game_over")
                )

            
            self.previous_state = current_state
            self.previous_action = action_id

            if self.current_state.get("game_over"):
                self.previous_state = None
                self.previous_action = None
                self.previous_score = 0
                self.save(self.file)

            #print(
            #f"player_x={player_x}, "
            #f"target_dx={target_dx}, "
            #f"action={action_id}"
            #)
            score = self.current_state.get("score", 0)

            if score >= 15000:
                print("\nTARGET SCORE REACHED!")
                print(f"Final score: {score}")

                self.save(self.file)

                raise SystemExit

        return action



    def save(self, file_path: str) -> None:
        """Serializes the agent state to a file."""
        print("\nSaved q_table")
        with open(file_path, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load(self, file_path: str) -> None:
        """Deserializes the agent state from a file."""
        with open(file_path, 'rb') as f:
            self.q_table = pickle.load(f)



def main() -> None:

    agent = FinalAgent()

    parser = argparse.ArgumentParser(description='StarWars')
    parser.add_argument('-e', '--epochs', type=int, default=10)
    parser.add_argument('-m','--gamemode',choices=["train", "play"], required=True)
    parser.add_argument("-o", "--output", type=str, default="agent.pkl", help="Path to save/load the agent")
    
    args = parser.parse_args()

    agent = FinalAgent(mode=args.gamemode, file=args.output)
        
    asyncio.run(agent.run())



if __name__ == "__main__":
    main()