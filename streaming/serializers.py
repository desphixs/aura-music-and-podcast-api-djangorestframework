# Import the serializers module from Django REST Framework (DRF).
# Think of serializers as digital translators. They convert complex database models 
# (Python objects) into clean JSON strings for our frontend to read, and vice-versa!
from rest_framework import serializers

# Import the Category and Podcast models from our current streaming app's models file.
# This tells our serializers exactly what database tables they will be translating.
from streaming.models import Category, Podcast

# Import the custom User model defined in our accounts app so we can serialize creator details.
from django.contrib.auth import get_user_model

# Get the current active User model class.
User = get_user_model()


# CreatorSerializer is a simple, read-only serializer to display the basic details of a creator.
# Instead of just showing a creator's ID, this lets us show their email and username in the JSON!
class CreatorSerializer(serializers.ModelSerializer):
    class Meta:
        # We bind this serializer directly to the custom User model table.
        model = User
        # We only expose the ID, email, and username of the creator.
        # This keeps the creator's password and sensitive info completely hidden from public view!
        fields = ['id', 'email', 'username']


# PodcastSerializer handles the serialization and validation of Podcast objects.
# It inherits from ModelSerializer, which automatically builds serializer fields 
# based on our database model columns.
class PodcastSerializer(serializers.ModelSerializer):
    # We use our CreatorSerializer nested inside this podcast serializer.
    # 'read_only=True' ensures that the creator field cannot be sent in the request body (POST).
    # Instead, we will assign the creator automatically in our view from the authenticated user!
    creator = CreatorSerializer(read_only=True)
    
    # We define the category field using PrimaryKeyRelatedField.
    # This allows a client to pass the integer ID of a Category when creating a podcast.
    # 'queryset=Category.objects.all()' tells DRF to search the Category table for valid matching IDs.
    # 'required=False' and 'allow_null=True' mean a podcast does not have to be assigned a category.
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        # We bind this serializer directly to our Podcast model table.
        model = Podcast
        
        # We specify exactly which fields we want to include in our JSON payloads.
        fields = [
            'id', 
            'title', 
            'description', 
            'creator', 
            'category', 
            'created_at'
        ]
        
        # We make the 'created_at' field read-only because it is automatically generated 
        # by the database and should never be modified or submitted by a user.
        read_only_fields = ['created_at']
