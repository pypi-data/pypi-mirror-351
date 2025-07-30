# spell/__init__.py
from .main import Spell
from .main import PipeWriter, _execute_code_target, listen_for_interrupt_module_level
try:
    from .main import LLMProvider
except ImportError:
    LLMProvider = None

__version__ = "0.1.1"
__all__ = [
    'Spell',
    'PipeWriter',
    'LLMProvider',
    '__version__',
]