from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Category, Item, UserRating, UserCollection, ForumPost, ForumReply
from .views import get_recommendations

User = get_user_model()


class UserModelTest(TestCase):
    """Tests for the custom User model"""

    def test_create_user(self):
        user = User.objects.create_user(username='alice', password='pass1234', email='alice@example.com')
        self.assertEqual(user.username, 'alice')
        self.assertEqual(user.role, 'user')
        self.assertTrue(user.check_password('pass1234'))

    def test_user_default_role_is_user(self):
        user = User.objects.create_user(username='bob', password='pass1234')
        self.assertEqual(user.role, 'user')

    def test_user_str(self):
        user = User.objects.create_user(username='charlie', password='pass1234')
        self.assertEqual(str(user), 'charlie')


class CategoryModelTest(TestCase):
    """Tests for the Category model"""

    def test_create_category(self):
        cat = Category.objects.create(name='Chinese', description='Chinese cuisine')
        self.assertEqual(str(cat), 'Chinese')

    def test_category_ordering(self):
        Category.objects.create(name='B Cat', sort_order=2)
        Category.objects.create(name='A Cat', sort_order=1)
        cats = list(Category.objects.all())
        self.assertEqual(cats[0].name, 'A Cat')


class ItemModelTest(TestCase):
    """Tests for the Item (dish) model"""

    def setUp(self):
        self.category = Category.objects.create(name='Italian')
        self.item = Item.objects.create(
            name='Spaghetti Carbonara',
            category=self.category,
            price=12.50
        )

    def test_item_str(self):
        self.assertEqual(str(self.item), 'Spaghetti Carbonara')

    def test_item_default_avg_rating(self):
        self.assertEqual(self.item.avg_rating, 0.0)

    def test_update_avg_rating(self):
        user1 = User.objects.create_user(username='u1', password='pass1234')
        user2 = User.objects.create_user(username='u2', password='pass1234')
        UserRating.objects.create(user=user1, item=self.item, rating=4)
        UserRating.objects.create(user=user2, item=self.item, rating=2)
        self.item.update_avg_rating()
        self.assertEqual(self.item.avg_rating, 3.0)

    def test_update_avg_rating_no_ratings(self):
        self.item.update_avg_rating()
        self.assertEqual(self.item.avg_rating, 0.0)


class UserRatingModelTest(TestCase):
    """Tests for the UserRating model"""

    def setUp(self):
        self.user = User.objects.create_user(username='rater', password='pass1234')
        self.category = Category.objects.create(name='Japanese')
        self.item = Item.objects.create(name='Sushi', category=self.category)

    def test_create_rating(self):
        rating = UserRating.objects.create(user=self.user, item=self.item, rating=5, comment='Excellent!')
        self.assertEqual(rating.rating, 5)
        self.assertEqual(str(rating), 'rater rated Sushi: 5')

    def test_unique_user_item_rating(self):
        UserRating.objects.create(user=self.user, item=self.item, rating=4)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            UserRating.objects.create(user=self.user, item=self.item, rating=3)


class UserCollectionModelTest(TestCase):
    """Tests for the UserCollection (save/bookmark) model"""

    def setUp(self):
        self.user = User.objects.create_user(username='collector', password='pass1234')
        self.category = Category.objects.create(name='Mexican')
        self.item = Item.objects.create(name='Tacos', category=self.category)

    def test_create_collection(self):
        col = UserCollection.objects.create(user=self.user, item=self.item)
        self.assertEqual(str(col), 'collector saved Tacos')

    def test_unique_collection(self):
        UserCollection.objects.create(user=self.user, item=self.item)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            UserCollection.objects.create(user=self.user, item=self.item)


class ForumModelTest(TestCase):
    """Tests for ForumPost and ForumReply models"""

    def setUp(self):
        self.user = User.objects.create_user(username='poster', password='pass1234')
        self.post = ForumPost.objects.create(
            user=self.user, title='Best ramen in town', content='Tried a great place!'
        )

    def test_post_str(self):
        self.assertEqual(str(self.post), 'Best ramen in town')

    def test_create_reply(self):
        reply = ForumReply.objects.create(post=self.post, user=self.user, content='Agree!')
        self.assertIn('poster', str(reply))


class AuthViewTest(TestCase):
    """Tests for registration and login views"""

    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Log In')

    def test_register_creates_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'TestPass@123',
            'password2': 'TestPass@123',
        })
        self.assertEqual(response.status_code, 302)  # redirect after success
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_valid_user(self):
        User.objects.create_user(username='loginuser', password='TestPass@123')
        response = self.client.post(reverse('login'), {
            'username': 'loginuser',
            'password': 'TestPass@123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'nobody',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)  # stays on login page


class DishViewTest(TestCase):
    """Tests for dish listing and detail views"""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Thai')
        self.item = Item.objects.create(name='Pad Thai', category=self.category, price=10.00)

    def test_dishes_page_loads(self):
        response = self.client.get(reverse('dishes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pad Thai')

    def test_dish_detail_loads(self):
        response = self.client.get(reverse('dish_detail', args=[self.item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pad Thai')

    def test_dish_search(self):
        Item.objects.create(name='Tom Yum Soup', category=self.category)
        response = self.client.get(reverse('dishes') + '?q=Tom')
        self.assertContains(response, 'Tom Yum Soup')
        self.assertNotContains(response, 'Pad Thai')

    def test_dish_filter_by_category(self):
        other_cat = Category.objects.create(name='Indian')
        Item.objects.create(name='Curry', category=other_cat)
        response = self.client.get(reverse('dishes') + f'?category={self.category.pk}')
        self.assertContains(response, 'Pad Thai')
        self.assertNotContains(response, 'Curry')


class ProfileViewTest(TestCase):
    """Tests for the profile page (requires login)"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='profuser', password='pass1234')

    def test_profile_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, '/login/?next=/profile/')

    def test_profile_loads_when_logged_in(self):
        self.client.login(username='profuser', password='pass1234')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'profuser')


class RecommendationEngineTest(TestCase):
    """Tests for the collaborative filtering recommendation engine"""

    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.user_a = User.objects.create_user(username='user_a', password='pass')
        self.user_b = User.objects.create_user(username='user_b', password='pass')
        self.items = [
            Item.objects.create(name=f'Dish {i}', category=self.category)
            for i in range(6)
        ]

    def test_cold_start_returns_top_rated(self):
        """User with <2 ratings gets top-rated fallback"""
        self.items[0].avg_rating = 4.5
        self.items[0].save()
        results = get_recommendations(self.user_a, limit=3)
        self.assertIsNotNone(results)

    def test_recommendations_exclude_already_rated(self):
        """Recommended items should not include already-rated items"""
        # user_a rates items 0-2
        for i in range(3):
            UserRating.objects.create(user=self.user_a, item=self.items[i], rating=4)
        # user_b rates items 0-2 similarly + item 3 highly
        for i in range(3):
            UserRating.objects.create(user=self.user_b, item=self.items[i], rating=4)
        UserRating.objects.create(user=self.user_b, item=self.items[3], rating=5)

        results = get_recommendations(self.user_a, limit=6)
        result_ids = [item.id for item in results]
        rated_ids = [self.items[i].id for i in range(3)]
        for rid in rated_ids:
            self.assertNotIn(rid, result_ids)

    def test_recommendations_returns_list(self):
        """get_recommendations always returns a list-like object"""
        results = get_recommendations(self.user_a, limit=5)
        self.assertIsNotNone(results)


class AjaxViewTest(TestCase):
    """Tests for AJAX endpoints"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='ajaxuser', password='pass1234')
        self.category = Category.objects.create(name='Ajax Cat')
        self.item = Item.objects.create(name='Ajax Dish', category=self.category)
        self.client.login(username='ajaxuser', password='pass1234')

    def test_toggle_collection_saves(self):
        response = self.client.post(
            reverse('toggle_collection', args=[self.item.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        import json
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'saved')

    def test_toggle_collection_removes(self):
        UserCollection.objects.create(user=self.user, item=self.item)
        response = self.client.post(reverse('toggle_collection', args=[self.item.pk]))
        import json
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'removed')

    def test_rate_dish_ajax(self):
        import json
        response = self.client.post(
            reverse('rate_dish_ajax', args=[self.item.pk]),
            data=json.dumps({'rating': 4, 'comment': 'Good!'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn(data['status'], ['created', 'updated'])
        self.assertEqual(data['avg_rating'], 4.0)

    def test_rate_dish_invalid_rating(self):
        import json
        response = self.client.post(
            reverse('rate_dish_ajax', args=[self.item.pk]),
            data=json.dumps({'rating': 99}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
