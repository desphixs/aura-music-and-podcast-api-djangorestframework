from django.contrib import admin
# We import UserAdmin from django.contrib.auth.admin.
# Think of UserAdmin as a custom dashboard configuration specifically designed 
# for handling user passwords, groups, and permissions.
# Without it, if we just registered the User model normally, password hashes 
# would be displayed as ugly plain text and we wouldn't have special forms 
# to reset or change passwords safely in the admin page!
from django.contrib.auth.admin import UserAdmin
# We import User and Profile models so we can register them to the admin dashboard
from .models import User, Profile

# We register our custom User model in the Django Admin.
# This makes our custom User table visible inside the /admin/ web dashboard 
# so we can easily create, read, update, or delete users visually.
# We pass UserAdmin as the second argument so Django uses the special, 
# secure layout to display user details.
admin.site.register(User, UserAdmin)

# We register our Profile model in the Django Admin.
# This allows administrators to visually manage user profiles, roles, and avatar URLs
# directly from the secure /admin/ dashboard panel.
admin.site.register(Profile)

