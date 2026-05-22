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
        # We use select_related('creator') to fetch creator details in a single query.
        # We also use prefetch_related('tracks') to pull all tracks in one go to prevent N+1 query loops.
        # This double-optimization keeps our application incredibly fast and efficient!
        podcasts = Podcast.objects.all().select_related('creator').prefetch_related('tracks')
        
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


# PodcastDetailAPIView handles fetching (GET), updating (PUT/PATCH), and deleting (DELETE) a single Podcast.
# It inherits from DRF's APIView.
class PodcastDetailAPIView(APIView):
    
    # We define a helper method to safely retrieve a single podcast object by its ID (primary key).
    # This prevents code duplication in GET, PUT, and DELETE methods!
    def get_object(self, pk):
        try:
            # We query the database to fetch a specific podcast matching the pk ID.
            # We use select_related('creator') to pre-load the creator's user account in the same SQL query.
            # We use prefetch_related('tracks') to pre-load all the tracks belonging to this specific podcast.
            # This is an important optimization to keep our database operations extremely fast and robust!
            return Podcast.objects.select_related('creator').prefetch_related('tracks').get(pk=pk)
        except Podcast.DoesNotExist:
            # If no podcast with this ID exists, we return None so the calling method
            # can respond to the client with a clear 404 error cleanly.
            return None

    # We define the GET method to handle requests fetching a specific podcast's details.
    # Anyone (even unauthenticated guests) can view a specific podcast's profile card!
    def get(self, request, pk):
        # We call our helper method to fetch the podcast from the SQLite cabinet.
        podcast = self.get_object(pk)
        
        # We check if the podcast was found. If it returned None, we respond with a 404.
        if podcast is None:
            # We return an HTTP 404 Not Found error with a descriptive message.
            return Response(
                {"detail": "Podcast not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # We feed the retrieved podcast database object to our PodcastSerializer.
        serializer = PodcastSerializer(podcast)
        
        # We return the serialized JSON details inside a standard Response with 200 OK.
        return Response(serializer.data, status=status.HTTP_200_OK)

    # We define the PUT method to handle updates to a specific podcast.
    # Only the creator of this specific podcast is allowed to update it!
    def put(self, request, pk):
        # We fetch the specific podcast object using our helper method.
        podcast = self.get_object(pk)
        
        # We check if the podcast exists. If not, we block the request with a 404 error.
        if podcast is None:
            return Response(
                {"detail": "Podcast not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # 1. We manually enforce authentication check.
        # The user must be logged in to modify any data!
        if not request.user.is_authenticated:
            # Return 401 Unauthorized if they are anonymous.
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # 2. We check ownership authorization (Is this user the original creator?).
        # We compare the podcast's creator User object directly against the logged-in request.user.
        if podcast.creator != request.user:
            # If the user logged in is NOT the person who created this podcast, they cannot modify it!
            # We return a 403 Forbidden status with a strict error message.
            return Response(
                {"detail": "You do not have permission to edit this podcast."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # 3. If ownership is verified, we process the update.
        # We instantiate our PodcastSerializer, feeding it both the existing podcast object 
        # and the new request data. We pass 'partial=True' so they can update just a single 
        # field (like description) without having to submit all fields every single time!
        serializer = PodcastSerializer(podcast, data=request.data, partial=True)
        
        # 4. We run validation checks on the updated fields.
        serializer.is_valid(raise_exception=True)
        
        # 5. We save the updated podcast record back into our database filing cabinet.
        serializer.save()
        
        # 6. We return the fresh, updated podcast JSON details with a standard 200 OK.
        return Response(serializer.data, status=status.HTTP_200_OK)

    # We define the DELETE method to handle removing a podcast completely.
    # Only the original creator of this specific podcast is allowed to delete it!
    def delete(self, request, pk):
        # We query the specific podcast record using our helper.
        podcast = self.get_object(pk)
        
        # We verify the podcast exists. If not, we return a 404.
        if podcast is None:
            return Response(
                {"detail": "Podcast not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # 1. We manually enforce authentication.
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # 2. We verify ownership authorization.
        # Only the creator of this specific show can delete it from our platform catalog.
        if podcast.creator != request.user:
            # Return 403 Forbidden to any user attempting to delete someone else's show.
            return Response(
                {"detail": "You do not have permission to delete this podcast."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # 3. If verified, we delete the podcast record from the database.
        # This will trigger an automatic database cascade deletion,
        # cleanly wiping out all associated tracks and ratings linked to this podcast!
        podcast.delete()
        
        # 4. We return an HTTP 204 No Content status.
        # This is the universal standard response for a successful deletion, 
        # telling the client: "Success! The item has been deleted, there is nothing left to show!"
        return Response(status=status.HTTP_204_NO_CONTENT)

