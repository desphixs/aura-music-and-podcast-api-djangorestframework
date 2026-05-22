# Import the base APIView class from Django REST Framework (DRF).
# Think of APIView as a specialized control center for handling standard HTTP requests manually.
from rest_framework.views import APIView

# Import the Response class from DRF.
# This wraps our Python data dictionaries into a beautiful HTTP response format (usually JSON).
from rest_framework.response import Response

# Import the status module from DRF to use clear, standardized HTTP status code names.
from rest_framework import status

# Import the Podcast, Track, and Rating models so we can fetch and create records from our SQLite database.
from streaming.models import Podcast, Track, Rating

# Import our serializers to translate our models to and from JSON.
from streaming.serializers import PodcastSerializer, TrackSerializer, RatingSerializer


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


# TrackListCreateAPIView handles listing all tracks for a specific podcast (GET)
# and uploading/creating a new track for a specific podcast (POST).
# It inherits from DRF's APIView.
class TrackListCreateAPIView(APIView):
    
    # We define a helper method to safely retrieve a specific podcast by its ID (primary key).
    # This prevents code duplication in GET and POST methods, and ensures we can check if the podcast exists.
    def get_podcast(self, podcast_id):
        try:
            # We query the database to retrieve the podcast matching the podcast_id.
            # We use select_related('creator') so that we fetch the creator in the same database query.
            # This is highly optimized and prevents N+1 query problems when checking ownership!
            return Podcast.objects.select_related('creator').get(pk=podcast_id)
        except Podcast.DoesNotExist:
            # If the podcast does not exist in our system, we return None.
            # This allows the calling view method to easily respond to the client with a clear 404 error.
            return None

    # The GET method lists all tracks belonging to the specified podcast.
    # Anyone (even guest listeners) can view the track episodes of a podcast!
    def get(self, request, podcast_id):
        # We fetch the specific podcast using our helper method.
        podcast = self.get_podcast(podcast_id)
        
        # If the podcast doesn't exist, we return a clean 404 Not Found error response.
        if podcast is None:
            return Response(
                {"detail": "Podcast not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # We query the database to get all tracks associated with this podcast.
        # Since this podcast relation is already captured, we filter tracks by the podcast object.
        tracks = Track.objects.filter(podcast=podcast)
        
        # We instantiate our TrackSerializer, passing the queryset of tracks.
        # 'many=True' tells DRF that we are translating a list of multiple track objects.
        serializer = TrackSerializer(tracks, many=True)
        
        # We return the serialized list of tracks with a 200 OK status.
        return Response(serializer.data, status=status.HTTP_200_OK)

    # The POST method uploads a new track episode to the specified podcast.
    # This action is strictly restricted to the authenticated creator who owns the podcast!
    def post(self, request, podcast_id):
        # 1. First, we manually check if the user is authenticated.
        # A guest cannot upload tracks to any podcast!
        if not request.user.is_authenticated:
            # Return a 401 Unauthorized response if the user is anonymous.
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # 2. Next, we retrieve the target podcast.
        podcast = self.get_podcast(podcast_id)
        
        # If the podcast doesn't exist, we cannot attach a track to it! Return a 404 Not Found error.
        if podcast is None:
            return Response(
                {"detail": "Podcast not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # 3. We enforce ownership authorization.
        # Only the creator who owns this specific podcast can add tracks to it!
        # If the logged-in user does not match the podcast's creator, we reject them.
        if podcast.creator != request.user:
            # Return a 403 Forbidden status with a descriptive error message.
            return Response(
                {"detail": "You do not have permission to add tracks to this podcast."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # 4. If all checks pass, we deserialize the incoming request payload.
        # We pass the JSON data (request.data) to our TrackSerializer.
        serializer = TrackSerializer(data=request.data)
        
        # 5. We validate the incoming track data.
        # If validation fails (e.g., missing title or audio url), DRF throws an exception 
        # and returns a clean 400 Bad Request error to the client automatically.
        serializer.is_valid(raise_exception=True)
        
        # 6. We save the new track to our database filing cabinet.
        # We pass 'podcast=podcast' to explicitly associate this track with our retrieved podcast!
        serializer.save(podcast=podcast)
        
        # 7. We return the serialized JSON details of the newly created track with a 201 Created status!
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# TrackDetailAPIView handles fetching (GET), updating (PUT/PATCH), and deleting (DELETE) a single Track.
# It inherits from DRF's APIView.
class TrackDetailAPIView(APIView):
    
    # We define a helper method to safely retrieve a specific track by its ID (primary key).
    # This prevents code duplication in GET, PUT, and DELETE methods!
    def get_object(self, pk):
        try:
            # We query the database to fetch a specific track matching the pk ID.
            # We use select_related('podcast__creator') to execute a double-level SQL JOIN.
            # This pulls the track, its parent podcast, and the podcast's creator in a single query!
            # This optimization keeps our database lookups incredibly fast and avoids N+1 queries.
            return Track.objects.select_related('podcast__creator').get(pk=pk)
        except Track.DoesNotExist:
            # If no track with this ID exists, we return None.
            # This allows the calling view methods to respond with a clean 404 error response cleanly.
            return None

    # The GET method handles fetching details of a specific track episode.
    # Anyone (even unauthenticated guest listeners) can fetch a single track's profile details!
    def get(self, request, pk):
        # We call our helper method to fetch the track record.
        track = self.get_object(pk)
        
        # If the track is not found, we respond with a clean 404 error.
        if track is None:
            return Response(
                {"detail": "Track not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # We pass our database track object into the TrackSerializer.
        serializer = TrackSerializer(track)
        
        # We return the serialized track JSON details with a standard 200 OK status.
        return Response(serializer.data, status=status.HTTP_200_OK)

    # The PUT method handles editing and updating a specific track episode's metadata.
    # Editing a track is strictly locked to the creator who owns the parent podcast!
    def put(self, request, pk):
        # We retrieve the specific track record using our helper.
        track = self.get_object(pk)
        
        # If the track doesn't exist, we return a 404 Not Found error.
        if track is None:
            return Response(
                {"detail": "Track not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # 1. We manually check if the user is authenticated.
        # Anonymous visitors are completely blocked from editing anything!
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # 2. We check ownership authorization.
        # We verify if the logged-in user matches the creator who owns the track's parent podcast!
        if track.podcast.creator != request.user:
            # If they don't match, we immediately block the edit and return a 403 Forbidden response.
            return Response(
                {"detail": "You do not have permission to edit this track."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # 3. If ownership checks pass, we deserialize the incoming request payload.
        # We pass 'partial=True' so they can update just the title or audio url individually 
        # without having to resubmit all fields in every PUT request!
        serializer = TrackSerializer(track, data=request.data, partial=True)
        
        # 4. We run input validation.
        # If the new details fail validation (e.g. title is blank), DRF immediately aborts
        # and returns a clean 400 Bad Request error to the client.
        serializer.is_valid(raise_exception=True)
        
        # 5. We save the updated track record back into our SQLite database.
        serializer.save()
        
        # 6. We return the fresh, updated track JSON details with a standard 200 OK.
        return Response(serializer.data, status=status.HTTP_200_OK)

    # The DELETE method handles completely removing a track record from our library database.
    # Deleting a track is strictly locked to the creator who owns the parent podcast!
    def delete(self, request, pk):
        # We fetch the target track record.
        track = self.get_object(pk)
        
        # If the track doesn't exist, we return a 404.
        if track is None:
            return Response(
                {"detail": "Track not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # 1. We manually enforce login verification.
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # 2. We enforce ownership authorization.
        # Only the creator of the parent show has the permissions to delete its episodes!
        if track.podcast.creator != request.user:
            return Response(
                {"detail": "You do not have permission to delete this track."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # 3. If authorized, we delete the track from SQLite.
        track.delete()
        
        # 4. We return an HTTP 204 No Content response.
        # This is the universal success standard for deletion, representing clean closure!
        return Response(status=status.HTTP_204_NO_CONTENT)


# RatingAPIView handles listeners submitting review ratings for podcasts.
# It inherits from DRF's base APIView class.
class RatingAPIView(APIView):
    
    # The POST method handles creating and saving a brand-new rating score.
    # Ratings are restricted strictly to authenticated, logged-in listeners!
    def post(self, request):
        # 1. We manually enforce authentication check.
        # Anonymous guest users are completely blocked from leaving reviews!
        if not request.user.is_authenticated:
            # We return a 401 Unauthorized response to tell the client to sign in.
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2. We extract the podcast ID and score from the incoming request data body.
        # This will look inside the JSON data sent by the client.
        podcast_id = request.data.get('podcast')
        score = request.data.get('score')

        # 3. We validate that both required parameters are provided in the payload.
        # If either is missing, we must let the client know with a 400 Bad Request.
        if not podcast_id or score is None:
            return Response(
                {"detail": "Both podcast ID and score fields are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. We check if the target podcast actually exists in our library database.
        # We cannot submit a rating for a non-existent show!
        try:
            podcast = Podcast.objects.get(pk=podcast_id)
        except Podcast.DoesNotExist:
            # Return a 404 Not Found error if the podcast cannot be found in our database table.
            return Response(
                {"detail": "Podcast not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 5. We validate that the score is strictly between 1 and 5.
        # Standard reviews must be whole integers on a 1-to-5 star scale!
        try:
            # Convert the score to integer to make sure it's a valid numeric type.
            score_int = int(score)
        except (ValueError, TypeError):
            # If they sent a non-numeric score (like "five"), reject it with a 400 Bad Request.
            return Response(
                {"detail": "Score must be a valid integer score."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if score_int < 1 or score_int > 5:
            # If the score is outside the 1-to-5 boundary, we reject the request.
            return Response(
                {"detail": "Score must be strictly between 1 and 5."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 6. We check if a rating already exists for this logged-in user and podcast.
        # A single member can only submit one rating review per podcast show!
        # This checks our unique_together composite rule constraints manually.
        rating_exists = Rating.objects.filter(user=request.user, podcast=podcast).exists()
        if rating_exists:
            # If a rating already exists, we reject the submit with a 400 Bad Request.
            return Response(
                {"detail": "You have already rated this podcast show."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 7. If all validation checks succeed, we prepare the data and save the record.
        # We instantiate our RatingSerializer with our incoming request data.
        serializer = RatingSerializer(data=request.data)
        
        # We run the serializer's validation to ensure format safety.
        serializer.is_valid(raise_exception=True)
        
        # We save the rating database record back into our sqlite database filing cabinet.
        # We pass 'user=request.user' to automatically associate this rating with the logged-in user!
        serializer.save(user=request.user)

        # 8. We return a clean, descriptive success message and the serialized JSON data.
        # We return a 201 Created status telling the listener: "Success! Your review has been saved!"
        return Response(
            {
                "message": "Rating saved successfully.",
                "rating": serializer.data
            }, 
            status=status.HTTP_201_CREATED
        )


