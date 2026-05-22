# Import the base APIView class from Django REST Framework (DRF).
# Think of APIView as a specialized control center for handling standard HTTP requests manually.
from rest_framework.views import APIView

# Import the Response class from DRF.
# This wraps our Python data dictionaries into a beautiful HTTP response format (usually JSON).
from rest_framework.response import Response

# Import the status module from DRF to use clear, standardized HTTP status code names.
from rest_framework import status

# Import the Podcast model so we can fetch and create podcast records from our SQLite database.
from streaming.models import Podcast

# Import the PodcastSerializer to translate our Podcast objects to and from JSON.
from streaming.serializers import PodcastSerializer


# PodcastListAPIView handles listing all podcasts (GET) and creating a new podcast (POST).
# It inherits from DRF's APIView.
class PodcastListAPIView(APIView):
    
    # We define the GET method to handle requests fetching all podcasts.
    # Anyone (even unauthenticated visitors) can read podcasts!
    def get(self, request):
        # We query the database to fetch all podcast records.
        # We use select_related('creator') to optimize the database query,
        # fetching the creator details in one go instead of hitting the database repeatedly (N+1 query problem).
        podcasts = Podcast.objects.all().select_related('creator')
        
        # We instantiate our PodcastSerializer with the list of podcasts.
        # 'many=True' tells DRF that we are passing a list/queryset of multiple objects, 
        # not just a single podcast instance.
        serializer = PodcastSerializer(podcasts, many=True)
        
        # We return the serialized list of podcasts inside a Response.
        # By default, this sends a 200 OK status.
        return Response(serializer.data, status=status.HTTP_200_OK)

    # We define the POST method to handle requests for creating a new podcast.
    # Creating a podcast is restricted to logged-in users with a 'creator' role.
    def post(self, request):
        # 1. We require authentication manually.
        # We check if the user is logged in. If they are not, 'request.user.is_authenticated' will be False.
        if not request.user.is_authenticated:
            # We return a 401 Unauthorized response to tell the client they must sign in.
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2. We check the user's profile role.
        # We access the user's profile and check if their role is equal to 'creator'.
        if request.user.profile.role != 'creator':
            # If they are NOT a creator (e.g. they are a listener), we reject their request!
            # We return a 403 Forbidden status with a friendly, informative error message.
            return Response(
                {"detail": "Only creators can upload podcasts."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 3. If they passed all security checks, we proceed to handle the input data.
        # We pass the incoming JSON request data (request.data) to our PodcastSerializer.
        serializer = PodcastSerializer(data=request.data)
        
        # 4. We validate the incoming request details.
        # 'is_valid(raise_exception=True)' scans the user input against our model boundaries.
        # If the input fails validation (e.g., missing title), it automatically interrupts 
        # the code and returns a clean 400 Bad Request error to the client.
        serializer.is_valid(raise_exception=True)
        
        # 5. If validation succeeds, we save the podcast record.
        # We pass 'creator=request.user' inside 'serializer.save()' so that Django 
        # automatically links the newly created podcast to the currently logged-in user!
        serializer.save(creator=request.user)
        
        # 6. We return the newly created podcast details as JSON with a 201 Created status.
        # This tells the creator: "Success! Your new podcast has been created and published!"
        return Response(serializer.data, status=status.HTTP_201_CREATED)
