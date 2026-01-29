"""
Converts existing StreamField data to ShowableBlock format and alters field definition.
"""

from django.db import migrations
import json
import wagtail.blocks
import wagtail.fields
import home.showable


def convert_to_showable(apps, schema_editor):
    from django.db import connection
    cursor = connection.cursor()

    cursor.execute('SELECT page_ptr_id, body FROM home_richtextpage')
    rows = cursor.fetchall()

    for pk, field_value in rows:
        if not field_value:
            continue

        try:
            data = json.loads(field_value)
        except (json.JSONDecodeError, TypeError):
            continue

        if not isinstance(data, list):
            continue

        modified = False
        for block in data:
            if isinstance(block.get('value'), dict) and 'content' in block['value']:
                continue

            block['value'] = {
                'content': block['value'],
                'show': True
            }
            modified = True

        if modified:
            cursor.execute(
                'UPDATE home_richtextpage SET body = %s WHERE page_ptr_id = %s',
                [json.dumps(data), pk]
            )


def revert_to_old_format(apps, schema_editor):
    from django.db import connection
    cursor = connection.cursor()

    cursor.execute('SELECT page_ptr_id, body FROM home_richtextpage')
    rows = cursor.fetchall()

    for pk, field_value in rows:
        if not field_value:
            continue

        try:
            data = json.loads(field_value)
        except (json.JSONDecodeError, TypeError):
            continue

        if not isinstance(data, list):
            continue

        modified = False
        for block in data:
            if isinstance(block.get('value'), dict) and 'content' in block['value']:
                block['value'] = block['value']['content']
                modified = True

        if modified:
            cursor.execute(
                'UPDATE home_richtextpage SET body = %s WHERE page_ptr_id = %s',
                [json.dumps(data), pk]
            )


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_create_sample_page'),
    ]

    operations = [
        migrations.RunPython(convert_to_showable, revert_to_old_format),

        migrations.AlterField(
            model_name='richtextpage',
            name='body',
            field=wagtail.fields.StreamField(
                [('richtext', home.showable.ShowableBlock(wagtail.blocks.RichTextBlock()))],
                blank=True,
                use_json_field=True,
            ),
        ),
    ]
