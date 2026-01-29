"""
Creates admin user and sample page with OLD format StreamField data.
"""

from django.db import migrations
import json
import uuid


def create_sample_page(apps, schema_editor):
    from django.db import connection
    from django.contrib.auth.hashers import make_password

    cursor = connection.cursor()

    # Create admin user
    cursor.execute("SELECT id FROM auth_user WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO auth_user
            (password, is_superuser, username, first_name, last_name, email,
             is_staff, is_active, date_joined)
            VALUES (%s, 1, 'admin', '', '', 'admin@example.com', 1, 1, datetime('now'))
        """, [make_password('admin')])

    # Get the home page (depth=2)
    cursor.execute("SELECT id, path, depth FROM wagtailcore_page WHERE depth = 2 LIMIT 1")
    home_row = cursor.fetchone()
    if not home_row:
        return
    home_id, home_path, home_depth = home_row

    # Get or create content type for RichTextPage
    cursor.execute(
        "SELECT id FROM django_content_type WHERE app_label = 'home' AND model = 'richtextpage'"
    )
    ct_row = cursor.fetchone()
    if not ct_row:
        cursor.execute(
            "INSERT INTO django_content_type (app_label, model) VALUES ('home', 'richtextpage')"
        )
        cursor.execute(
            "SELECT id FROM django_content_type WHERE app_label = 'home' AND model = 'richtextpage'"
        )
        ct_row = cursor.fetchone()
    content_type_id = ct_row[0]

    # Get default locale
    cursor.execute("SELECT id FROM wagtailcore_locale LIMIT 1")
    locale_row = cursor.fetchone()
    if not locale_row:
        return
    locale_id = locale_row[0]

    # Find next available path
    cursor.execute(
        "SELECT path FROM wagtailcore_page WHERE depth = %s ORDER BY path DESC LIMIT 1",
        [home_depth + 1]
    )
    last_child = cursor.fetchone()
    if last_child:
        next_num = int(last_child[0][-4:]) + 1
        new_path = home_path + f"{next_num:04d}"
    else:
        new_path = home_path + "0001"

    # Insert into wagtailcore_page
    translation_key = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO wagtailcore_page
        (path, depth, numchild, title, slug, live, has_unpublished_changes,
         url_path, content_type_id, locale_id, draft_title, live_revision_id,
         latest_revision_id, first_published_at, last_published_at,
         search_description, show_in_menus, seo_title, expired, locked,
         alias_of_id, owner_id, go_live_at, expire_at, locked_at, locked_by_id,
         translation_key)
        VALUES (%s, %s, 0, 'Sample Rich Text Page', 'sample-page', 1, 0,
                '/home/sample-page/', %s, %s, 'Sample Rich Text Page', NULL,
                NULL, NULL, NULL, '', 0, '', 0, 0, NULL, NULL, NULL, NULL, NULL, NULL,
                %s)
    """, [new_path, home_depth + 1, content_type_id, locale_id, translation_key])

    # Get the new page id
    cursor.execute("SELECT id FROM wagtailcore_page WHERE slug = 'sample-page'")
    page_id = cursor.fetchone()[0]

    # OLD FORMAT body data - value is just a string, NOT wrapped in ShowableBlock
    old_format_body = json.dumps([
        {
            "type": "richtext",
            "value": "<h2>Welcome to Wagtail</h2><p>This is a sample page with a <strong>RichText block</strong>.</p><p>You can edit this content in the Wagtail admin.</p>",
            "id": "legacy-001"
        }
    ])

    # Insert into home_richtextpage
    cursor.execute(
        "INSERT INTO home_richtextpage (page_ptr_id, body) VALUES (%s, %s)",
        [page_id, old_format_body]
    )

    # Update home page numchild
    cursor.execute(
        "UPDATE wagtailcore_page SET numchild = numchild + 1 WHERE id = %s",
        [home_id]
    )


def delete_sample_page(apps, schema_editor):
    from django.db import connection
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM wagtailcore_page WHERE slug = 'sample-page'")
    row = cursor.fetchone()
    if row:
        page_id = row[0]
        cursor.execute("DELETE FROM home_richtextpage WHERE page_ptr_id = %s", [page_id])
        cursor.execute("DELETE FROM wagtailcore_page WHERE id = %s", [page_id])


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
        ('wagtailcore', '0054_initial_locale'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_sample_page, delete_sample_page),
    ]
