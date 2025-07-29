import os
from pathlib import Path
from dallinger.config import get_config

# Get absolute path to experiment.py
experiment_path = Path(__file__).parent / "experiment.py"
print(f"Experiment path: {experiment_path}")
print(f"Path exists: {experiment_path.exists()}")

# Try to load config
config = get_config()
config.load()
print("Config loaded successfully")
