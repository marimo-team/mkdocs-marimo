import textwrap
import urllib.parse
import xml.etree.ElementTree as etree
from typing import Any, Dict, List, Union, cast

from pymdownx.blocks import BlocksExtension  # type: ignore
from pymdownx.blocks.block import Block, type_boolean, type_string, type_string_in  # type: ignore


class BaseMarimoBlock(Block):
    """Base class for marimo embed blocks"""

    OPTIONS: Dict[str, List[Union[str, Any]]] = {
        "height": [
            "medium",
            type_string,  # Allow any string value for height (e.g. "500px", "small", etc.)
        ],
        "mode": ["read", type_string_in(["read", "edit"])],
        "include_code": [True, type_boolean],
    }

    def on_create(self, parent: etree.Element) -> etree.Element:
        container = etree.SubElement(parent, "div")
        container.set("class", "marimo-embed-container")
        return container

    def on_add(self, block: etree.Element) -> etree.Element:
        return block

    def _create_iframe(self, block: etree.Element, url: str) -> None:
        # Clear existing content
        block.text = None
        for child in block:
            block.remove(child)

        # Add iframe
        height: str = cast(str, self.options["height"])
        include_code: bool = cast(bool, self.options.get("include_code", True))
        iframe = etree.SubElement(block, "iframe")

        # Convert named sizes to pixels
        height_map = {
            "small": "300px",
            "medium": "400px",
            "large": "600px",
            "xlarge": "800px",
            "xxlarge": "1000px",
        }
        iframe_height = height_map.get(height, height)
        if not iframe_height.endswith("px"):
            iframe_height += "px"

        # Adjust URL to include include_code parameter
        url_parts = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qsl(url_parts[4]))
        query["include-code"] = str(include_code).lower()
        url_parts[4] = urllib.parse.urlencode(query)
        final_url = urllib.parse.urlunparse(url_parts)

        iframe.set("class", "marimo-embed")
        iframe.set("src", final_url)
        iframe.set(
            "allow",
            "camera; geolocation; microphone; fullscreen; autoplay; encrypted-media; picture-in-picture; clipboard-read; clipboard-write",
        )
        iframe.set("width", "100%")
        iframe.set("height", iframe_height)
        iframe.set("frameborder", "0")
        iframe.set("style", "display: block; margin: 0 auto;")

    def on_markdown(self) -> str:
        return "raw"


class MarimoEmbedBlock(BaseMarimoBlock):
    NAME: str = "marimo-embed"
    OPTIONS: Dict[str, List[Union[str, Any]]] = {
        **BaseMarimoBlock.OPTIONS,
        "app_width": ["medium", type_string_in(["medium", "full", "compact"])],
    }

    def on_end(self, block: etree.Element) -> None:
        code = block.text.strip() if block.text else ""
        if code.startswith("```python"):
            code = code[9:]
            code = code[:-3]
        code = textwrap.dedent(code)

        app_width: str = cast(str, self.options["app_width"])
        mode: str = cast(str, self.options["mode"])
        url = create_marimo_app_url(
            code=create_marimo_app_code(code=code, app_width=app_width),
            mode=mode,
        )
        self._create_iframe(block, url)


class MarimoEmbedFileBlock(BaseMarimoBlock):
    NAME: str = "marimo-embed-file"
    OPTIONS: Dict[str, List[Union[str, Any]]] = {
        **BaseMarimoBlock.OPTIONS,
        "filepath": ["", type_string],
        "show_source": ["true", type_string_in(["true", "false"])],
    }

    def on_end(self, block: etree.Element) -> None:
        filepath = cast(str, self.options["filepath"])
        if not filepath:
            raise ValueError("File path must be provided")

        # Read from project root
        try:
            with open(filepath, "r") as f:
                code = f.read()
        except FileNotFoundError:
            raise ValueError(f"File not found: {filepath}")

        mode: str = cast(str, self.options["mode"])
        url = create_marimo_app_url(code=code, mode=mode)
        self._create_iframe(block, url)

        # Add source code section if enabled
        show_source: str = cast(str, self.options.get("show_source", "true"))
        if show_source == "true":
            details = etree.SubElement(block, "details")
            summary = etree.SubElement(details, "summary")
            summary.text = f"Source code for `{filepath}`"

            copy_paste_container = etree.SubElement(details, "p")
            copy_paste_container.text = "Tip: paste this code into an empty cell, and the marimo editor will create cells for you"

            code_container = etree.SubElement(details, "pre")
            code_container.set("class", "marimo-source-code")
            code_block = etree.SubElement(code_container, "code")
            code_block.set("class", "language-python")
            code_block.text = code


def uri_encode_component(code: str) -> str:
    return urllib.parse.quote(code, safe="~()*!.'")


def create_marimo_app_code(
    *,
    code: str,
    app_width: str = "medium",
) -> str:
    header = "\n".join(
        [
            "import marimo",
            f'app = marimo.App(width="{app_width}")',
            "",
        ]
    )

    # Only add import if not already present
    if "import marimo as mo" not in code:
        header += "\n".join(
            [
                "",
                "@app.cell",
                "def __():",
                "    import marimo as mo",
                "    return",
            ]
        )
    return header + code


def create_marimo_app_url(code: str, mode: str = "read") -> str:
    encoded_code = uri_encode_component(code)
    return f"https://marimo.app/?code={encoded_code}&embed=true&mode={mode}"


class MarimoBlocksExtension(BlocksExtension):
    def extendMarkdownBlocks(self, md: Any, block_mgr: Any) -> None:
        block_mgr.register(MarimoEmbedBlock, self.getConfigs())
        block_mgr.register(MarimoEmbedFileBlock, self.getConfigs())


def makeExtension(*args: Any, **kwargs: Any) -> MarimoBlocksExtension:
    return MarimoBlocksExtension(*args, **kwargs)
