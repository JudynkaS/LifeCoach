from django.urls import path
from .views import (
    HomeView, SessionHistoryView, SessionDetailView,
    ServiceListView, ServiceDetailView, ServiceCreateView,
    ServiceUpdateView, ServiceDeleteView
)

app_name = 'viewer'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('sessions/', SessionHistoryView.as_view(), name='session-history'),
    path('sessions/<int:pk>/', SessionDetailView.as_view(), name='session-detail'),
    path('services/', ServiceListView.as_view(), name='services'),
    path('services/create/', ServiceCreateView.as_view(), name='service-create'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    path('services/<int:pk>/update/', ServiceUpdateView.as_view(), name='service-update'),
    path('services/<int:pk>/delete/', ServiceDeleteView.as_view(), name='service-delete'),
] 