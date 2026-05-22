from rest_framework import serializers
# We import our custom User model class.
# This represents our database user layout.
from .models import User
# We import the built-in authenticate tool from Django's authentication engine.
# Think of authenticate as a security guard who takes a credentials slip, 
# walks back to the database filing cabinet, looks up the record, 
# verifies if the password matches, and returns the User object if successful!
from django.contrib.auth import authenticate


# RegisterSerializer handles registration of brand new users.
# It inherits from ModelSerializer because we are mapping inputs directly 
# to our User database table columns.
class RegisterSerializer(serializers.ModelSerializer):
    # We define password as a write-only CharField.
    # 'write_only=True' is a critical security rule! It ensures that the password 
    # goes INTO the database, but is NEVER returned back in the JSON API responses.
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        min_length=6
    )

    class Meta:
        # We bind this serializer directly to our custom User model
        model = User
        # We expose only the email, username, and password fields for registration
        fields = ('email', 'username', 'password')

    # The create method defines what happens when the serializer is valid 
    # and we save the record. We must hash the password safely!
    def create(self, validated_data):
        # We use Django's helper 'create_user' from our User manager.
        # Think of create_user as a high-security lockbox creator. 
        # Instead of saving the password as plain text (like 'admin123'), 
        # it runs the password through a heavy cryptographic algorithm (PBKDF2/bcrypt)
        # to generate a secure, unreadable hash.
        # This guarantees that even if our database gets leaked, nobody can read passwords!
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        # We return the newly created user object
        return user


# LoginSerializer handles user login credential verification.
# It inherits from serializers.Serializer (not ModelSerializer) because we are 
# not creating or editing anything in the database—we are simply validating incoming logs!
class LoginSerializer(serializers.Serializer):
    # We define the incoming email field
    email = serializers.EmailField()
    
    # We define the incoming password field as write-only
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    # The validate method acts as our custom gatekeeper.
    # It takes the parsed input, runs checks, and returns a verified state.
    def validate(self, attrs):
        # We pull the email and password from the validated dictionary attributes
        email = attrs.get('email')
        password = attrs.get('password')

        # We check if both email and password are provided
        if email and password:
            # We call the 'authenticate' bouncer.
            # When USERNAME_FIELD is 'email', Django's authenticate method expects 
            # the email to be passed to the 'username' parameter.
            user = authenticate(username=email, password=password)

            # If the user does not exist or credentials fail, authenticate returns None
            if not user:
                # We raise a validation error to let the API caller know they failed login
                raise serializers.ValidationError(
                    "Invalid email or password. Please check your credentials and try again."
                )
            
            # If the account has been disabled, we block them
            if not user.is_active:
                raise serializers.ValidationError("This user account has been deactivated.")
            
        else:
            # If they forgot to send email or password, we complain
            raise serializers.ValidationError("Both email and password are required to log in.")

        # We store the authenticated user object in our validated attributes dictionary.
        # This makes it super easy for our API views to grab the user and issue tokens next!
        attrs['user'] = user
        # We return the attributes dictionary
        return attrs
