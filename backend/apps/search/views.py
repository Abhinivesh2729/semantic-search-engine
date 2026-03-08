import time
from django.db.models import Case, IntegerField, Q, Value, When
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pgvector.django import CosineDistance
from .models import Document
from .embeddings import generate_embedding
from .cache import get_cached, set_cached


@api_view(['GET'])
def keyword_search(request):
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({'error': 'Query parameter q is required'}, status=400)

    cache_key = 'keyword_v2'
    cached = get_cached(query, cache_key)
    if cached:
        return Response({'results': cached, 'cached': True})

    start = time.time()
    docs = Document.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query)
    ).annotate(
        match_priority=Case(
            When(title__iexact=query, then=Value(0)),
            When(title__icontains=query, then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )
    ).order_by('match_priority', 'title').values('id', 'title', 'content', 'category')[:10]

    results = []
    for doc in docs:
        results.append({
            'id': doc['id'],
            'title': doc['title'],
            'content': doc['content'][:300],
            'category': doc['category'],
        })

    elapsed = round((time.time() - start) * 1000)
    set_cached(query, cache_key, results)
    return Response({'results': results, 'cached': False, 'time_ms': elapsed})


@api_view(['GET'])
def semantic_search(request):
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({'error': 'Query parameter q is required'}, status=400)

    cached = get_cached(query, 'semantic')
    if cached:
        return Response({'results': cached, 'cached': True})

    start = time.time()
    query_embedding = generate_embedding(query)

    docs = Document.objects.annotate(
        distance=CosineDistance('embedding', query_embedding)
    ).order_by('distance')[:5]

    results = []
    for doc in docs:
        similarity = round(1 - doc.distance, 4)
        results.append({
            'id': doc.id,
            'title': doc.title,
            'content': doc.content[:300],
            'category': doc.category,
            'similarity': similarity,
        })

    elapsed = round((time.time() - start) * 1000)
    set_cached(query, 'semantic', results)
    return Response({'results': results, 'cached': False, 'time_ms': elapsed})
