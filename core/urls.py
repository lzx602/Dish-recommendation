from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dishes
    path('dishes/', views.dishes_view, name='dishes'),
    path('dishes/<int:pk>/', views.dish_detail_view, name='dish_detail'),

    # Recommendations
    path('recommendations/', views.recommendations_view, name='recommendations'),

    # Profile
    path('profile/', views.profile_view, name='profile'),

    # Forum
    path('forum/', views.forum_view, name='forum'),
    path('forum/post/', views.create_post_view, name='create_post'),
    path('forum/<int:pk>/', views.post_detail_view, name='post_detail'),

    # About
    path('about/', views.about_view, name='about'),

    # AJAX
    path('ajax/collect/<int:pk>/', views.toggle_collection, name='toggle_collection'),
    path('ajax/rate/<int:pk>/', views.rate_dish_ajax, name='rate_dish_ajax'),
    path('ajax/search/', views.search_ajax, name='search_ajax'),
]
