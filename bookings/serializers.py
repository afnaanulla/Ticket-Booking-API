from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Movie, Show, Booking

# ---------------- SIGNUP ----------------
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

# ---------------- MOVIE & SHOW ----------------
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'title', 'duration_minutes', 'genre', 'rating', 'age_limit')

class ShowSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    available_seats = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Show
        fields = ('id', 'movie', 'screen_name', 'date_time', 'total_seats', 'available_seats', 'status')

    def get_available_seats(self, obj):
        booked_count = Booking.objects.filter(show=obj, status='booked').count()
        return obj.total_seats - booked_count

    def get_status(self, obj):
        return "Fully Booked" if self.get_available_seats(obj) <= 0 else "Available"

# ---------------- PASSENGER ----------------
class PassengerSerializer(serializers.Serializer):
    passenger_name = serializers.CharField(max_length=255)
    passenger_age = serializers.IntegerField(min_value=0)

# ---------------- BOOKING ----------------
class BookingSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True, write_only=True)
    seat_number = serializers.IntegerField(write_only=True)
    show = ShowSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'show', 'seat_number', 'status', 'created_at', 'passengers']

    def validate(self, data):
        request = self.context['request']
        show = self.context['show']
        movie = show.movie

        booked_count = Booking.objects.filter(show=show, status='booked').count()
        if booked_count >= show.total_seats:
            raise serializers.ValidationError("Show is fully booked.")

        passengers = data.get('passengers', [])
        if not passengers:
            raise serializers.ValidationError("At least one passenger is required.")

        # Check if enough seats available
        available_count = show.total_seats - booked_count
        if len(passengers) > available_count:
            raise serializers.ValidationError(
                f"Only {available_count} seats available, but {len(passengers)} passengers requested."
            )

        seat_number = data.get('seat_number')
        if seat_number is None or not (1 <= seat_number <= show.total_seats):
            raise serializers.ValidationError(f"seat_number must be between 1 and {show.total_seats}.")

        # Check if we have enough consecutive seats starting from seat_number
        num_passengers = len(passengers)
        if seat_number + num_passengers - 1 > show.total_seats:
            raise serializers.ValidationError(
                f"Cannot book {num_passengers} consecutive seats starting from seat {seat_number}. "
                f"Only {show.total_seats - seat_number + 1} seats available from that position."
            )

        # Check if any of the required consecutive seats are already booked
        booked_seats = set(Booking.objects.filter(show=show, status='booked').values_list('seat_number', flat=True))
        required_seats = range(seat_number, seat_number + num_passengers)
        
        already_booked = [s for s in required_seats if s in booked_seats]
        if already_booked:
            raise serializers.ValidationError(
                f"Cannot book consecutive seats starting from {seat_number}. "
                f"Seats {already_booked} are already booked."
            )

        # Genre-enhanced age validation - ALL passengers must meet age requirement
        effective_age_limit = movie.age_limit
        if movie.genre.lower() == "horror":
            effective_age_limit += 2

        underage_passengers = []
        for p in passengers:
            age = p.get('passenger_age')
            if age < effective_age_limit:
                underage_passengers.append(
                    f"{p.get('passenger_name')} (age {age})"
                )
        
        if underage_passengers:
            raise serializers.ValidationError(
                f"The following passengers do not meet the age requirement ({effective_age_limit}+): "
                f"{', '.join(underage_passengers)}"
            )

        return data

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        show = self.context['show']

        passengers = validated_data.pop('passengers', [])
        seat_number = validated_data.pop('seat_number')
        bookings = []

        # Create one booking per passenger with consecutive seats
        current_seat = seat_number
        for passenger in passengers:
            name = passenger['passenger_name']
            age = passenger['passenger_age']

            booking = Booking.objects.create(
                user=user,
                show=show,
                seat_number=current_seat,
                passenger_name=name,
                passenger_age=age,
                status='booked'
            )
            bookings.append(booking)
            current_seat += 1  # Next consecutive seat

        return bookings