"""
Integration tests for file path completion in history commands.

These tests verify that the enhanced completer correctly suggests
.json and .md files when using /load_history command.
"""

import tempfile
from pathlib import Path

from prompt_toolkit.document import Document

from completers import EnhancedAgentCompleter, FilePathCompleter, create_enhanced_completer


class TestFilePathCompleter:
    """Test the FilePathCompleter class."""

    def test_completes_json_files(self):
        """Verify .json files are suggested."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            (Path(tmpdir) / "history.json").touch()
            (Path(tmpdir) / "config.json").touch()
            (Path(tmpdir) / "readme.txt").touch()

            completer = FilePathCompleter(base_path=Path(tmpdir))
            document = Document("")

            completions = list(completer.get_completions(document, None))

            names = [c.text for c in completions]
            assert "history.json" in names
            assert "config.json" in names
            assert "readme.txt" not in names

    def test_completes_md_files(self):
        """Verify .md files are suggested."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "notes.md").touch()
            (Path(tmpdir) / "readme.txt").touch()

            completer = FilePathCompleter(base_path=Path(tmpdir))
            document = Document("")

            completions = list(completer.get_completions(document, None))

            names = [c.text for c in completions]
            assert "notes.md" in names
            assert "readme.txt" not in names

    def test_completes_directories(self):
        """Verify directories are suggested for navigation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            (Path(tmpdir) / "file.json").touch()

            completer = FilePathCompleter(base_path=Path(tmpdir))
            document = Document("")

            completions = list(completer.get_completions(document, None))

            names = [c.text for c in completions]
            assert "subdir/" in names
            assert "file.json" in names

    def test_prefix_matching(self):
        """Verify prefix matching works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "history1.json").touch()
            (Path(tmpdir) / "history2.json").touch()
            (Path(tmpdir) / "config.json").touch()

            completer = FilePathCompleter(base_path=Path(tmpdir))
            document = Document("hist")

            completions = list(completer.get_completions(document, None))

            names = [c.text for c in completions]
            assert "history1.json" in names
            assert "history2.json" in names
            assert "config.json" not in names

    def test_case_insensitive_prefix(self):
        """Verify prefix matching is case-insensitive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "History.json").touch()

            completer = FilePathCompleter(base_path=Path(tmpdir))
            document = Document("hist")

            completions = list(completer.get_completions(document, None))

            names = [c.text for c in completions]
            assert "History.json" in names

    def test_nonexistent_directory(self):
        """Verify graceful handling of nonexistent directories."""
        completer = FilePathCompleter(base_path=Path("/nonexistent/path"))
        document = Document("")

        completions = list(completer.get_completions(document, None))

        assert len(completions) == 0

    def test_custom_extensions(self):
        """Verify custom extensions are respected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file.json").touch()
            (Path(tmpdir) / "file.yaml").touch()

            completer = FilePathCompleter(extensions=[".yaml"], base_path=Path(tmpdir))
            document = Document("")

            completions = list(completer.get_completions(document, None))

            names = [c.text for c in completions]
            assert "file.yaml" in names
            assert "file.json" not in names


class TestEnhancedAgentCompleter:
    """Test the EnhancedAgentCompleter class."""

    def test_command_completion_still_works(self):
        """Verify base command completion is preserved."""
        completer = EnhancedAgentCompleter(agents=["agent1"])
        document = Document("/he")

        completions = list(completer.get_completions(document, None))

        names = [c.text for c in completions]
        assert "help" in names

    def test_agent_completion_still_works(self):
        """Verify base agent completion is preserved."""
        completer = EnhancedAgentCompleter(agents=["test_agent"])
        document = Document("@test")

        completions = list(completer.get_completions(document, None))

        names = [c.text for c in completions]
        assert "test_agent" in names

    def test_load_history_file_completion(self):
        """Verify file completion works for /load_history command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "history.json").touch()

            # Change to temp directory for the test
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                completer = EnhancedAgentCompleter(agents=[])
                document = Document("/load_history ")

                completions = list(completer.get_completions(document, None))

                names = [c.text for c in completions]
                assert "history.json" in names
            finally:
                os.chdir(original_cwd)

    def test_load_shorthand_file_completion(self):
        """Verify file completion works for /load command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.md").touch()

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                completer = EnhancedAgentCompleter(agents=[])
                document = Document("/load ")

                completions = list(completer.get_completions(document, None))

                names = [c.text for c in completions]
                assert "test.md" in names
            finally:
                os.chdir(original_cwd)

    def test_save_history_file_completion(self):
        """Verify file completion works for /save_history command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "existing.json").touch()

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                completer = EnhancedAgentCompleter(agents=[])
                document = Document("/save_history ")

                completions = list(completer.get_completions(document, None))

                names = [c.text for c in completions]
                assert "existing.json" in names
            finally:
                os.chdir(original_cwd)


class TestCreateEnhancedCompleter:
    """Test the factory function."""

    def test_creates_completer(self):
        """Verify factory creates a valid completer."""
        completer = create_enhanced_completer(agents=["agent1", "agent2"])

        assert isinstance(completer, EnhancedAgentCompleter)

    def test_respects_agent_types(self):
        """Verify agent types are passed through."""
        from fast_agent.agents.agent_types import AgentType

        completer = create_enhanced_completer(
            agents=["agent1"],
            agent_types={"agent1": AgentType.BASIC},
        )

        assert "agent1" in completer.agent_types
        assert completer.agent_types["agent1"] == AgentType.BASIC

    def test_file_extensions_configured(self):
        """Verify file extensions are configured correctly."""
        completer = create_enhanced_completer(agents=[])

        assert ".json" in completer.file_completer.extensions
        assert ".md" in completer.file_completer.extensions
