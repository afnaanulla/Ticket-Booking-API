from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError

from .models import Movie, Show, Booking
from .serializers import (
    SignupSerializer, MovieSerializer, ShowSerializer,
    BookingSerializer
)


# ---------------- SIGNUP ----------------
class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]


# ---------------- MOVIE ----------------
class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]


# ---------------- SHOW ----------------
class ShowListView(generics.ListAPIView):
    serializer_class = ShowSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        movie_id = self.kwargs.get('movie_id')
        return Show.objects.filter(movie_id=movie_id).order_by('date_time')


# ---------------- BOOKING ----------------
class BookShowView(generics.GenericAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        """
        Handles booking for multiple passengers.
        Validates:
          - Seat availability
          - Age restrictions
          - Overbooking
          - Duplicate seat booking
        """
        show = get_object_or_404(Show, id=pk)
        serializer = self.get_serializer(data=request.data, context={'request': request, 'view': self, 'show': show})
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            locked_show = Show.objects.select_for_update().get(pk=show.pk)
            booked_count = Booking.objects.filter(show=locked_show, status=Booking.STATUS_BOOKED).count()

            if booked_count >= locked_show.total_seats:
                return Response({"detail": "Show is fully booked."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                bookings = serializer.save()
            except IntegrityError:
                return Response({"detail": "Some seats were just booked by another user."},
                                status=status.HTTP_409_CONFLICT)

        # Return all bookings with proper count
        num_bookings = len(bookings)
        return Response(
            {
                "message": f"{num_bookings} ticket(s) booked successfully!",
                "bookings": BookingSerializer(bookings, many=True, context={'request': request}).data
            },
            status=status.HTTP_201_CREATED
        )


# ---------------- CANCEL BOOKING ----------------
class CancelBookingAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        booking = get_object_or_404(Booking, id=id)

        if booking.user != request.user:
            return Response({"detail": "You may only cancel your own bookings."}, status=status.HTTP_403_FORBIDDEN)

        if booking.status == Booking.STATUS_CANCELLED:
            return Response({"detail": "Booking already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

        booking.status = Booking.STATUS_CANCELLED
        booking.save(update_fields=['status'])
        return Response({"detail": "Booking cancelled."}, status=status.HTTP_200_OK)


# ---------------- MY BOOKINGS ----------------
class MyBookingsListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).select_related('show__movie')