from wagtail.blocks import StructBlock, BooleanBlock


class ShowableBlock(StructBlock):
    """
    Wrapper that adds a show/hide toggle to any block.

    When 'show' is unchecked, the block will not render on the live site.
    The checkbox appears below the wrapped block's widget in admin.
    """

    def __init__(self, child_block, **kwargs):
        super().__init__(
            [
                ("content", child_block),
                ("show", BooleanBlock(default=True, required=False, label="Show")),
            ],
            **kwargs
        )

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
