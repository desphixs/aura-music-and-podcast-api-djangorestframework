from django.db import models
# AbstractUser is the base blueprint that Django uses for standard users.
# Think of it as a pre-built house that already has plumbing, electrical wiring, and doors.
# By inheriting from it, we don't have to build password hashing, security systems, 
# or staff permissions from scratch—we just customize the parts we want to change!
from django.contrib.auth.models import AbstractUser
# post_save is the specific database signal triggered immediately after a model record is saved
from django.db.models.signals import post_save
# receiver is the decorator used to connect our signal handler functions to signals
from django.dispatch import receiver

# We define a custom User model class.
# This represents a single user account in our application database.
# Think of it like creating a customized template for a digital membership passport.
class User(AbstractUser):
    
    # We create a unique 'email' field.
    # Standard Django user models treat email as an optional string.
    # But in modern web apps, the email is your primary digital identity (like a physical fingerprint).
    # 'unique=True' ensures that two different people cannot register using the exact same email address.
    email = models.EmailField(unique=True) 
    
    # We create a unique 'username' field with a maximum length of 50 characters.
    # While we log in with our email, we still want a friendly nickname or display name for each user.
    # 'max_length=50' sets a reasonable boundary, like writing a name on a standard name tag.
    username = models.CharField(unique=True, max_length=50)

    # USERNAME_FIELD is a special variable that tells Django which field acts as the primary login credential.
    # By default, Django looks for a 'username' to log people in.
    # By setting this to 'email', we tell our security guards: "Check their email address when they log in!"
    USERNAME_FIELD = 'email'
    
    # REQUIRED_FIELDS is a list of field names that are prompted when creating a superuser via command line.
    # Since we swapped USERNAME_FIELD to 'email', Django automatically requires the email.
    # We explicitly add 'username' here so that Django still prompts and requires a username nickname
    # during user creation.
    REQUIRED_FIELDS = ['username']

    # The __str__ method defines the human-readable string representation of this object.
    # If a developer or admin looks at a list of users, instead of showing a confusing "User Object (1)",
    # it will show their actual email address, making administration and debugging a breeze.
    def __str__(self):
        # We return the email field as the text representation of the user
        return self.email


# We define the choices for the user roles in our application.
# A user can either be a standard listener or a creator who can publish shows.
ROLE_CHOICES = (
    ('listener', 'Listener'),
    ('creator', 'Creator'),
)

# The Profile model extends our custom User model with extra role-based fields.
# Think of this like adding specialized details on a membership card.
class Profile(models.Model):
    # OneToOneField creates a strict one-to-one relationship with our User model.
    # 'on_delete=models.CASCADE' means if a User is deleted, their profile is deleted too.
    # 'related_name="profile"' allows us to access this model via user.profile.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    # avatar_url is a TextField that will hold the secure URL of the image hosted on Cloudinary.
    # We default it to an empty string in case they haven't uploaded an avatar yet.
    avatar_url = models.TextField(blank=True, default='')
    # role determines if the user is a listener or creator.
    # We restrict choices to ROLE_CHOICES and set the default to 'listener'.
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='listener'
    )

    # The __str__ method defines the human-readable text representation of a Profile object.
    def __str__(self):
        # Returns a friendly string displaying the owner's email and role.
        return f"Profile for {self.user.email} ({self.role})"



# --- SIGNALS SECTION ---
# These receiver functions listen to User events to keep our profiles automatically synchronized.

# create_user_profile is triggered immediately after a User instance is saved.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # If the user was just newly created (created=True), we build their database Profile.
    if created:
        # Create a new Profile record mapped directly to this new User instance.
        Profile.objects.create(user=instance)


# save_user_profile ensures that when a User is updated, their Profile changes are saved too.
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Save the profile mapped to this User instance.
    instance.profile.save()
