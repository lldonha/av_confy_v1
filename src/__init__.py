"""
Lipsync ComfyUI Workflow - Sistema de geração de vídeos com lipsync
Desenvolvido para o canal CÓSMICA DREAD
"""

__version__ = "1.0.0"
__author__ = "Cósmica Dread Team"

from .logger import get_logger, setup_logging
from .error_handler import (
    ModelNotFoundError,
    VRAMInsufficientError,
    NodeMissingError,
    WorkflowValidationError,
    AudioGenerationError,
    LipsyncFailedError
)
from .model_manager import ModelManager
from .workflow_executor import WorkflowExecutor

__all__ = [
    'get_logger',
    'setup_logging',
    'ModelNotFoundError',
    'VRAMInsufficientError',
    'NodeMissingError',
    'WorkflowValidationError',
    'AudioGenerationError',
    'LipsyncFailedError',
    'ModelManager',
    'WorkflowExecutor'
]
