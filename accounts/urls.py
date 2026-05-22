from django.urls import path
# We import our RegisterAPIView, LoginAPIView, LogoutAPIView, RefreshAPIView, and MeAPIView classes from our views module
from .views import RegisterAPIView, LoginAPIView, LogoutAPIView, RefreshAPIView, MeAPIView

# urlpatterns defines a list of URL patterns that this specific application handles.
# Think of urlpatterns like a local department directory that maps a visitor's request 
# straight to the correct office room desk!
urlpatterns = [
    # path() defines the specific url pathway and maps it to the view.
    # We map 'register/' to RegisterAPIView.
    # Since RegisterAPIView is a Class-Based View, we must call '.as_view()' 
    # to unpack and convert our view class into a standard callable function.
    path('register/', RegisterAPIView.as_view(), name='register'),
    
    # We map 'login/' to LoginAPIView using the as_view() helper to unpack the class logic.
    path('login/', LoginAPIView.as_view(), name='login'),
    
    # We map 'logout/' to LogoutAPIView using the as_view() helper to unpack the class logic.
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    
    # We map 'refresh/' to RefreshAPIView using the as_view() helper to unpack the class logic.
    path('refresh/', RefreshAPIView.as_view(), name='token_refresh'),
    
    # We map 'me/' to MeAPIView using the as_view() helper to unpack the class logic.
    path('me/', MeAPIView.as_view(), name='me'),
]
