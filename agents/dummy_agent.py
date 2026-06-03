import asyncio
import random
from typing import Optional, Dict, Any
from agents.base_agent import BaseAgent

class DummyAgent(BaseAgent):
    async def deliberate(self) -> Optional[Dict[str, Any]]:
        if not self.current_state or self.current_state.get("game_over"):
            return None
        
        # Randomly choose between moving left, moving right, shooting, or doing nothing
        choice = random.choice(["move_west", "move_east", "shoot", "idle"])
        
        if choice == "move_west":
            return {"action": "move", "direction": "WEST"}
        elif choice == "move_east":
            return {"action": "move", "direction": "EAST"}
        elif choice == "shoot":
            return {"action": "shoot"}
        
        return None

if __name__ == "__main__":
    agent = DummyAgent()
    asyncio.run(agent.run())
