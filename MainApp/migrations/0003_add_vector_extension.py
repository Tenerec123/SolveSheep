from django.db import migrations
from pgvector.django import VectorExtension

class Migration(migrations.Migration):
    dependencies = [
        ('MainApp', '0002_alter_bundle_slug_alter_bundle_title_and_more'), # El nombre de tu migración anterior
    ]

    operations = [
        VectorExtension()
    ]