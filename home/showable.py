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
        # Build from scratch - don't use super() which includes child blocks in kwargs
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        args = (self.child_blocks["content"],)
        kwargs = {}
        if self.meta.label:
            kwargs["label"] = self.meta.label
        if self.meta.icon != "placeholder":
            kwargs["icon"] = self.meta.icon
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
