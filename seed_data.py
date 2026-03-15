"""
Run this script to populate the database with sample data:
    python manage.py shell < seed_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dish_recommendation.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Category, Item, UserRating, ForumPost, Banner, SystemConfig

User = get_user_model()

print("Seeding database...")

# ── Superuser ──────────────────────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("  Created superuser: admin / admin123")

# ── Sample users ───────────────────────────────────────────────────────────
users = []
for name in ['alice', 'bob', 'carol', 'dave']:
    u, created = User.objects.get_or_create(username=name, defaults={
        'email': f'{name}@example.com', 'role': 'user'
    })
    if created:
        u.set_password('pass1234')
        u.save()
    users.append(u)
    if created:
        print(f"  Created user: {name} / pass1234")

# ── Categories ─────────────────────────────────────────────────────────────
categories_data = [
    ('Chinese',    'Traditional and modern Chinese cuisine', '🍜', 1),
    ('Italian',    'Pasta, pizza, and more',                 '🍕', 2),
    ('Japanese',   'Sushi, ramen, and Japanese delicacies',  '🍣', 3),
    ('Mexican',    'Tacos, burritos, and spicy favourites',  '🌮', 4),
    ('Indian',     'Rich curries and aromatic dishes',       '🍛', 5),
    ('Thai',       'Fresh and flavourful Thai dishes',       '🌶️', 6),
    ('Desserts',   'Sweet treats and confections',           '🍰', 7),
    ('Fast Food',  'Quick and satisfying bites',             '🍔', 8),
]
category_objs = {}
for name, desc, icon, order in categories_data:
    cat, _ = Category.objects.get_or_create(name=name, defaults={
        'description': desc, 'icon': icon, 'sort_order': order
    })
    category_objs[name] = cat
print(f"  Created {len(category_objs)} categories")

# ── Dishes ─────────────────────────────────────────────────────────────────
dishes_data = [
    # (name, category, description, price, is_hot)
    ('Kung Pao Chicken',    'Chinese',  'Spicy stir-fried chicken with peanuts and chillies.',        12.50, True),
    ('Peking Duck',         'Chinese',  'Crispy roasted duck served with pancakes and hoisin sauce.', 22.00, True),
    ('Mapo Tofu',           'Chinese',  'Silken tofu in a spicy, numbing Sichuan sauce.',             10.00, False),
    ('Hot Pot',             'Chinese',  'Communal simmering broth with meats and vegetables.',        18.00, True),
    ('Spaghetti Carbonara', 'Italian',  'Creamy pasta with pancetta, egg, and Parmesan.',             13.00, False),
    ('Margherita Pizza',    'Italian',  'Classic tomato, mozzarella, and fresh basil pizza.',         11.00, True),
    ('Risotto ai Funghi',   'Italian',  'Creamy Arborio rice with wild mushrooms.',                   14.00, False),
    ('Tiramisu',            'Desserts', 'Classic Italian coffee-flavoured dessert.',                   7.50, True),
    ('Sushi Platter',       'Japanese', 'Assorted fresh nigiri and maki rolls.',                      20.00, True),
    ('Tonkotsu Ramen',      'Japanese', 'Rich pork broth with noodles, chashu, and soft-boiled egg.', 14.00, True),
    ('Tempura Udon',        'Japanese', 'Thick udon noodles in dashi broth with crispy tempura.',    13.50, False),
    ('Chicken Tacos',       'Mexican',  'Grilled chicken in corn tortillas with salsa and guac.',     10.00, False),
    ('Beef Burrito',        'Mexican',  'Flour tortilla filled with rice, beans, beef, and cheese.',  11.50, True),
    ('Butter Chicken',      'Indian',   'Tender chicken in a rich, creamy tomato-based curry.',       13.00, True),
    ('Palak Paneer',        'Indian',   'Fresh spinach curry with soft paneer cheese.',               11.00, False),
    ('Pad Thai',            'Thai',     'Stir-fried rice noodles with shrimp, egg, and peanuts.',     12.00, True),
    ('Green Curry',         'Thai',     'Fragrant coconut milk curry with vegetables and chicken.',   13.00, False),
    ('Cheeseburger',        'Fast Food','Beef patty with cheese, lettuce, tomato, and pickles.',       9.00, True),
    ('Chocolate Lava Cake', 'Desserts', 'Warm chocolate cake with a gooey molten centre.',             8.50, True),
    ('Mango Sticky Rice',   'Thai',     'Sweet glutinous rice served with fresh mango and coconut.',   7.00, False),
]

item_objs = []
for name, cat_name, desc, price, is_hot in dishes_data:
    item, created = Item.objects.get_or_create(name=name, defaults={
        'category': category_objs[cat_name],
        'description': desc,
        'price': price,
        'is_hot': is_hot,
    })
    item_objs.append(item)
print(f"  Created {len(item_objs)} dishes")

# ── Sample ratings ─────────────────────────────────────────────────────────
ratings_data = [
    # (user_index, item_index, rating, comment)
    (0, 0,  5, 'Absolutely delicious! The spice level was perfect.'),
    (0, 1,  4, 'Great duck, very crispy skin.'),
    (0, 4,  5, 'Best carbonara I have ever had!'),
    (0, 8,  4, 'Fresh fish, well-presented.'),
    (0, 9,  5, 'Rich broth, perfectly cooked egg.'),
    (1, 0,  4, 'Love the peanuts and chilli combination.'),
    (1, 2,  3, 'A bit too spicy for my taste.'),
    (1, 5,  5, 'Perfect Margherita, simple but excellent.'),
    (1, 8,  5, 'The freshest sushi I have tried.'),
    (1, 13, 4, 'Creamy and flavourful curry.'),
    (2, 4,  4, 'Authentic Italian flavours.'),
    (2, 5,  4, 'Good pizza, crispy crust.'),
    (2, 9,  5, 'Incredible ramen, will definitely return.'),
    (2, 15, 5, 'Perfect Pad Thai, just the right balance.'),
    (2, 17, 4, 'Juicy burger, great value.'),
    (3, 1,  5, 'Best Peking duck in the city!'),
    (3, 7,  5, 'Tiramisu was heavenly.'),
    (3, 10, 3, 'Decent but not exceptional.'),
    (3, 13, 5, 'Outstanding butter chicken.'),
    (3, 18, 5, 'The molten centre was perfect!'),
]
for user_idx, item_idx, rating, comment in ratings_data:
    r, created = UserRating.objects.get_or_create(
        user=users[user_idx], item=item_objs[item_idx],
        defaults={'rating': rating, 'comment': comment}
    )
    if created:
        item_objs[item_idx].update_avg_rating()
print(f"  Created {len(ratings_data)} ratings")

# ── Sample forum posts ─────────────────────────────────────────────────────
posts_data = [
    (0, 'Best ramen spots recommendation', 'I\'ve been on a ramen quest lately. Tonkotsu is my favourite — that rich pork broth is unmatched. Has anyone tried making it at home?'),
    (1, 'Hot pot etiquette guide', 'First time at a hot pot restaurant and I was completely lost! Here are some tips I picked up so you don\'t make the same mistakes.'),
    (2, 'Ranking all the Italian dishes', 'I went through all the Italian dishes on here and here\'s my personal ranking. Carbonara takes the top spot every time.'),
    (3, 'Why is Pad Thai so universally loved?', 'It seems like everyone loves Pad Thai. I think it\'s the perfect balance of sweet, sour, salty and umami. What do you think?'),
]
for user_idx, title, content in posts_data:
    ForumPost.objects.get_or_create(
        user=users[user_idx], title=title,
        defaults={'content': content}
    )
print(f"  Created {len(posts_data)} forum posts")

# ── System config ──────────────────────────────────────────────────────────
SystemConfig.objects.get_or_create(
    config_key='site_name',
    defaults={'value': 'Dish Discovery', 'description': 'Name of the platform'}
)
SystemConfig.objects.get_or_create(
    config_key='recommendation_limit',
    defaults={'value': '8', 'description': 'Number of recommendations to show'}
)

print("\nDone! ✓")
print("Admin login: admin / admin123")
print("Sample users: alice, bob, carol, dave (password: pass1234)")
