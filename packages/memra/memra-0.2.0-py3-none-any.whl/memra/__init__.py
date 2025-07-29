"""
Memra SDK - Declarative framework for enterprise workflows with MCP integration

A powerful orchestration framework that allows you to build AI-powered business workflows
with hybrid cloud/local execution capabilities.
"""

__version__ = "0.2.0"
__author__ = "Memra"
__email__ = "info@memra.co"

# Core imports
from .models import Agent, Department, LLM, Tool
from .execution import ExecutionEngine

# Make key classes available at package level
__all__ = [
    "Agent",
    "Department", 
    "LLM",
    "Tool",
    "ExecutionEngine",
    "__version__"
] 