# Generated migration for adding docs_url field to TemplateModel

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("svs_core", "0002_usergroupmodel"),
    ]

    operations = [
        migrations.AddField(
            model_name="templatemodel",
            name="docs_url",
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
