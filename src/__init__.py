# agent/__init__.py

# Import different agents from different files
import os
from .day_trip import root_agent as day_trip_agent
from .telephone_game import root_agent as telephone_agent  
from .spymaster import root_agent as spymaster_agent
from .operative import root_agent as operative_agent
from .gamemaster import root_agent as gamemaster_agent
#from .run_game import root_agent as game_master_agent
# Optional: allow override via environment variable (e.g., "ADK_AGENT=day_trip")
selected = os.getenv("ADK_AGENT", "telephone")

# Map name to agent
agents = {
    "telephone": telephone_agent,
    "day_trip": day_trip_agent,
    "spymaster": spymaster_agent,
    "operative": operative_agent,
    "gamemaster": gamemaster_agent,
}

# Choose the agent to expose
root_agent = agents.get(selected, telephone_agent)
# Choose which one to expose as the main agent
# noroot_agent = telephone_agent  # ← Change this to switch agents

__all__ = ['root_agent']