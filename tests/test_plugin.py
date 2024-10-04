from typing import List, Match
from unittest.mock import MagicMock

import pytest
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.pages import Page

from mkdocs_marimo.plugin import (
    MarimoPlugin,
    MarimoPluginConfig,
    collect_marimo_code,
    find_marimo_code_fences,
    is_inside_four_backticks,
)


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

    # def test_on_page_markdown(
    #     self, plugin: MarimoPlugin, mock_config: MkDocsConfig, mock_page: MagicMock
    # ) -> None:
    #     markdown: str = "```marimo\nprint('HelloWorld!')\n```"

    #     result = plugin.on_page_markdown(markdown, page=mock_page, config=mock_config, files=None)
    #     result = plugin.on_post_page(result, page=mock_page, config=mock_config)

    #     assert "HelloWorld" in result
    #     assert "```marimo" not in result

    def test_on_post_page(
        self, plugin: MarimoPlugin, mock_config: MkDocsConfig, mock_page: MagicMock
    ) -> None:
        output: str = "<head></head><body></body>"
        result: str = plugin.on_post_page(output, page=mock_page, config=mock_config)
        assert "<marimo-filename hidden" in result

    def test_find_marimo_code_fences(self) -> None:
        markdown: str = """
        Some text
        ```marimo
        print('Hello')
        ```
        More text
        ````
        ```marimo
        print('Ignored')
        ```
        ````
        ```marimo-display
        print('Display')
        ```
        """
        matches: List[Match[str]] = find_marimo_code_fences(markdown)
        assert len(matches) == 2
        assert matches[0].group(2).strip() == "print('Hello')"
        assert matches[1].group(2).strip() == "print('Display')"

    def test_collect_marimo_code(self) -> None:
        markdown: str = """
        ```marimo
        code1
        ```
        ```marimo-display
        code2
        ```
        """
        code_blocks, matches = collect_marimo_code(markdown)
        assert code_blocks == ["code1", "code2"]
        assert len(matches) == 2

    def test_is_inside_four_backticks(self):
        markdown = "Some text\n````\n```marimo\ncode\n```\n````\nMore text"
        assert is_inside_four_backticks(markdown, markdown.index("```marimo"))
        assert not is_inside_four_backticks(markdown, 0)

    def test_marimo_plugin_config(self):
        config = MarimoPluginConfig()
        import marimo

        assert config.enabled == True
        assert config.marimo_version == marimo.__version__

    def test_on_page_markdown_with_options(self, mock_page: MagicMock):
        plugin = MarimoPlugin()
        markdown = "```marimo-display\nprint('Hello')\n```"

        result = plugin.on_page_markdown(markdown, page=mock_page, config=MagicMock(), files=None)
        result = plugin.on_post_page(result, page=mock_page, config=MagicMock())

        assert "Hello" in result
        assert "```marimo-display" not in result

    def test_on_post_page_with_existing_marimo_filename(self, mock_page: MagicMock):
        plugin = MarimoPlugin()
        output = "<head></head><body># Content</body>"
        result = plugin.on_post_page(output, page=mock_page, config=MagicMock())

        assert "<marimo-filename hidden></marimo-filename>" in result
        assert result.count("<marimo-filename") == 1  # Ensure we don't add duplicate tags

    def test_on_page_markdown_with_empty_code_block(self, mock_page: MagicMock):
        plugin = MarimoPlugin()
        markdown = "```marimo\n\n```"
        result = plugin.on_page_markdown(markdown, page=mock_page, config=MagicMock(), files=None)
        result = plugin.on_post_page(result, page=mock_page, config=MagicMock())
        assert "```marimo" not in result
        assert "<marimo-island" in result

    def test_on_page_markdown_with_invalid_option(self, mock_page: MagicMock):
        plugin = MarimoPlugin()
        markdown = "```marimo-invalid_option\nprint('Hello')\n```"
        result = plugin.on_page_markdown(markdown, page=mock_page, config=MagicMock(), files=None)
        result = plugin.on_post_page(result, page=mock_page, config=MagicMock())
        assert "```marimo-invalid_option" not in result
        assert "<marimo-island" in result

    def test_on_page_markdown_with_multiple_code_blocks(self, mock_page: MagicMock):
        plugin = MarimoPlugin()
        markdown = "```marimo\nprint('First')\n```\nSome text\n```marimo\nprint('Second')\n```"

        result = plugin.on_page_markdown(markdown, page=mock_page, config=MagicMock(), files=None)
        result = plugin.on_post_page(result, page=mock_page, config=MagicMock())

        assert "First" in result
        assert "Second" in result
        assert "```marimo" not in result

    def test_on_page_markdown_with_exception_in_code_execution(self, mock_page: MagicMock):
        plugin = MarimoPlugin()
        markdown = "```marimo\nraise Exception('Test error')\n```"

        result = plugin.on_page_markdown(markdown, page=mock_page, config=MagicMock(), files=None)
        result = plugin.on_post_page(result, page=mock_page, config=MagicMock())

        assert "This cell raised an exception" in result
        assert "Test error" in result
