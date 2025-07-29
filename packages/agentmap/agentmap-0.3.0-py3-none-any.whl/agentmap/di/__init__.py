# agentmap/di/__init__.py
from typing import Optional, Union
from pathlib import Path
from agentmap.di.containers import ApplicationContainer

# Global container instance
application = ApplicationContainer()


def initialize_di(config_path: Optional[Union[str, Path]] = None) -> ApplicationContainer:
    """
    Initialize the DI container for CLI usage.

    This should be called at the start of every CLI command before
    any code that uses @inject decorators.

    Args:
        config_path: Path to the configuration file

    Returns:
        Initialized application container
    """
    # Configure the container with the provided config path
    config_path = config_path or "agentmap_config.yaml"
    application.config_path.override(config_path)

    # Initialize logging early - this ensures logging is configured
    # before any other code that might want to log
    logging_service = application.logging_service()
    logging_service.initialize()

    # Wire the container to all modules that use injection
    application.wire(modules=[
        "agentmap.graph.assembler",
        "agentmap.graph.builder",
        "agentmap.runner",
        "agentmap.prompts.manager",
        "agentmap.compiler",
        "agentmap.graph.scaffold",
        "agentmap.services.llm_service",
        "agentmap.services.node_registry_service",
    ])

    # Force initialization of configuration to catch any errors early
    _ = application.configuration()

    return application


def cleanup():
    """Clean up the DI container (useful for testing or between commands)."""
    # Reset logging
    logging_service = application.logging_service()
    logging_service.reset()

    # Unwire the container
    application.unwire()