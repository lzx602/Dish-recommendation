from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg, Count
from django.views.decorators.http import require_POST
import json

from .models import User, Category, Item, UserRating, UserCollection, ForumPost, ForumReply, Banner
from .forms import RegisterForm, LoginForm, RatingForm, ForumPostForm, ForumReplyForm, ProfileForm

def get_recommendations(user, limit=8):
    user_ratings = UserRating.objects.filter(user=user)
    if user_ratings.count() < 2:
        # Cold start: return hot/top-rated items not yet rated by user
        rated_ids = user_ratings.values_list('item_id', flat=True)
        return Item.objects.exclude(id__in=rated_ids).order_by('-avg_rating', '-is_hot')[:limit]

    # Build current user's rating dict {item_id: rating}
    my_ratings = {r.item_id: r.rating for r in user_ratings}
    my_item_ids = set(my_ratings.keys())

    # Find other users who rated at least one same item
    other_user_ids = UserRating.objects.filter(
        item_id__in=my_item_ids
    ).exclude(user=user).values_list('user_id', flat=True).distinct()

    # Compute cosine-like similarity for each other user
    scores = {}  # {item_id: [weighted_ratings]}
    for other_id in other_user_ids:
        other_ratings_qs = UserRating.objects.filter(user_id=other_id)
        other_ratings = {r.item_id: r.rating for r in other_ratings_qs}

        # Dot product on shared items
        shared = my_item_ids & set(other_ratings.keys())
        if not shared:
            continue
        dot = sum(my_ratings[i] * other_ratings[i] for i in shared)
        norm_me = sum(v ** 2 for v in my_ratings.values()) ** 0.5
        norm_other = sum(v ** 2 for v in other_ratings.values()) ** 0.5
        similarity = dot / (norm_me * norm_other) if norm_me and norm_other else 0

        if similarity <= 0:
            continue

        # Collect items this user liked that I haven't rated
        for item_id, rating in other_ratings.items():
            if item_id not in my_item_ids and rating >= 3:
                scores.setdefault(item_id, []).append(similarity * rating)

    if not scores:
        rated_ids = list(my_item_ids)
        return Item.objects.exclude(id__in=rated_ids).order_by('-avg_rating')[:limit]

    # Rank by average weighted score
    ranked = sorted(scores.items(), key=lambda x: sum(x[1]) / len(x[1]), reverse=True)
    top_ids = [item_id for item_id, _ in ranked[:limit]]

    items = {item.id: item for item in Item.objects.filter(id__in=top_ids)}
    return [items[i] for i in top_ids if i in items]


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def home_view(request):
    hot_items = Item.objects.filter(is_hot=True).order_by('-avg_rating')[:6]
    new_items = Item.objects.order_by('-created_at')[:6]
    categories = Category.objects.all()
    banners = Banner.objects.filter(is_active=True)

    recommendations = []
    if request.user.is_authenticated:
        recommendations = get_recommendations(request.user, limit=4)

    context = {
        'hot_items': hot_items,
        'new_items': new_items,
        'categories': categories,
        'banners': banners,
        'recommendations': recommendations,
    }
    return render(request, 'core/home.html', context)


def dishes_view(request):
    """Dish library with search and filter (M2, M6)"""
    items = Item.objects.select_related('category').all()
    categories = Category.objects.all()

    # Search
    query = request.GET.get('q', '').strip()
    if query:
        items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        items = items.filter(category_id=category_id)

    # Sort
    sort = request.GET.get('sort', '-created_at')
    sort_options = {
        'rating': '-avg_rating',
        '-rating': 'avg_rating',
        'name': 'name',
        'newest': '-created_at',
        'price': 'price',
    }
    items = items.order_by(sort_options.get(sort, '-created_at'))

    collected_ids = set()
    if request.user.is_authenticated:
        collected_ids = set(
            UserCollection.objects.filter(user=request.user).values_list('item_id', flat=True)
        )

    context = {
        'items': items,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'sort': sort,
        'collected_ids': collected_ids,
    }
    return render(request, 'core/dishes.html', context)


def dish_detail_view(request, pk):
    """Dish detail page with rating form (M3)"""
    item = get_object_or_404(Item, pk=pk)
    ratings = item.ratings.select_related('user').order_by('-created_at')
    related_items = Item.objects.filter(category=item.category).exclude(pk=pk)[:4]

    user_rating = None
    is_collected = False
    form = RatingForm()

    if request.user.is_authenticated:
        user_rating = UserRating.objects.filter(user=request.user, item=item).first()
        is_collected = UserCollection.objects.filter(user=request.user, item=item).exists()
        if user_rating:
            form = RatingForm(instance=user_rating)

    if request.method == 'POST' and request.user.is_authenticated:
        form = RatingForm(request.POST, instance=user_rating)
        if form.is_valid():
            rating_obj = form.save(commit=False)
            rating_obj.user = request.user
            rating_obj.item = item
            rating_obj.save()
            item.update_avg_rating()
            messages.success(request, 'Your rating has been saved!')
            return redirect('dish_detail', pk=pk)

    context = {
        'item': item,
        'ratings': ratings,
        'user_rating': user_rating,
        'is_collected': is_collected,
        'form': form,
        'related_items': related_items,
        'rating_range': range(1, 6),
    }
    return render(request, 'core/dish_detail.html', context)


@login_required
def recommendations_view(request):
    """Personalised recommendations page (M5)"""
    recommended = get_recommendations(request.user, limit=12)
    user_rating_count = UserRating.objects.filter(user=request.user).count()
    context = {
        'recommended': recommended,
        'user_rating_count': user_rating_count,
    }
    return render(request, 'core/recommendations.html', context)


@login_required
def profile_view(request):
    """Personal info and rating history (M4)"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    ratings = UserRating.objects.filter(user=request.user).select_related('item').order_by('-created_at')
    collections = UserCollection.objects.filter(user=request.user).select_related('item').order_by('-created_at')

    context = {
        'form': form,
        'ratings': ratings,
        'collections': collections,
    }
    return render(request, 'core/profile.html', context)


def forum_view(request):
    """Community forum (S1)"""
    posts = ForumPost.objects.select_related('user', 'item').annotate(
        reply_count=Count('replies')
    ).order_by('-created_at')

    # Search posts
    query = request.GET.get('q', '').strip()
    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(content__icontains=query))

    form = ForumPostForm()
    context = {'posts': posts, 'form': form, 'query': query}
    return render(request, 'core/forum.html', context)


@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created!')
            return redirect('forum')
    return redirect('forum')


def post_detail_view(request, pk):
    post = get_object_or_404(ForumPost, pk=pk)
    replies = post.replies.select_related('user').order_by('created_at')
    form = ForumReplyForm()

    if request.method == 'POST' and request.user.is_authenticated:
        form = ForumReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.user = request.user
            reply.save()
            messages.success(request, 'Reply posted!')
            return redirect('post_detail', pk=pk)

    context = {'post': post, 'replies': replies, 'form': form}
    return render(request, 'core/post_detail.html', context)


def about_view(request):
    return render(request, 'core/about.html')


@login_required
@require_POST
def toggle_collection(request, pk):
    item = get_object_or_404(Item, pk=pk)
    collection, created = UserCollection.objects.get_or_create(user=request.user, item=item)
    if not created:
        collection.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'saved'})


@login_required
@require_POST
def rate_dish_ajax(request, pk):
    item = get_object_or_404(Item, pk=pk)
    try:
        data = json.loads(request.body)
        rating_value = int(data.get('rating', 0))
        comment = data.get('comment', '').strip()
    except (ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid data'}, status=400)

    if not (1 <= rating_value <= 5):
        return JsonResponse({'error': 'Rating must be 1-5'}, status=400)

    rating, created = UserRating.objects.update_or_create(
        user=request.user, item=item,
        defaults={'rating': rating_value, 'comment': comment}
    )
    item.update_avg_rating()
    return JsonResponse({
        'status': 'created' if created else 'updated',
        'avg_rating': round(item.avg_rating, 1),
        'rating_count': item.ratings.count(),
    })


@require_POST
def search_ajax(request):
    query = request.POST.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    items = Item.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    ).values('id', 'name', 'avg_rating')[:6]
    return JsonResponse({'results': list(items)})
