import os
from pathlib import Path
from typing import List, Match, Optional
from unittest.mock import MagicMock

import marimo
import pytest
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

from mkdocs_marimo.plugin import (
    MarimoPlugin,
    MarimoPluginConfig,
    VirtualFile,
    collect_marimo_code,
    find_marimo_code_fences,
    is_inside_four_backticks,
)


class MockFile(File):
    def __init__(self, abs_src_path: str):
        self.abs_src_path = abs_src_path
        super().__init__(abs_src_path, src_dir=None, dest_dir="", use_directory_urls=False)

    @property
    def abs_url(self) -> Optional[str]:
        return self.abs_src_path


class MockPage(Page):
    def __init__(self, abs_src_path: str):
        self.file = MockFile(abs_src_path)
        super().__init__(None, self.file, MkDocsConfig())
        self.abs_url = abs_src_path


class TestMarimoPlugin:
    @pytest.fixture
    def plugin(self) -> MarimoPlugin:
        return MarimoPlugin()

    @pytest.fixture
    def mock_config(self) -> MkDocsConfig:
        return MkDocsConfig()

    @pytest.fixture
    def mock_page(self) -> MagicMock:
        page = MagicMock(spec=Page)
        page.abs_url = "/home"
        return page

    def test_on_page_markdown(
        self, plugin: MarimoPlugin, mock_config: MkDocsConfig, mock_page: MagicMock
    ) -> None:
        markdown: str = "```python {marimo}\nprint('HelloWorld!')\n```"

        result = plugin.on_page_markdown(markdown, page=mock_page, config=mock_config, files=None)
        result = plugin.on_post_page(result, page=mock_page, config=mock_config)

        assert "HelloWorld" in result
        assert "```python {marimo}" not in result

    def test_on_post_page(
        self, plugin: MarimoPlugin, mock_config: MkDocsConfig, mock_page: MagicMock
    ) -> None:
        output: str = "<head></head><body></body>"
        result: str = plugin.on_post_page(output, page=mock_page, config=mock_config)
        assert "<marimo-filename hidden" in result

    def test_find_marimo_code_fences(self) -> None:
        markdown: str = """
        Some text
        ```python {marimo}
        print('Hello')
        ```
        More text
        ````
        ```python {marimo}
        print('Ignored')
        ```
        ````
        ```python {marimo-display}
        print('Display')
        ```
        """
        matches: List[Match[str]] = find_marimo_code_fences(markdown)
        assert len(matches) == 2
        assert matches[0].group(2).strip() == "print('Hello')"
        assert matches[1].group(2).strip() == "print('Display')"

    def test_collect_marimo_code(self) -> None:
        markdown: str = """
        ```python {marimo}
        code1
        ```
        ```python {marimo-display}
        code2
        ```
        """
        code_blocks, matches = collect_marimo_code(markdown)
        assert code_blocks == ["code1", "code2"]
        assert len(matches) == 2

    def test_is_inside_four_backticks(self):
        markdown = "Some text\n````\n```python {marimo}\ncode\n```\n````\nMore text"
        assert is_inside_four_backticks(markdown, markdown.index("```python {marimo}"))
        assert not is_inside_four_backticks(markdown, 0)

    def test_marimo_plugin_config(self):
        config = MarimoPluginConfig()

        assert config.enabled == True
        assert config.marimo_version == marimo.__version__

    def test_parse_options(self, plugin: MarimoPlugin):
        options_string = "display_code=true width=500 height=300 is_reactive"
        expected = {"display_code": True, "width": 500, "height": 300, "is_reactive": True}
        assert plugin.parse_options(options_string) == expected

    def test_parse_value(self, plugin: MarimoPlugin):
        assert plugin.parse_value("true") == True
        assert plugin.parse_value("false") == False
        assert plugin.parse_value("42") == 42
        assert plugin.parse_value("3.14") == 3.14
        assert plugin.parse_value("hello") == "hello"

    def test_on_page_markdown_with_options(self, plugin: MarimoPlugin, mock_page: MagicMock):
        markdown = "```python {marimo display_code=true width=500}\nprint('Hello')\n```"

        result = plugin.on_page_markdown(markdown, page=mock_page, config=MagicMock(), files=None)
        result = plugin.on_post_page(result, page=mock_page, config=MagicMock())

        assert "Hello" in result
        assert "```python {marimo display_code=true width=500}" not in result
        assert "<marimo-island" in result
        # Unsupported options are ignored
        assert 'style="width: 500px;"' not in result

    def test_on_post_page_with_existing_marimo_filename(self, mock_page: MagicMock):
        plugin = MarimoPlugin()
        output = "<head></head><body># Content</body>"
        result = plugin.on_post_page(output, page=mock_page, config=MagicMock())

        assert "<marimo-filename hidden></marimo-filename>" in result
        assert result.count("<marimo-filename") == 1  # Ensure we don't add duplicate tags

    def test_on_page_markdown_with_empty_code_block(self, mock_page: MagicMock):
        plugin = MarimoPlugin()
        markdown = "```python {marimo}\n\n```"
        result = plugin.on_page_markdown(markdown, page=mock_page, config=MagicMock(), files=None)
        result = plugin.on_post_page(result, page=mock_page, config=MagicMock())
        assert "```python {marimo}" not in result
        assert "<marimo-island" in result

    def test_on_page_markdown_with_invalid_option(self, mock_page: MagicMock):
        plugin = MarimoPlugin()
        markdown = "```python {marimo-invalid_option}\nprint('Hello')\n```"
        result = plugin.on_page_markdown(markdown, page=mock_page, config=MagicMock(), files=None)
        result = plugin.on_post_page(result, page=mock_page, config=MagicMock())
        assert "```python {marimo-invalid_option}" not in result
        assert "<marimo-island" in result

    def test_on_page_markdown_with_multiple_code_blocks(self, mock_page: MagicMock):
        plugin = MarimoPlugin()
        markdown = "```python {marimo}\nprint('First')\n```\nSome text\n```python {marimo}\nprint('Second')\n```"

        result = plugin.on_page_markdown(markdown, page=mock_page, config=MagicMock(), files=None)
        result = plugin.on_post_page(result, page=mock_page, config=MagicMock())

        assert "First" in result
        assert "Second" in result
        assert "```python {marimo}" not in result

    def test_on_page_markdown_with_exception_in_code_execution(self, mock_page: MagicMock):
        plugin = MarimoPlugin()
        markdown = "```python {marimo}\nraise Exception('Test error')\n```"

        result = plugin.on_page_markdown(markdown, page=mock_page, config=MagicMock(), files=None)
        result = plugin.on_post_page(result, page=mock_page, config=MagicMock())

        assert "This cell raised an exception" in result
        assert "Test error" in result

    def test_process_marimo_file_directives(self, plugin: MarimoPlugin, tmp_path: Path) -> None:
        # Create a temporary marimo file
        marimo_file = tmp_path / "example.py"
        marimo_file.write_text("""
import marimo
app = marimo.App()

@app.cell
def __():
    print('Hello from marimo!')

if __name__ == "__main__":
    app.run()
""")

        mock_page = MockPage(str(tmp_path / "current_file.md"))

        markdown = f"Some text\n!marimo_file {marimo_file.name}\nMore text"

        result = plugin.process_marimo_file_directives(markdown, mock_page, config=MkDocsConfig())

        # The actual content of the generated HTML will depend on your implementation
        # Here we're just checking that the directive was replaced with some HTML
        assert result.startswith("Some text\n<")
        assert result.endswith(">\nMore text")
        assert "marimo" in result.lower()

    def test_resolve_marimo_file_path(self, plugin: MarimoPlugin):
        mock_page = MockPage("/path/to/current/file.md")

        file_path = "../example.py"

        result = plugin.resolve_marimo_file_path(file_path, mock_page, "/path/to")
        expected = os.path.normpath("/path/to/example.py")
        assert result == expected

    def test_generate_marimo_html(self, plugin: MarimoPlugin, tmp_path: Path) -> None:
        file_content = """
import marimo
app = marimo.App()

@app.cell
def __():
    print('Hello from marimo!')

if __name__ == "__main__":
    app.run()
"""
        file_path = tmp_path / "example.py"
        file_path.write_text(file_content)

        result = plugin.generate_marimo_body(str(file_path))

        assert "Hello%20from%20marimo!" in result
        assert "<marimo-island" in result

    def test_on_page_markdown_with_marimo_file_directive(
        self, plugin: MarimoPlugin, mock_config: MkDocsConfig, tmp_path: Path
    ):
        file_content = """
import marimo
app = marimo.App()

@app.cell
def __():
    print('Hello from included marimo file!')

if __name__ == "__main__":
    app.run()
"""
        file_path = tmp_path / "example.py"
        file_path.write_text(file_content)

        markdown = "# Title\n!marimo_file /example.py\n## Section"
        mock_page = MockPage(str(tmp_path / "current_file.md"))

        mock_config = MkDocsConfig()
        mock_config.docs_dir = str(tmp_path)
        result = plugin.on_page_markdown(markdown, page=mock_page, config=mock_config, files=None)
        assert "Hello%20from%20included%20marimo%20file!" in result
        assert "!marimo_file /example.py" not in result
        assert "<marimo-island" in result

    def test_global_config_and_code_fence_options(self, tmp_path: Path):
        # Create a custom config with global options
        custom_config = MarimoPluginConfig()
        custom_config.display_code = True
        custom_config.display_output = False
        custom_config.is_reactive = False

        plugin = MarimoPlugin()
        plugin.config = custom_config

        # Create a mock page
        mock_page = MockPage(str(tmp_path / "test_page.md"))

        # Test case 1: Use global config
        markdown1 = "```python {marimo}\nprint('Hello')\n```"
        result1 = plugin.on_page_markdown(
            markdown1, page=mock_page, config=MkDocsConfig(), files=None
        )
        result1 = plugin.on_post_page(result1, page=mock_page, config=MkDocsConfig())

        assert "Hello" in result1
        # Visible code
        assert "<marimo-code-editor" in result1
        # No output
        assert "<marimo-cell-output></marimo-cell-output>" in result1
        assert "data-reactive=false" in result1

        # Test case 2: Override global config with code fence options
        markdown2 = "```python {marimo display_code=false display_output=true is_reactive=true}\n'World'\n```"
        result2 = plugin.on_page_markdown(
            markdown2, page=mock_page, config=MkDocsConfig(), files=None
        )
        result2 = plugin.on_post_page(result2, page=mock_page, config=MkDocsConfig())

        assert "World" in result2
        # Not visible code
        assert "<marimo-code-editor" not in result2
        # Output
        assert (
            '<marimo-cell-output><pre style="font-size: 12px">World</pre></marimo-cell-output>'
            in result2
        )
        assert "data-reactive=true" in result2

        # Test case 3: Partially override global config
        markdown3 = "```python {marimo display_output=true}\n'Partial'\n```"
        result3 = plugin.on_page_markdown(
            markdown3, page=mock_page, config=MkDocsConfig(), files=None
        )
        result3 = plugin.on_post_page(result3, page=mock_page, config=MkDocsConfig())

        assert "Partial" in result3
        # Visible code
        assert "<marimo-code-editor" in result3
        # Output
        assert (
            '<marimo-cell-output><pre style="font-size: 12px">Partial</pre></marimo-cell-output>'
            in result3
        )
        assert "data-reactive=false" in result3

    def test_plugin_enabled(self, tmp_path: Path):
        # Test when plugin is enabled (default)
        plugin = MarimoPlugin()
        markdown = "```python {marimo}\nprint('Hello')\n```"
        mock_page = MockPage(str(tmp_path / "test_page.md"))
        result = plugin.on_page_markdown(
            markdown, page=mock_page, config=MkDocsConfig(), files=None
        )
        assert "<marimo-internal-island" in result

        # Test when plugin is disabled
        plugin.config.enabled = False
        result = plugin.on_page_markdown(
            markdown, page=mock_page, config=MkDocsConfig(), files=None
        )
        assert result == markdown  # Markdown should be unchanged

    def test_on_post_page_with_plugin_disabled(self, mock_page: MagicMock):
        plugin = MarimoPlugin()
        plugin.config.enabled = False
        output = "<head></head><body># Content</body>"
        result = plugin.on_post_page(output, page=mock_page, config=MkDocsConfig())
        assert result == output  # Output should be unchanged when plugin is disabled

    def test_process_python_file_in_navigation(self, tmp_path: Path):
        plugin = MarimoPlugin()

        # Create a mock MkDocs config
        config = MkDocsConfig()
        config.docs_dir = str(tmp_path)
        config.site_dir = str(tmp_path / "site")
        config.use_directory_urls = True
        config.nav = [{"Home": "index.md"}, {"Python File": "example.py"}]

        # Create a mock marimo Python file
        py_file_path = tmp_path / "example.py"
        py_file_path.write_text("""
import marimo
app = marimo.App()

@app.cell
def __():
    print('Hello from marimo!')

if __name__ == "__main__":
    app.run()
""")

        # Create a mock files collection
        files = Files(
            [
                File("index.md", str(tmp_path), str(tmp_path / "site"), use_directory_urls=True),
                File("example.py", str(tmp_path), str(tmp_path / "site"), use_directory_urls=True),
            ]
        )

        # Process the files
        processed_files = plugin.on_files(files, config=config)

        # Check that the Python file was replaced with a virtual Markdown file
        md_file = next((f for f in processed_files if f.src_path == "example.md"), None)
        assert md_file is not None
        assert isinstance(md_file, VirtualFile)
        assert not any(f.src_path.endswith("example.py") for f in processed_files)

        # Check the content of the generated virtual Markdown file
        md_content = md_file.read_text()
        assert "!marimo_file /example.py" in md_content

        # Check that the navigation was updated
        assert config.nav == [{"Home": "index.md"}, {"Python File": "example.md"}]
