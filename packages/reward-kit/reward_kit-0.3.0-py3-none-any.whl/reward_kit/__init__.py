"""
Fireworks Reward Kit - Simplify reward modeling for LLM RL fine-tuning.

A Python library for defining, testing, deploying, and using reward functions
for LLM fine-tuning, including launching full RL jobs on the Fireworks platform.

The library also provides an agent evaluation framework for testing and evaluating
tool-augmented models using self-contained task bundles.
"""

import warnings

# Import everything from models
from .models import EvaluateResult, Message, MetricResult

# Import from reward_function
from .reward_function import RewardFunction

# Import the decorator from typed_interface
from .typed_interface import reward_function

# Show deprecation warnings
warnings.filterwarnings("default", category=DeprecationWarning, module="reward_kit")

__all__ = [
    # Core interfaces
    "Message",
    "MetricResult",
    "EvaluateResult",
    "reward_function",
    "RewardFunction",
]

from . import _version
__version__ = _version.get_versions()['version']
