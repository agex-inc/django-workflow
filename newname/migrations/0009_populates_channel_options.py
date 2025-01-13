from django.db import migrations

def add_channel_elements(apps, schema_editor):
    schema_editor.execute(
        "INSERT INTO newname_channel (name, template) VALUES ('SMS', 'Your SMS template here');"
    )
    schema_editor.execute(
        "INSERT INTO newname_channel (name, template) VALUES ('Email', 'Your Email template here');"
    )
    schema_editor.execute(
        "INSERT INTO newname_channel (name, template) VALUES ('Internal', 'Your Internal template here');"
    )

class Migration(migrations.Migration):
    dependencies = [
        ("newname", "0008_alter_channel_options"),
    ]

    operations = [
        migrations.RunPython(add_channel_elements),
    ]
