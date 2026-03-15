from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """Extended user model with avatar and role"""
    ROLE_CHOICES = [('user', 'User'), ('admin', 'Admin')]
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return self.username


class Category(models.Model):
    """Dish categories e.g. Chinese, Italian"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Item(models.Model):
    """A dish/menu item"""
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_url = models.ImageField(upload_to='dishes/', blank=True, null=True)
    avg_rating = models.FloatField(default=0.0)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_hot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def update_avg_rating(self):
        """Recalculate average rating from all user ratings"""
        ratings = self.ratings.all()
        if ratings.exists():
            self.avg_rating = sum(r.rating for r in ratings) / ratings.count()
        else:
            self.avg_rating = 0.0
        self.save(update_fields=['avg_rating'])


class UserRating(models.Model):
    """A user's rating (1-5) and optional comment on a dish"""
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


class UserCollection(models.Model):
    """A user's saved/favourited dish"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='collected_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} saved {self.item.name}'


class ForumPost(models.Model):
    """A community forum post, optionally linked to a dish"""
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


class ForumReply(models.Model):
    """A reply to a forum post"""
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Reply by {self.user.username} on {self.post.title}'


class Banner(models.Model):
    """Homepage promotional banner"""
    title = models.CharField(max_length=200)
    image_url = models.ImageField(upload_to='banners/', blank=True, null=True)
    link_url = models.URLField(blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title


class SystemConfig(models.Model):
    """Key-value system configuration"""
    config_key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.config_key
