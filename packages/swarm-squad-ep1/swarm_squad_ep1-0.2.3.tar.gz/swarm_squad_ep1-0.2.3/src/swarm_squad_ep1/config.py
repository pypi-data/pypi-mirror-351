"""
Configuration parameters for the formation control simulation.
"""

from enum import Enum

import numpy as np


# Obstacle modes
class ObstacleMode(Enum):
    HARD = "physical"  # Physical obstacle
    LOW_POWER_JAMMING = "low_power_jamming"  # Communication degradation
    HIGH_POWER_JAMMING = "high_power_jamming"  # Abrupt disruption


# Active obstacle mode
OBSTACLE_MODE = ObstacleMode.HARD  # Default obstacle mode

# Jamming parameters
JAMMING_RADIUS_MULTIPLIER = (
    2.0  # How much larger jamming radius is than physical radius
)
LOWPOWER_JAMMING_DEGRADATION = 0.8  # Base factor for low power jamming (higher = less degradation at edge of field)
# Note: Actual degradation is gradual based on penetration depth into jamming field
# At the edge: degradation_factor = LOWPOWER_JAMMING_DEGRADATION (mild effect)
# Deep inside: degradation_factor approaches 0.2 (severe effect)

# Predefined obstacles
# Format: List of tuples (x, y, radius)
# If list is empty, no obstacles will be pre-drawn
PREDEFINED_OBSTACLES = [
    # Example: (x, y, radius)
    # (20, 50, 10),
    # (-10, 70, 25),
]


# Simulation parameters
MAX_ITER = 1000
ALPHA = 10 ** (-5)
DELTA = 2
BETA = ALPHA * (2**DELTA - 1)
V = 3
R0 = 5
PT = 0.94

# Initial swarm positions
INITIAL_SWARM_POSITIONS = np.array(
    [[-5, 4], [-5, -9], [0, -10], [35, -14], [68, -10], [72, 3], [72, -8]],
    dtype=float,
)

# Default destination
DEFAULT_DESTINATION = np.array([35, 150], dtype=float)

# Node and line visualization colors
NODE_COLORS = [
    [108 / 255, 155 / 255, 207 / 255],  # Light Blue
    [247 / 255, 147 / 255, 39 / 255],  # Orange
    [242 / 255, 102 / 255, 171 / 255],  # Light Pink
    [255 / 255, 217 / 255, 90 / 255],  # Light Gold
    [122 / 255, 168 / 255, 116 / 255],  # Green
    [147 / 255, 132 / 255, 209 / 255],  # Purple
    [245 / 255, 80 / 255, 80 / 255],  # Red
]

# Movement Controller parameters
DESTINATION_ATTRACTION_MAGNITUDE = 1.0  # am parameter
DESTINATION_DISTANCE_THRESHOLD = 1.0  # bm parameter
OBSTACLE_AVOIDANCE_MAGNITUDE = 3.0  # ao parameter
OBSTACLE_INFLUENCE_RANGE = 6.0  # bo parameter
WALL_FOLLOWING_MAGNITUDE = 2.0  # af parameter
WALL_DISTANCE = 10.0  # df parameter

# LLM Integration Parameters
LLM_ENABLED = True
LLM_FEEDBACK_INTERVAL = 5  # How often to send updates to LLM (every N simulation steps) - increase for less frequent updates
LLM_ENDPOINT = "http://localhost:11434/api/generate"  # Ollama direct endpoint
LLM_MODEL = "llama3.3:70b-instruct-q4_K_M"  # Model to use with Ollama
AGENT_NAMES = [
    f"Agent-{i}" for i in range(len(INITIAL_SWARM_POSITIONS))
]  # Default agent names

LLM_NORMAL_PROMPT = """You are a tactical advisor for a swarm of autonomous vehicles.

IMPORTANT CONTEXT:
- Communication quality ranges from 0 (no connection) to 1 (perfect quality)
- Quality above 0.94 is considered "good" and below 0.94 is "poor"
- The swarm needs to maintain good communication while reaching the destination
- Physical obstacles should be avoided by all agents

YOUR TASK:
1. Analyze the formation and communication quality between agents
2. Provide PRECISE directional instructions for effective movement
3. Specify EXACT directions using the following system:
   - Cardinal: north, east, south, west
   - Ordinal: northeast, southeast, southwest, northwest
   - Secondary: north-northeast, east-northeast, east-southeast, south-southeast, 
     south-southwest, west-southwest, west-northwest, north-northwest
   - Tertiary: north by northeast, northeast by north, northeast by east, east by northeast,
     east by southeast, southeast by east, southeast by south, south by southeast,
     south by southwest, southwest by south, southwest by west, west by southwest,
     west by northwest, northwest by west, northwest by north, north by northwest
4. Ensure all agents maintain good communication links
5. Focus on reaching the destination efficiently while maintaining formation

FORMAT YOUR RESPONSE as a 30-word tactical instruction with specific agent numbers and EXACT directions:
Example: "Agent-1: Move 5 units east by southeast to improve formation. Agent-2: Reposition 4 units north-northeast to maintain optimal spacing."

REMEMBER: Balance between maintaining formation and reaching the destination is key."""

LLM_ALTERNATE_PROMPT = """You are a tactical advisor for a swarm of autonomous vehicles specializing in ESCAPING JAMMING FIELDS and OBSTACLES.

IMPORTANT CONTEXT:
- Communication quality ranges from 0 (no connection) to 1 (perfect quality)
- Quality above 0.94 is considered "good" and below 0.94 is "poor"
- Low-power jamming causes gradual degradation of communication quality
- High-power jamming causes abrupt disconnection and agents return to base
- JAMMING FIELDS ARE YOUR PRIMARY CONCERN - they must be escaped immediately
- OBSTACLES ARE YOUR SECONDARY CONCERN - they should be avoided but not at the expense of escaping jamming fields

YOUR TASK:
1. Identify agents inside jamming fields (showing communication degradation)
2. Provide PRECISE directional instructions to escape jamming
3. Specify EXACT directions using the following system:
   - Cardinal: north, east, south, west
   - Ordinal: northeast, southeast, southwest, northwest
   - Secondary: north-northeast, east-northeast, east-southeast, south-southeast, 
     south-southwest, west-southwest, west-northwest, north-northwest
   - Tertiary: north by northeast, northeast by north, northeast by east, east by northeast,
     east by southeast, southeast by east, southeast by south, south by southeast,
     south by southwest, southwest by south, southwest by west, west by southwest,
     west by northwest, northwest by west, northwest by north, north by northwest
4. Always prioritize MOVING AWAY FROM JAMMING FIELDS or OBSTACLES over formation integrity
5. Suggest distance values between 5-10 units for effective escape

FORMAT YOUR RESPONSE as a 30-word tactical instruction with specific agent numbers and EXACT directions:
Example: "Agent-1: Move 8 units north-northwest to escape jamming. Agent-2: Reposition 10 units west by southwest to exit interference field."

REMEMBER: Focus on EXTRACTING AGENTS FROM JAMMING FIELDS or OBSTACLES first, maintain formation second."""
