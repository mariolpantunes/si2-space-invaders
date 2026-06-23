# Agent - SI2 Space Invaders

**Authors:** Guilherme Ribeiro (114279) · Francisco Fernandes (115129)  
**Course:** Sistemas Inteligentes II — Mestrado em Robótica e Sistemas Inteligentes

---

## Overview

Tabular Q-Learning agent for the SI2-Space-Invaders environment. The agent learns to move laterally (WEST/EAST) and shoot strategically to eliminate waves of aliens while avoiding diving aliens.

---

## Setup

```bash
# From the project root
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Running

Start the game server first (from the project root, in a separate terminal):

```bash
python3 -m server.server
```

The web viewer will be available at `http://localhost:8765/`.

### Train

```bash
python3 -m agents.new_agent -m train -e 200 -o agents/agent.pkl
```

Click **Play** in the web viewer to start each episode. The model is saved automatically after each episode, and training stops once the score reaches 15 000 points.

### Play (run the trained model)

```bash
python3 -m agents.new_agent -m play -o agents/agent.pkl
```

---

## Agent file

| File | Description |
|------|-------------|
| `new_agent.py` | Q-Learning agent (state abstraction, Q-table, reward function) |
| `agent.pkl` | Saved Q-table (generated after training) |
