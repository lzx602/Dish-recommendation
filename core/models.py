from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# Custom user model, adds avatar and role on top of Django's default User
class User(AbstractUser):
    ROLE_CHOICES = [('user', 'User'), ('admin', 'Admin')]
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return self.username

# Dish category
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name'] # Sort by sort_order first, then name
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

# Dish item
class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_url = models.ImageField(upload_to='dishes/', blank=True, null=True)
    avg_rating = models.FloatField(default=0.0) # Recalculated every time a rating is submitted
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_hot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def update_avg_rating(self): # Recalculate and save the average rating from all user ratings
        ratings = self.ratings.all()
        if ratings.exists():
            self.avg_rating = sum(r.rating for r in ratings) / ratings.count()
        else:
            self.avg_rating = 0.0
        self.save(update_fields=['avg_rating'])

# User rating for a dish, one rating per user per dish
class UserRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'item')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} rated {self.item.name}: {self.rating}'

# User saved dish collection
class UserCollection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='collected_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item') # Can't save the same dish twice
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} saved {self.item.name}'

# Forum post, optionally linked to a dish
class ForumPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

# Reply to a forum post
class ForumReply(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Replies shown oldest first

    def __str__(self):
        return f'Reply by {self.user.username} on {self.post.title}'

# Homepage banner image
class Banner(models.Model):
    title = models.CharField(max_length=200)
    image_url = models.ImageField(upload_to='banners/', blank=True, null=True)
    link_url = models.URLField(blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True) # Only active banners are displayed

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title

# Key-value store for system settings
class SystemConfig(models.Model):
    config_key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.config_key
