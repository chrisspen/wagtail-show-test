from django.db import models

from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.blocks import RichTextBlock
from wagtail.admin.panels import FieldPanel


class RichTextPage(Page):
    """A page with a StreamField containing RichText blocks."""

    body = StreamField(
        [
            ("richtext", RichTextBlock()),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]
