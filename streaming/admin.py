from django.contrib import admin
# We import our custom models so that we can register them inside the Django Admin dashboard
from .models import Category, Podcast, Track, Rating

# We register our Category model in the Django Admin.
# This makes our categories table visible in the visual backend panel
# so we can easily create, read, update, or delete categories like Technology or Comedy.
admin.site.register(Category)

# We register our Podcast model in the Django Admin.
# This lets us manage podcasts, see descriptions, view which user is the creator,
# and link them to categories directly from the admin interface.
admin.site.register(Podcast)

# We register our Track model in the Django Admin.
# This lets us manage individual audio episodes or music tracks, update their streaming URLs,
# edit their duration, and link them to their parent podcasts.
admin.site.register(Track)

# We register our Rating model in the Django Admin.
# This lets us monitor the rating scores (1 to 5 stars) given to different podcasts
# by listeners, helping administrators manage user feedback seamlessly.
admin.site.register(Rating)
