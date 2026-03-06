import time
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

    cached = get_cached(query, 'keyword')
    if cached:
        return Response({'results': cached, 'cached': True})

    start = time.time()
    docs = Document.objects.filter(
        content__icontains=query
    ).values('id', 'title', 'content', 'category')[:10]

    results = []
    for doc in docs:
        results.append({
            'id': doc['id'],
            'title': doc['title'],
            'content': doc['content'][:300],
            'category': doc['category'],
        })

    elapsed = round((time.time() - start) * 1000)
    set_cached(query, 'keyword', results)
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
