# Import the path function from Django's URL routing engine.
# Think of path as a road sign director that points incoming URLs to the correct server office.
from django.urls import path

# Import our views from the current streaming app.
from streaming.views import (
    PodcastListAPIView, 
    PodcastDetailAPIView,
    TrackListCreateAPIView,
    TrackDetailAPIView
)

# urlpatterns defines a list of local URL patterns that this specific streaming app handles.
# This works like a localized department directory within our music/podcast streaming division.
urlpatterns = [
    # We map 'podcasts/' to our PodcastListAPIView.
    # Since PodcastListAPIView is a Class-Based View, we must call '.as_view()' 
    # to convert the view class into a standard callable function that Django can execute.
    # We also give the path a helpful 'name' alias for clean, dynamic reverse lookup references.
    path('podcasts/', PodcastListAPIView.as_view(), name='podcast_list'),

    # We map 'podcasts/<int:pk>/' to our PodcastDetailAPIView.
    # '<int:pk>' is a dynamic path converter that captures the integer ID from the URL 
    # and passes it as a keyword argument named 'pk' to our view's methods!
    path('podcasts/<int:pk>/', PodcastDetailAPIView.as_view(), name='podcast_detail'),

    # We map 'podcasts/<int:podcast_id>/tracks/' to our TrackListCreateAPIView.
    # '<int:podcast_id>' captures the specific podcast ID from the request URL, and passes it
    # as a keyword argument named 'podcast_id' straight into our GET and POST view methods!
    path('podcasts/<int:podcast_id>/tracks/', TrackListCreateAPIView.as_view(), name='track_list_create'),

    # We map 'tracks/<int:pk>/' to our TrackDetailAPIView.
    # '<int:pk>' is a dynamic path converter that captures the integer ID from the URL.
    # This dynamic ID represents the primary key (pk) of the specific track we want to manage.
    # We call '.as_view()' because TrackDetailAPIView is a Class-Based View.
    # This path is named 'track_detail' for dynamic reverse routing.
    path('tracks/<int:pk>/', TrackDetailAPIView.as_view(), name='track_detail'),
]


