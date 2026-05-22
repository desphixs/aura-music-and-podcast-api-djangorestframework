import os
import django

# Set the settings module environment variable for Django to find our configuration
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
# Initialize Django's applications registry and database connections
django.setup()

from django.contrib.auth import get_user_model
from streaming.models import Category, Podcast, Track, Rating

User = get_user_model()

def seed_data():
    print("--- Starting Database Seeding ---")

    # 1. Clear any existing records to prevent unique constraints or duplicate key conflicts
    print("Clearing existing data...")
    Rating.objects.all().delete()
    Track.objects.all().delete()
    Podcast.objects.all().delete()
    Category.objects.all().delete()
    # Delete non-superuser accounts to rebuild them cleanly
    User.objects.filter(is_superuser=False).delete()
    User.objects.filter(email='admin@gmail.com').delete()

    # 2. Create Users
    print("Creating users...")

    # Create the Admin / Superuser
    # Using create_superuser ensures they have full admin panel control
    admin_user = User.objects.create_superuser(
        email='admin@gmail.com',
        username='admin',
        password='admin'
    )
    # Automatically created profile should have its role updated to creator
    admin_user.profile.role = 'creator'
    admin_user.profile.save()
    print("Created Superuser: admin@gmail.com / password: admin")

    # Create a dedicated Creator User
    creator_user = User.objects.create_user(
        email='creator@gmail.com',
        username='creator_podcasts',
        password='password123'
    )
    creator_user.profile.role = 'creator'
    creator_user.profile.save()
    print("Created Creator: creator@gmail.com / password: password123")

    # Create a dedicated Listener User
    listener_user = User.objects.create_user(
        email='listener@gmail.com',
        username='avid_listener',
        password='password123'
    )
    # The default profile role is already 'listener', but we save it explicitly for clarity
    listener_user.profile.role = 'listener'
    listener_user.profile.save()
    print("Created Listener: listener@gmail.com / password: password123")

    # 3. Create Categories
    print("Creating Categories...")
    tech_cat = Category.objects.create(name="Technology")
    comedy_cat = Category.objects.create(name="Comedy")
    music_cat = Category.objects.create(name="Music")
    health_cat = Category.objects.create(name="Health & Wellness")

    # 4. Create Podcasts (4 in total)
    print("Creating Podcasts...")
    
    podcast_1 = Podcast.objects.create(
        title="Tech Horizons",
        description="Exploring the latest in AI, developer trends, and next-generation programming tools.",
        creator=creator_user,
        category=tech_cat
    )
    
    podcast_2 = Podcast.objects.create(
        title="The Friday Giggles",
        description="Your weekly dose of comedy, absolute absurdity, and developer humor.",
        creator=creator_user,
        category=comedy_cat
    )
    
    podcast_3 = Podcast.objects.create(
        title="Ambient Synths",
        description="Relaxing lo-fi and cinematic beats for study, coding, and focus.",
        creator=admin_user,  # Created by superuser
        category=music_cat
    )
    
    podcast_4 = Podcast.objects.create(
        title="Mindful Minutes",
        description="Daily micro-meditations, breathing practices, and stress reduction guides.",
        creator=creator_user,
        category=health_cat
    )

    # 5. Create Audio Tracks
    print("Creating Tracks...")
    
    # Tracks for Tech Horizons
    Track.objects.create(
        title="Episode 1: The Rise of AI Coding Assistants",
        audio_url="https://res.cloudinary.com/demo/video/upload/sample_audio.mp3",
        duration="320", # Duration in seconds stored as text
        podcast=podcast_1
    )
    Track.objects.create(
        title="Episode 2: Understanding Django REST Framework Signals",
        audio_url="https://res.cloudinary.com/demo/video/upload/sample_audio_2.mp3",
        duration="450",
        podcast=podcast_1
    )

    # Track for Friday Giggles
    Track.objects.create(
        title="Episode 1: Why the Bouncer Blocked My Loop",
        audio_url="https://res.cloudinary.com/demo/video/upload/comedy_clip.mp3",
        duration="180",
        podcast=podcast_2
    )

    # Track for Ambient Synths
    Track.objects.create(
        title="Focus Track A: Cyber Sunset",
        audio_url="https://res.cloudinary.com/demo/video/upload/ambient_track_1.mp3",
        duration="600",
        podcast=podcast_3
    )

    # Track for Mindful Minutes
    Track.objects.create(
        title="Session 1: Three Deep Breaths",
        audio_url="https://res.cloudinary.com/demo/video/upload/meditation_1.mp3",
        duration="120",
        podcast=podcast_4
    )

    # 6. Create Ratings
    print("Creating Ratings...")
    
    # Listener rates Tech Horizons as 5 stars
    Rating.objects.create(
        score=5,
        user=listener_user,
        podcast=podcast_1
    )
    
    # Admin rates Tech Horizons as 4 stars
    Rating.objects.create(
        score=4,
        user=admin_user,
        podcast=podcast_1
    )

    # Listener rates Ambient Synths as 4 stars
    Rating.objects.create(
        score=4,
        user=listener_user,
        podcast=podcast_3
    )

    # Listener rates Friday Giggles as 5 stars
    Rating.objects.create(
        score=5,
        user=listener_user,
        podcast=podcast_2
    )

    print("--- Database Seeding Completed Successfully! ---")

if __name__ == "__main__":
    seed_data()
