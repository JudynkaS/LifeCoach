from django.urls import path
from . import views
from .views import SessionUpdateView

app_name = 'viewer'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('services/', views.ServiceListView.as_view(), name='services'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('sessions/', views.SessionHistoryView.as_view(), name='session_history'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<int:pk>/edit/', SessionUpdateView.as_view(), name='session_edit'),
    path('book/', views.BookingCreateView.as_view(), name='book_session'),
    # ... další cesty podle potřeby ...
] 