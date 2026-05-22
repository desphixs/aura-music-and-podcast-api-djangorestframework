# Import the path function from Django's URL routing engine.
# Think of path as a road sign director that points incoming URLs to the correct server office.
from django.urls import path

# Import our views from the current streaming app.
from streaming.views import PodcastListAPIView, PodcastDetailAPIView

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
]

