from django.shortcuts import render
from django.db.models import Q, Avg, Count
from django.core.cache import cache
from services.models import Service, Category
from django.conf import settings
from decimal import Decimal, InvalidOperation
import json
import hashlib


def _call_claude(messages, max_tokens=400):
    """Call Claude API safely, return text or None."""
    if not getattr(settings, 'ANTHROPIC_API_KEY', ''):
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(
            api_key=settings.ANTHROPIC_API_KEY,
            timeout=5.0
        )
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            messages=messages
        )
        return msg.content[0].text.strip()
    except Exception as e:
        print(f"[Claude API] Error: {e}")
        return None


def _parse_json_response(raw):
    """Safely parse JSON from Claude response, handling markdown fences."""
    if raw is None:
        return None
    raw = raw.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    try:
        return json.loads(raw)
    except Exception:
        return None


def get_ai_suggestions(query, results_count, categories):
    """Get Claude search tips, with caching."""
    cache_key = 'ai_tips_' + hashlib.md5(query.lower().encode()).hexdigest()
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    category_names = ', '.join([c.name for c in categories])
    raw = _call_claude([{
        "role": "user",
        "content": (
            f"A user searched for '{query}' on a local services marketplace in India. "
            f"We found {results_count} results. Available categories: {category_names}. "
            f"Give 2-3 short, helpful tips (each max 15 words) to help them find what they need. "
            f"Respond ONLY with a JSON array of strings. Example: [\"tip one\", \"tip two\"]"
        )
    }], max_tokens=300)

    result = _parse_json_response(raw)
    if result and isinstance(result, list):
        cache.set(cache_key, result, timeout=3600)
        return result
    return None


def search_view(request):
    query = request.GET.get('q', '').strip()
    city = request.GET.get('city', '').strip()
    category_slug = request.GET.get('category', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort_by = request.GET.get('sort', 'recent')

    services = Service.objects.filter(is_active=True).select_related('provider', 'category').annotate(
        avg_r=Avg('reviews__rating'),
        review_cnt=Count('reviews', distinct=True)
    )

    if query:
        services = services.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(provider__username__icontains=query) |
            Q(city__icontains=query)
        )
    if city:
        services = services.filter(city__icontains=city)
    if category_slug:
        services = services.filter(category__slug=category_slug)

    # Use Decimal for price comparisons to match DecimalField precisely
    if min_price:
        try:
            services = services.filter(price__gte=Decimal(min_price))
        except InvalidOperation:
            pass
    if max_price:
        try:
            services = services.filter(price__lte=Decimal(max_price))
        except InvalidOperation:
            pass

    if sort_by == 'price_asc':
        services = services.order_by('price')
    elif sort_by == 'price_desc':
        services = services.order_by('-price')
    elif sort_by == 'rating':
        services = services.order_by('-avg_r')
    elif sort_by == 'popular':
        services = services.order_by('-views_count')
    else:
        services = services.order_by('-created_at')

    categories = Category.objects.all()
    results_count = services.count()

    ai_suggestions = None
    if query:
        ai_suggestions = get_ai_suggestions(query, results_count, categories)

    return render(request, 'search/search_results.html', {
        'services': services,
        'query': query,
        'city': city,
        'category_slug': category_slug,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
        'categories': categories,
        'results_count': results_count,
        'ai_suggestions': ai_suggestions,
    })


def ai_recommend_view(request):
    """AI-powered service recommendations page."""
    user_need = request.GET.get('need', '').strip()
    services = []

    if not user_need:
        return render(request, 'search/ai_recommend.html', {'user_need': '', 'services': []})

    cache_key = 'ai_rec_' + hashlib.md5(user_need.lower().encode()).hexdigest()
    cached_titles = cache.get(cache_key)

    try:
        if cached_titles is not None:
            recommended_titles = cached_titles
        elif getattr(settings, 'ANTHROPIC_API_KEY', ''):
            # Fetch only title + category for the prompt — reduces token cost significantly
            all_services = Service.objects.filter(is_active=True).values(
                'title', 'category__name', 'city'
            )[:60]
            service_list = json.dumps(list(all_services), default=str)

            raw = _call_claude([{
                "role": "user",
                "content": (
                    f"User in India needs: '{user_need}'. "
                    f"Available services (JSON): {service_list}. "
                    f"Find the top 4 most relevant services from the list that could help this user. "
                    f"Consider synonyms, related skills, and partial matches. "
                    f"Return ONLY titles that exist EXACTLY as written in the list above. "
                    f"Respond ONLY with a JSON array of title strings. No other text. "
                    f"Example: [\"title1\", \"title2\"]"
                )
            }], max_tokens=500)

            recommended_titles = _parse_json_response(raw) or []
            if isinstance(recommended_titles, list) and recommended_titles:
                cache.set(cache_key, recommended_titles, timeout=1800)
        else:
            recommended_titles = []

        if recommended_titles:
            services = list(Service.objects.filter(
                title__in=recommended_titles, is_active=True
            ).select_related('provider', 'category'))
            order_map = {t: i for i, t in enumerate(recommended_titles)}
            services.sort(key=lambda s: order_map.get(s.title, 99))

        # Keyword fallback if AI returned nothing or is not configured
        if not services:
            words = user_need.lower().split()
            q = Q()
            for word in words:
                if len(word) > 3:
                    q |= (
                        Q(title__icontains=word) |
                        Q(description__icontains=word) |
                        Q(category__name__icontains=word) |
                        Q(city__icontains=word)
                    )
            if q:
                services = list(
                    Service.objects.filter(is_active=True).filter(q)
                    .select_related('provider', 'category')[:6]
                )

    except Exception as e:
        print(f"[AI Recommend] Error: {e}")
        words = user_need.lower().split()
        q = Q()
        for word in words:
            if len(word) > 3:
                q |= (
                    Q(title__icontains=word) |
                    Q(description__icontains=word) |
                    Q(category__name__icontains=word) |
                    Q(city__icontains=word)
                )
        if q:
            try:
                services = list(
                    Service.objects.filter(is_active=True).filter(q)
                    .select_related('provider', 'category')[:6]
                )
            except Exception:
                services = []

    return render(request, 'search/ai_recommend.html', {
        'user_need': user_need,
        'services': services,
    })
