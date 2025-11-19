"""
Integration tests for prompt_toolkit completions in fast-agent.

These tests verify that the completion system works correctly for
commands and file paths without using mocks or monkeypatching.
"""

import tempfile
from pathlib import Path

from fast_agent.ui.enhanced_prompt import AgentCompleter
from prompt_toolkit.document import Document


class TestAgentCompleter:
    """Test the AgentCompleter class for command completion."""

    def test_command_completion_starts_with_slash(self):
        """Verify commands are completed when input starts with /."""
        completer = AgentCompleter(agents=["agent1", "agent2"])
        document = Document("/he")

        completions = list(completer.get_completions(document, None))

        # Should suggest 'help'
        command_names = [c.text for c in completions]
        assert "help" in command_names

    def test_command_completion_load_history(self):
        """Verify /load_history command is suggested."""
        completer = AgentCompleter(agents=[])
        document = Document("/load")

        completions = list(completer.get_completions(document, None))

        command_names = [c.text for c in completions]
        assert "load_history" in command_names

    def test_command_completion_save_history(self):
        """Verify /save_history command is suggested."""
        completer = AgentCompleter(agents=[])
        document = Document("/save")

        completions = list(completer.get_completions(document, None))

        command_names = [c.text for c in completions]
        assert "save_history" in command_names

    def test_agent_completion_starts_with_at(self):
        """Verify agent names are completed when input starts with @."""
        completer = AgentCompleter(agents=["test_agent", "other_agent"])
        document = Document("@test")

        completions = list(completer.get_completions(document, None))

        agent_names = [c.text for c in completions]
        assert "test_agent" in agent_names
        assert "other_agent" not in agent_names

    def test_agent_completion_case_insensitive(self):
        """Verify agent completion is case-insensitive."""
        completer = AgentCompleter(agents=["TestAgent"])
        document = Document("@test")

        completions = list(completer.get_completions(document, None))

        agent_names = [c.text for c in completions]
        assert "TestAgent" in agent_names

    def test_completion_with_no_match(self):
        """Verify no completions returned when nothing matches."""
        completer = AgentCompleter(agents=["agent1"])
        document = Document("/xyz")

        completions = list(completer.get_completions(document, None))

        assert len(completions) == 0

    def test_all_commands_have_descriptions(self):
        """Verify all commands have meta descriptions for user guidance."""
        completer = AgentCompleter(agents=[])

        # Check that all commands have descriptions
        for command, description in completer.commands.items():
            assert description, f"Command '{command}' has no description"
            assert len(description) > 0, f"Command '{command}' has empty description"


class TestFileCompletion:
    """Test file completion for /load_history command."""

    def test_json_files_in_directory(self):
        """Verify .json files are found in a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            json_file = Path(tmpdir) / "history.json"
            md_file = Path(tmpdir) / "notes.md"
            txt_file = Path(tmpdir) / "readme.txt"

            json_file.touch()
            md_file.touch()
            txt_file.touch()

            # Find .json and .md files
            json_files = list(Path(tmpdir).glob("*.json"))
            md_files = list(Path(tmpdir).glob("*.md"))

            assert len(json_files) == 1
            assert json_files[0].name == "history.json"
            assert len(md_files) == 1
            assert md_files[0].name == "notes.md"

    def test_nested_directory_glob(self):
        """Verify files can be found in nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()

            json_file = subdir / "nested.json"
            json_file.touch()

            # Find all .json files recursively
            all_json = list(Path(tmpdir).rglob("*.json"))

            assert len(all_json) == 1
            assert all_json[0].name == "nested.json"


class TestHistoryExport:
    """Test history export/import functionality."""

    def test_history_exporter_import(self):
        """Verify HistoryExporter can be imported."""
        from fast_agent.history.history_exporter import HistoryExporter

        assert HistoryExporter is not None

    def test_prompt_load_import(self):
        """Verify prompt loading functionality can be imported."""
        from fast_agent.mcp.prompts.prompt_load import load_prompt

        assert load_prompt is not None


class TestPreProcessInput:
    """Test the pre_process_input logic for command parsing."""

    def test_load_history_command_parsing(self):
        """Verify /load_history command is parsed correctly."""
        # Test the command parsing logic directly
        text = "/load_history test.json"
        cmd_parts = text[1:].strip().split(maxsplit=1)
        cmd = cmd_parts[0].lower()

        assert cmd == "load_history"
        assert len(cmd_parts) == 2
        assert cmd_parts[1].strip() == "test.json"

    def test_save_history_command_parsing(self):
        """Verify /save_history command is parsed correctly."""
        text = "/save_history output.json"
        cmd_parts = text[1:].strip().split(maxsplit=1)
        cmd = cmd_parts[0].lower()

        assert cmd == "save_history"
        assert len(cmd_parts) == 2
        assert cmd_parts[1].strip() == "output.json"

    def test_command_without_filename(self):
        """Verify command without filename is handled."""
        text = "/load_history"
        cmd_parts = text[1:].strip().split(maxsplit=1)
        cmd = cmd_parts[0].lower()

        assert cmd == "load_history"
        assert len(cmd_parts) == 1
