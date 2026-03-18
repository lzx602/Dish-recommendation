from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Category, Item, UserRating, UserCollection, ForumPost, ForumReply, Banner, SystemConfig

# User admin, extends default UserAdmin with avatar and role fields
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {'fields': ('avatar', 'role')}),
    )

# Category admin, ordered by sort_order
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order', 'description')
    ordering = ('sort_order',)

# Item admin, supports search and inline editing of is_hot and price
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'avg_rating', 'price', 'is_hot', 'created_at')
    list_filter = ('category', 'is_hot')
    search_fields = ('name', 'description')
    list_editable = ('is_hot', 'price')

# User rating admin
@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username', 'item__name')

# User collection admin
@admin.register(UserCollection)
class UserCollectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'created_at')

# Forum post admin
@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'likes_count', 'created_at')
    search_fields = ('title', 'content')

# Forum reply admin
@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')

# Banner admin, sort_order and is_active can be edited in list view
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')

# System config admin
@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('config_key', 'value', 'description')
