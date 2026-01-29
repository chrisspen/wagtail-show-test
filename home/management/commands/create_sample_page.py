import json
from django.core.management.base import BaseCommand
from django.db import connection
from wagtail.models import Page

from home.models import RichTextPage


class Command(BaseCommand):
    help = "Creates a sample RichTextPage with OLD format data (before ShowableBlock)"

    def handle(self, *args, **options):
        # Get the root page (home)
        try:
            root_page = Page.objects.get(depth=1)
        except Page.DoesNotExist:
            self.stderr.write("No root page found. Run migrations first.")
            return

        # Check if sample page already exists
        if RichTextPage.objects.filter(slug="sample-page").exists():
            self.stdout.write(self.style.WARNING("Sample page already exists."))
            return

        # Get or create a site root
        try:
            home = Page.objects.get(depth=2)
        except Page.DoesNotExist:
            # Create a basic home page
            home = Page(title="Home", slug="home")
            root_page.add_child(instance=home)
            home.save_revision().publish()

        # Create the sample RichTextPage with empty body first
        sample_page = RichTextPage(
            title="Sample Rich Text Page",
            slug="sample-page",
            body=[],
        )

        home.add_child(instance=sample_page)
        sample_page.save_revision().publish()

        # Now update the body with OLD format data directly in the database
        old_format_body = json.dumps([
            {
                "type": "richtext",
                "value": "<h2>Welcome to Wagtail</h2><p>This is a sample page with a <strong>RichText block</strong>.</p><p>You can edit this content in the Wagtail admin at <a href=\"/admin/\">/admin/</a>.</p><ul><li>Rich text formatting</li><li>Links and images</li><li>Lists and headings</li></ul>",
                "id": "legacy-001",
            }
        ])

        cursor = connection.cursor()
        cursor.execute(
            'UPDATE home_richtextpage SET body = %s WHERE page_ptr_id = %s',
            [old_format_body, sample_page.pk]
        )

        self.stdout.write(
            self.style.SUCCESS(f"Created sample page with OLD format data: {sample_page.title}")
        )
