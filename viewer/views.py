from django.http import HttpResponse
from django.contrib.auth.models import User

def test_db(request):
    try:
        # Pokus o získání počtu uživatelů
        user_count = User.objects.count()
        return HttpResponse(f"Database connection successful! Number of users: {user_count}")
    except Exception as e:
        return HttpResponse(f"Database connection failed! Error: {str(e)}")

def hello(request):
    return HttpResponse('Hello, world!')