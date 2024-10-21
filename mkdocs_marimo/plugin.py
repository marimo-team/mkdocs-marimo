import asyncio
import logging
import os
import re
from typing import Any, Dict, Optional

import htmlmin
import marimo
from mkdocs.config.base import Config as BaseConfig
from mkdocs.config.config_options import Type as OptionType
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

log = logging.getLogger("mkdocs.plugins.marimo")

CODE_FENCE_REGEX = re.compile(r"```python\s*{marimo([^}]*)}\n([\s\S]+?)```", flags=re.MULTILINE)


def is_inside_four_backticks(markdown: str, start_pos: int) -> bool:
    backticks = "````"
    before = markdown[:start_pos]
    return before.count(backticks) % 2 == 1


def find_marimo_code_fences(markdown: str) -> list[re.Match[str]]:
    matches: list[Any] = []
    for match in CODE_FENCE_REGEX.finditer(markdown):
        if not is_inside_four_backticks(markdown, match.start()):
            matches.append(match)
    return matches


def collect_marimo_code(markdown: str) -> tuple[list[str], list[re.Match[str]]]:
    matches = find_marimo_code_fences(markdown)
    code_blocks = [match.group(2).strip() for match in matches]
    return code_blocks, matches


class MarimoPluginConfig(BaseConfig):
    enabled = OptionType(bool, default=True)
    marimo_version = OptionType(str, default=marimo.__version__)
    display_code = OptionType(bool, default=False)
    display_output = OptionType(bool, default=True)
    is_reactive = OptionType(bool, default=True)


class MarimoPlugin(BasePlugin[MarimoPluginConfig]):
    replacements: dict[str, list[str]] = {}

    def __init__(self):
        super().__init__()
        if isinstance(self.config, dict):
            plugin_config = MarimoPluginConfig()
            plugin_config.load_dict(self.config)
            self.config = plugin_config

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        if not self.config.enabled:
            return config

        return config

    def handle_marimo_file(self, page: Page) -> str:
        if page.abs_url is None:
            raise ValueError("Page has no abs_url")
        generator = marimo.MarimoIslandGenerator.from_file(page.abs_url, display_code=False)
        return generator.render_html()

    def on_page_markdown(
        self, markdown: str, /, *, page: Page, config: MkDocsConfig, files: Any
    ) -> str:
        if not self.config.enabled:
            return markdown

        del files

        if (
            page.abs_url is not None
            and os.path.exists(page.abs_url)
            and _is_marimo_file(page.abs_url)
        ):
            return self.handle_marimo_file(page)

        log.info("[marimo] on_page_markdown " + str(page.abs_url))

        # Process !marimo_file directives
        markdown = self.process_marimo_file_directives(markdown, page, config)

        if page.abs_url is None:
            return markdown

        generator = marimo.MarimoIslandGenerator()
        replacements: list[str] = []
        self.replacements[page.abs_url] = replacements
        outputs: list[Any] = []
        code_blocks, matches = collect_marimo_code(markdown)

        for code in code_blocks:
            outputs.append(generator.add_code(code))

        asyncio.run(generator.build())

        def match_equal(first: re.Match[str], second: re.Match[str]) -> bool:
            return first.start() == second.start() and first.end() == second.end()

        def marimo_repl(match: re.Match[str], outputs: list[Any]) -> str:
            if is_inside_four_backticks(markdown, match.start()):
                return match.group(0)

            # Get default options from plugin config
            default_options = {
                "display_code": self.config.display_code,
                "display_output": self.config.display_output,
                "is_reactive": self.config.is_reactive,
            }

            # Parse options from the code fence
            fence_options = self.parse_options(match.group(1))

            # Merge default options with fence options, giving priority to fence options
            options = {**default_options, **fence_options}

            index = next(i for i, m in enumerate(matches) if match_equal(m, match))
            output = outputs[index]

            # Filter out unsupported kwargs by inspecting the render method
            import inspect

            supported_kwargs = {}
            render_params = inspect.signature(output.render).parameters

            for key, value in options.items():
                if key in render_params:
                    supported_kwargs[key] = value
                else:
                    log.warning(f"[marimo] Unsupported option '{key}' for render method. Ignoring.")

            html = output.render(**supported_kwargs)
            minified_html = htmlmin.minify(str(html), remove_empty_space=True)
            replacements.append(minified_html)
            return f"<marimo-internal-island idx='{index}'/>"

        return CODE_FENCE_REGEX.sub(lambda m: marimo_repl(m, outputs), markdown)

    def process_marimo_file_directives(
        self, markdown: str, page: Page, config: MkDocsConfig
    ) -> str:
        def replace_marimo_file(match: re.Match[str]) -> str:
            file_path = match.group(1).strip()
            full_path = self.resolve_marimo_file_path(file_path, page, config.docs_dir)
            if full_path and os.path.exists(full_path):
                return self.generate_marimo_body(full_path)
            else:
                log.warning(f"marimo file not found: {file_path}")
                return f"""
!!! warning

    The marimo file `{full_path}` could not be found.
"""

        pattern = r"!marimo_file\s+(.+)"
        return re.sub(pattern, replace_marimo_file, markdown)

    def resolve_marimo_file_path(self, file_path: str, page: Page, docs_dir: str) -> str:
        if file_path.startswith("/"):
            # Treat as absolute path from the docs_dir
            return os.path.normpath(os.path.join(docs_dir, file_path[1:]))
        elif page.file.abs_src_path:
            # Relative path, resolve from the current page's directory
            base_dir = os.path.dirname(page.file.abs_src_path)
            return os.path.normpath(os.path.join(base_dir, file_path))
        return ""

    def generate_marimo_body(self, file_path: str) -> str:
        generator = marimo.MarimoIslandGenerator.from_file(file_path, display_code=False)
        return generator.render_body(include_init_island=True)

    def on_post_page(self, output: str, /, *, page: Page, config: MkDocsConfig) -> str:
        if not self.config.enabled:
            return output

        if page.abs_url is None:
            return output

        log.info("[marimo] on_post_page " + str(page.abs_url))
        generator = marimo.MarimoIslandGenerator()
        header = generator.render_head()

        # Add the extra header to the output
        output = output.replace("</head>", f"{header}\n</head>")

        replacesments: list[str] = self.replacements.get(page.abs_url, [])
        for idx, replacement in enumerate(replacesments):
            output = output.replace(f"<marimo-internal-island idx='{idx}'/>", replacement, 1)
        return output

    def parse_options(self, options_string: str) -> Dict[str, Any]:
        options: dict[str, Any] = {}
        for option in options_string.split():
            if "=" in option:
                key, value = option.split("=", 1)
                options[key.strip()] = self.parse_value(value.strip())
            else:
                options[option.strip()] = True
        return options

    def parse_value(self, value: str) -> Any:
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif value.isdigit():
            return int(value)
        elif value.replace(".", "", 1).isdigit():
            return float(value)
        else:
            return value

    def on_files(self, files: Files, config: MkDocsConfig) -> Files:
        # Process Python files in navigation
        nav = config.nav
        if nav is not None:
            self.process_nav_items(nav, files, config)
        return files

    def process_nav_items(self, items: list[Any], files: Files, config: MkDocsConfig) -> None:
        for item in items:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, list):
                        self.process_nav_items(value, files, config)
                    elif isinstance(value, str) and value.endswith(".py"):
                        self.process_python_file(value, files, config)
                        # Update the navigation to point to the virtual markdown file
                        item[key] = value[:-3] + ".md"

    def process_python_file(self, file_path: str, files: Files, config: MkDocsConfig) -> None:
        abs_src_path = os.path.join(config.docs_dir, file_path)
        if os.path.exists(abs_src_path) and _is_marimo_file(abs_src_path):
            # Create a virtual markdown file
            md_path = file_path[:-3] + ".md"
            md_content = f"!marimo_file /{file_path}"

            # Create a virtual File object
            virtual_file = VirtualFile(
                path=md_path,
                src_dir=config.docs_dir,
                dest_dir=config.site_dir,
                use_directory_urls=config.use_directory_urls,
                content=md_content,
            )

            # Add the virtual markdown file to MkDocs' file collection
            files.append(virtual_file)

            # Remove the original Python file from MkDocs' file collection
            found_file = next((f for f in files if f.src_path == file_path), None)
            if found_file:
                files.remove(found_file)


class VirtualFile(File):
    def __init__(
        self, path: str, src_dir: str, dest_dir: str, use_directory_urls: bool, content: str
    ):
        super().__init__(path, src_dir, dest_dir, use_directory_urls)
        self._content = content

    def read_text(self) -> str:
        return str(self._content)

    @property
    def abs_src_path(self) -> str:
        # Return a fake path that doesn't exist on disk
        assert self.src_dir is not None
        return os.path.join(self.src_dir, "virtual", self.src_path)

    def copy_file(self, dirty: bool = False) -> None:
        # Don't copy the file, as it doesn't exist on disk
        pass


# Hooks for development
def on_startup(command: str, dirty: bool) -> None:
    log.info("[marimo][development] plugin started.")


def on_page_markdown(markdown: str, page: Any, config: MkDocsConfig, files: Any) -> str:
    log.info("[marimo][development] plugin started.")
    plugin = MarimoPlugin()
    return plugin.on_page_markdown(markdown, page=page, config=config, files=files)


def on_post_page(output: str, page: Page, config: MkDocsConfig) -> str:
    log.info("[marimo][development] plugin started.")
    plugin = MarimoPlugin()
    return plugin.on_post_page(output, page=page, config=config)


def on_files(files: Files, config: MkDocsConfig) -> Files:
    log.info("[marimo][development] plugin started.")
    plugin = MarimoPlugin()
    return plugin.on_files(files, config)


def _is_marimo_file(filepath: Optional[str]) -> bool:
    if filepath is None:
        return False

    # Handle python
    if filepath.endswith(".py"):
        with open(filepath, "rb") as file:
            return b"app = marimo.App(" in file.read()

    # Handle markdown
    if filepath.endswith(".md"):
        with open(filepath, "r") as file:
            return "marimo-version:" in file.read()

    return False
