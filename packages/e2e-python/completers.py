"""
Custom completers for fast-agent with file path completion support.

This module provides an enhanced completer that adds file path completion
for commands like /load_history, suggesting .json and .md files.
"""

from pathlib import Path
from typing import Any

from fast_agent.agents.agent_types import AgentType
from fast_agent.ui.enhanced_prompt import AgentCompleter
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document


class FilePathCompleter(Completer):
    """
    Completer for file paths that filters by extensions.

    This completer suggests files matching specified extensions
    (.json and .md by default) for history loading operations.
    """

    def __init__(self, extensions: list[str] | None = None, base_path: Path | None = None):
        """
        Initialize the file path completer.

        Args:
            extensions: List of file extensions to match (e.g., ['.json', '.md'])
            base_path: Base directory to search from (defaults to current directory)
        """
        self.extensions = extensions or [".json", ".md"]
        self.base_path = base_path or Path.cwd()

    def get_completions(self, document: Document, complete_event: Any):
        """Generate file path completions."""
        text = document.text_before_cursor

        # Determine the path being typed
        if "/" in text:
            # User is typing a path
            path_text = text
        else:
            path_text = text

        # Handle relative and absolute paths
        if path_text.startswith("/"):
            search_path = Path(path_text)
        elif path_text.startswith("~"):
            search_path = Path(path_text).expanduser()
        else:
            search_path = self.base_path / path_text

        # Get the directory to search and the prefix to match
        if search_path.is_dir():
            search_dir = search_path
            prefix = ""
        else:
            search_dir = search_path.parent
            prefix = search_path.name

        # Ensure the directory exists
        if not search_dir.exists():
            return

        try:
            # List files in the directory
            for item in sorted(search_dir.iterdir()):
                # Match prefix
                if prefix and not item.name.lower().startswith(prefix.lower()):
                    continue

                # For directories, always show them for navigation
                if item.is_dir():
                    display_name = f"{item.name}/"
                    yield Completion(
                        display_name,
                        start_position=-len(prefix),
                        display=display_name,
                        display_meta="directory",
                    )
                # For files, filter by extension
                elif item.suffix.lower() in self.extensions:
                    yield Completion(
                        item.name,
                        start_position=-len(prefix),
                        display=item.name,
                        display_meta=f"{item.suffix} file",
                    )
        except PermissionError:
            # Skip directories we can't read
            pass


class EnhancedAgentCompleter(AgentCompleter):
    """
    Enhanced agent completer with file path completion for history commands.

    This extends the base AgentCompleter to provide file suggestions
    when the user types /load_history or /save_history followed by a space.
    """

    def __init__(
        self,
        agents: list[str],
        commands: list[str] | None = None,
        agent_types: dict | None = None,
        is_human_input: bool = False,
        file_extensions: list[str] | None = None,
    ):
        """
        Initialize the enhanced completer.

        Args:
            agents: List of available agent names
            commands: Optional custom commands
            agent_types: Dictionary mapping agent names to their types
            is_human_input: Whether this is a human input request
            file_extensions: File extensions to suggest for history commands
        """
        super().__init__(agents, commands, agent_types, is_human_input)
        self.file_completer = FilePathCompleter(extensions=file_extensions)

    def get_completions(self, document: Document, complete_event: Any):
        """Generate completions for commands, agents, and file paths."""
        original_text = document.text_before_cursor

        # Check if we're completing a file path for history commands
        history_commands = ["/load_history ", "/load ", "/save_history ", "/save "]
        for cmd in history_commands:
            if original_text.lower().startswith(cmd):
                # Extract the file path portion
                file_part = original_text[len(cmd) :]

                # Create a new document with just the file path
                file_document = Document(file_part)

                # Get file completions
                yield from self.file_completer.get_completions(file_document, complete_event)
                return

        # Fall back to base completion for commands and agents
        yield from super().get_completions(document, complete_event)


def create_enhanced_completer(
    agents: list[str],
    agent_types: dict[str, AgentType] | None = None,
    is_human_input: bool = False,
) -> EnhancedAgentCompleter:
    """
    Factory function to create an enhanced completer.

    Args:
        agents: List of available agent names
        agent_types: Dictionary mapping agent names to their types
        is_human_input: Whether this is a human input request

    Returns:
        An EnhancedAgentCompleter instance with file completion support
    """
    return EnhancedAgentCompleter(
        agents=agents,
        agent_types=agent_types or {},
        is_human_input=is_human_input,
        file_extensions=[".json", ".md"],
    )
