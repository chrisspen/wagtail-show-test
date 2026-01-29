from wagtail.blocks import StructBlock, BooleanBlock
from wagtail.rich_text import RichText


class ShowableString(str):
    """A string that also carries show/content attributes for ShowableBlock."""

    def __new__(cls, content, show=True):
        text = content if show and content else ""
        instance = super().__new__(cls, text)
        instance.show = show
        instance.content = content
        return instance


class ShowableBlock(StructBlock):
    """
    Wrapper that adds a show/hide toggle to any block.
    """

    def __init__(self, child_block, **kwargs):
        super().__init__(
            [
                ("content", child_block),
                ("show", BooleanBlock(default=True, required=False, label="Show")),
            ],
            **kwargs
        )

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        # Pass the original child block as the first positional arg
        args = (self.child_blocks["content"],)
        # Remove 'content' and 'show' from kwargs since they're dynamic
        kwargs.pop("content", None)
        kwargs.pop("show", None)
        return path, args, kwargs

    def to_python(self, value):
        if value is None:
            return None

        # Old format: value is not a dict, pass through to child block unchanged
        if not isinstance(value, dict):
            return self.child_blocks["content"].to_python(value)

        # New format: extract content and show
        struct_value = super().to_python(value)
        content = struct_value.get("content")
        show = struct_value.get("show", True)

        if not show:
            return ShowableString("", show=False)

        if isinstance(content, str):
            return ShowableString(content, show)

        if isinstance(content, RichText):
            return ShowableString(content.source, show)

        # Non-string blocks: return struct_value as-is
        return struct_value

    def render(self, value, context=None):
        # Handle ShowableString (from RichText/string blocks)
        if isinstance(value, ShowableString):
            if not value.show:
                return ""
            # Wrap back in RichText for proper rendering
            content = RichText(value.content) if value.content else value.content
            return self.child_blocks["content"].render(content, context=context)

        # Handle StructValue (for non-string blocks)
        if not value.get("show", True):
            return ""
        content = value.get("content")
        return self.child_blocks["content"].render(content, context=context)



def add_show(block_list):
    """
    Wrap a list of StreamField block definitions to add show/hide toggles.

    Usage:
        from home.showable import add_show

        body = StreamField(add_show([
            ('richtext', RichTextBlock()),
            ('image', ImageChooserBlock()),
        ]))

    Each block will get a "Show" checkbox that defaults to checked.
    When unchecked, that block won't render on the live site.
    """
    return [(name, ShowableBlock(block)) for name, block in block_list]
