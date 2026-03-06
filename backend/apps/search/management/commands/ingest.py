import json
from pathlib import Path
from django.core.management.base import BaseCommand
from search.models import Document
from search.embeddings import generate_embedding


class Command(BaseCommand):
    help = 'Load documents from JSON and generate embeddings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=str(Path(__file__).resolve().parent.parent.parent.parent.parent.parent / 'data' / 'documents.json'),
            help='Path to documents JSON file',
        )

    def handle(self, *args, **options):
        filepath = options['file']
        with open(filepath) as f:
            docs = json.load(f)

        self.stdout.write(f"Loading {len(docs)} documents...")

        for i, doc in enumerate(docs, 1):
            title = doc['title']
            content = doc['content']
            category = doc.get('category', '')

            if Document.objects.filter(title=title).exists():
                self.stdout.write(f"  [{i}] Skipping (exists): {title}")
                continue

            embedding = generate_embedding(f"{title} {content}")
            Document.objects.create(
                title=title,
                content=content,
                category=category,
                embedding=embedding,
            )
            self.stdout.write(f"  [{i}] Ingested: {title}")

        total = Document.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Done. {total} documents in database."))
