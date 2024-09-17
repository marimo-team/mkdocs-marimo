import asyncio
import logging
import re
from typing import Any

import htmlmin
import marimo
from mkdocs.config.config_options import Type as OptionType
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page

log = logging.getLogger("mkdocs.plugins.marimo")

CODE_FENCE_REGEX = re.compile(r"```marimo(-\w+)?\n([\s\S]+?)```", flags=re.MULTILINE)


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


OPTIONS = {
    "-display_code",
    "-display_output",
    "-is_reactive",
}


def collect_marimo_code(markdown: str) -> tuple[list[str], list[re.Match[str]]]:
    matches = find_marimo_code_fences(markdown)
    code_blocks = [match.group(2).strip() for match in matches]
    return code_blocks, matches


class MarimoPluginConfig(MkDocsConfig):
    enabled = OptionType(bool, default=True)
    marimo_version = OptionType(str, default=marimo.__version__)


class MarimoPlugin(BasePlugin[MarimoPluginConfig]):
    version = "0.1.0"

    replacements: dict[str, list[str]] = {}

    def __init__(self):
        super().__init__()

    def on_page_markdown(
        self, markdown: str, /, *, page: Page, config: MkDocsConfig, files: Any
    ) -> str:
        del files

        if not page.abs_url:
            return markdown

        log.info("[marimo] on_page_markdown " + page.abs_url)
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
            options = match.group(1)
            index = next(i for i, m in enumerate(matches) if match_equal(m, match))
            output = outputs[index]
            html = output.render()
            minified_html: str = htmlmin.minify(str(html), remove_empty_space=True)
            replacements.append(minified_html)
            return f"<marimo-internal-island idx='{index}'/>"

        return CODE_FENCE_REGEX.sub(lambda m: marimo_repl(m, outputs), markdown)

    def on_post_page(self, output: str, /, *, page: Page, config: MkDocsConfig) -> str:
        log.info("[marimo] on_post_page " + page.abs_url)
        generator = marimo.MarimoIslandGenerator()
        header = generator.render_head()

        # Add the extra header to the output
        output = output.replace("</head>", f"{header}\n</head>")
        output = output.replace(
            "<marimo-filename hidden></>", "<marimo-filename hidden></marimo-filename>"
        )

        replacesments: list[str] = self.replacements.get(page.abs_url, [])
        for idx, replacement in enumerate(replacesments):
            output = output.replace(f"<marimo-internal-island idx='{idx}'/>", replacement, 1)
        return output


# Hooks for development
def on_startup(command: str, dirty: bool) -> None:
    log.info("[marimo][development] plugin started.")


def on_page_markdown(markdown: str, page: Any, config: MkDocsConfig, files: Any) -> str:
    log.info("[marimo][development] plugin started.")
    md = MarimoPlugin().on_page_markdown(markdown, page=page, config=config, files=files)
    return md


def on_post_page(output: str, page: Page, config: MkDocsConfig) -> str:
    log.info("[marimo][development] plugin started.")
    return MarimoPlugin().on_post_page(output, page=page, config=config)
