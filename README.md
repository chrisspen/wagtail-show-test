Wagtail-Show-Test
=================

Simple toy test of wrapping a "show" checkbox around any Wagtail block item field.

Data Migration
--------------

When applying `add_show()` to an existing StreamField, the database has OLD format:
```json
{"type": "richtext", "value": "<p>Hello</p>", "id": "..."}
```

But the code now expects NEW format:
```json
{"type": "richtext", "value": {"content": "<p>Hello</p>", "show": true}, "id": "..."}
```

You must run a data migration to convert existing data. A template is provided:

1. Copy `home/migrations/convert_to_showable.py.template` to a new migration file
2. Rename it with the next migration number (e.g., `0003_convert_body_to_showable.py`)
3. Update the `dependencies` to point to your previous migration
4. Update the `make_showable_converter()` calls with your app, model, and field names
5. Run `python manage.py migrate`

The template handles both forward and reverse migrations.

Custom Template Tag
-------------------

If your templates access `block.value` directly (e.g., `{{ block.value|richtext }}`), you need to patch the `richtext` filter to handle `StructValue`:

```python
from wagtail.blocks import StructValue

def myrichtext(value):
    if isinstance(value, StructValue):
        if not value.get("show", True):
            return mark_safe("")
        value = value.get("content")
    # ... rest of your richtext logic
```
