from django.urls import path
from . import views

urlpatterns = [
    # Auth - register, login, logout
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dishes - list and detail pages
    path('dishes/', views.dishes_view, name='dishes'),
    path('dishes/<int:pk>/', views.dish_detail_view, name='dish_detail'),

    # Recommendations page (login required)
    path('recommendations/', views.recommendations_view, name='recommendations'),

    # User profile page (login required)
    path('profile/', views.profile_view, name='profile'),

    # Forum - list, create post, and post detail
    path('forum/', views.forum_view, name='forum'),
    path('forum/post/', views.create_post_view, name='create_post'),
    path('forum/<int:pk>/', views.post_detail_view, name='post_detail'),

    # About
    path('about/', views.about_view, name='about'),

    # AJAX endpoints - no page reload needed
    path('ajax/collect/<int:pk>/', views.toggle_collection, name='toggle_collection'),
    path('ajax/rate/<int:pk>/', views.rate_dish_ajax, name='rate_dish_ajax'),
    path('ajax/search/', views.search_ajax, name='search_ajax'),
]
