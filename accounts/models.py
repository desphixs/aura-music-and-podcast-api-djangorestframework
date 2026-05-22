from django.db import models
# AbstractUser is the base blueprint that Django uses for standard users.
# Think of it as a pre-built house that already has plumbing, electrical wiring, and doors.
# By inheriting from it, we don't have to build password hashing, security systems, 
# or staff permissions from scratch—we just customize the parts we want to change!
from django.contrib.auth.models import AbstractUser

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
