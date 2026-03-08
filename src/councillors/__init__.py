"""
Councillors module - Houses all LLM councillors for the debate system.
"""
from .base import Councillor
from .nova_premier import NovaPremierCouncillor, nova_premier_councillor
from .claude_sonnet_v4 import ClaudeSonnetV4Councillor, claude_sonnet_v4_councillor
from .nova_lite_v2 import NovaLiteV2Councillor, nova_lite_councillor
from .llama_3_3_70B import Llama33Councillor, llama_councillor
from .nova_pro import NovaProCouncillor, nova_pro_councillor

__all__ = [
    "Councillor",
    "NovaPremierCouncillor",
    "ClaudeSonnetV4Councillor",
    "NovaProCouncillor",
    "NovaLiteV2Councillor",
    "Llama33Councillor",
    "nova_premier_councillor",
    "claude_sonnet_v4_councillor",
    "nova_pro_councillor",
    "nova_lite_councillor",
    "llama_councillor",
]
