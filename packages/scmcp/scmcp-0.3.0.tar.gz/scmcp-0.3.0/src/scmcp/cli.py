"""
Command-line interface for scmcp.

This module provides a CLI entry point for the scmcp package.
"""
from enum import Enum
from scmcp_shared.cli import MCPCLI
from .server import SCMCPManager


class ModuleEnum(str, Enum):
    """Base class for module types."""
    ALL = "all"
    SC = "sc"
    LI = "li"
    CR = "cr"
    DC = "dc"


cli = MCPCLI(
    name="scmcp", 
    help_text="SCMCP Server CLI",
    manager=SCMCPManager,
    modules=ModuleEnum
)

def run_cli():
    cli.app()