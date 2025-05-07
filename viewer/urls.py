from django.urls import path
from . import views

app_name = 'viewer'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('services/', views.ServiceListView.as_view(), name='services'),
    path('services/<int:pk>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('services/create/', views.ServiceCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/edit/', views.ServiceUpdateView.as_view(), name='service_edit'),
    path('services/<int:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),
    path('sessions/', views.SessionHistoryView.as_view(), name='session_history'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<int:pk>/edit/', views.SessionUpdateView.as_view(), name='session_edit'),
    path('sessions/<int:pk>/cancel/', views.SessionCancelView.as_view(), name='cancel_session'),
    path('sessions/book/', views.BookingCreateView.as_view(), name='book_session'),
    path('sessions/<int:pk>/review/', views.ReviewCreateView.as_view(), name='create-review'),
]