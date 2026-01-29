from wagtail.blocks import StructBlock, BooleanBlock


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

        # Old format: value is not a dict, wrap it in new format
        if not isinstance(value, dict):
            value = {"content": value, "show": True}

        return super().to_python(value)

    def render(self, value, context=None):
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
