from django.db import migrations, models
import pgvector.django


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.RunSQL("CREATE EXTENSION IF NOT EXISTS vector", migrations.RunSQL.noop),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=500)),
                ('content', models.TextField()),
                ('category', models.CharField(blank=True, default='', max_length=100)),
                ('embedding', pgvector.django.VectorField(dimensions=768)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'documents'},
        ),
        # Note: IVFFlat index is omitted here — exact cosine scan is used instead.
        # For datasets over 1M rows, add: CREATE INDEX USING hnsw (embedding vector_cosine_ops)
    ]
