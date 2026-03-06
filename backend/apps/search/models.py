from django.db import models
from pgvector.django import VectorField


class Document(models.Model):
    title = models.CharField(max_length=500)
    content = models.TextField()
    category = models.CharField(max_length=100, blank=True, default='')
    embedding = VectorField(dimensions=768)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'documents'

    def __str__(self):
        return self.title
