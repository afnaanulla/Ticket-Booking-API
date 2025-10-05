# bookings/urls.py

from django.urls import path
from .views import (
    SignupView, MovieListView, ShowListView, BookShowView,
    CancelBookingAPIView, MyBookingsListView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='login'),  # returns access & refresh tokens
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('movies/', MovieListView.as_view(), name='movies-list'),
    path('movies/<int:movie_id>/shows/', ShowListView.as_view(), name='movie-shows'),

    # Updated to use BookShowView
    path('shows/<int:pk>/book/', BookShowView.as_view(), name='book-show'),

    path('bookings/<int:id>/cancel/', CancelBookingAPIView.as_view(), name='cancel-booking'),
    path('my-bookings/', MyBookingsListView.as_view(), name='my-bookings'),
]
