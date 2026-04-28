from datetime import date, time, timedelta
from decimal import Decimal
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Seat, SeatType, SubscriptionPlan
from movies.models import Cinema, Genre, Movie, Showtime

User = get_user_model()

SAMPLE_MOVIES = [
    {
        "title": "Dune: Part Two",
        "primary_genre": "Sci-Fi",
        "release_year": 2024,
        "runtime_minutes": 166,
        "rating": Decimal("8.7"),
        "star_rating": 4,
        "status": Movie.STATUS_NOW_SHOWING,
        "badge": Movie.BADGE_TRENDING,
        "cast": "Timothée Chalamet, Zendaya, Rebecca Ferguson, Josh Brolin, Austin Butler",
        "synopsis": "Paul Atreides unites with Chani and the Fremen while on a path of revenge against the conspirators who destroyed his family.",
    },
    {
        "title": "Oppenheimer",
        "primary_genre": "Drama",
        "release_year": 2023,
        "runtime_minutes": 180,
        "rating": Decimal("8.4"),
        "star_rating": 5,
        "status": Movie.STATUS_NOW_SHOWING,
        "badge": Movie.BADGE_TRENDING,
        "cast": "Cillian Murphy, Emily Blunt, Matt Damon, Robert Downey Jr.",
        "synopsis": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb.",
    },
    {
        "title": "Inception",
        "primary_genre": "Sci-Fi",
        "release_year": 2010,
        "runtime_minutes": 148,
        "rating": Decimal("9.8"),
        "star_rating": 5,
        "status": Movie.STATUS_NOW_SHOWING,
        "badge": "",
        "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page, Tom Hardy, Ken Watanabe",
        "synopsis": "A skilled thief is given a chance at redemption if he can successfully perform inception: planting an idea in a target's subconscious.",
    },
    {
        "title": "The Batman",
        "primary_genre": "Action",
        "release_year": 2022,
        "runtime_minutes": 176,
        "rating": Decimal("7.8"),
        "star_rating": 4,
        "status": Movie.STATUS_NOW_SHOWING,
        "badge": "",
        "cast": "Robert Pattinson, Zoë Kravitz, Paul Dano, Jeffrey Wright",
        "synopsis": "When a sadistic killer leaves behind a trail of cryptic clues, Batman must forge new relationships and unmask the culprit.",
    },
    {
        "title": "Eternal Sunshine of the Spotless Mind",
        "primary_genre": "Sci-Fi",
        "release_year": 2004,
        "runtime_minutes": 108,
        "rating": Decimal("8.3"),
        "star_rating": 4,
        "status": Movie.STATUS_NOW_SHOWING,
        "badge": "",
        "cast": "Jim Carrey, Kate Winslet, Kirsten Dunst",
        "synopsis": "A couple undergo a procedure to erase each other from their memories when their relationship turns sour.",
    },
    {
        "title": "Little Women",
        "primary_genre": "Drama",
        "release_year": 2019,
        "runtime_minutes": 135,
        "rating": Decimal("7.8"),
        "star_rating": 5,
        "status": Movie.STATUS_NOW_SHOWING,
        "badge": "",
        "cast": "Saoirse Ronan, Emma Watson, Florence Pugh, Eliza Scanlen",
        "synopsis": "Four sisters come of age in America in the aftermath of the Civil War.",
    },
    {
        "title": "Interstellar",
        "primary_genre": "Sci-Fi",
        "release_year": 2014,
        "runtime_minutes": 169,
        "rating": Decimal("8.6"),
        "star_rating": 5,
        "status": Movie.STATUS_NOW_SHOWING,
        "badge": "",
        "cast": "Matthew McConaughey, Anne Hathaway, Jessica Chastain",
        "synopsis": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
    },
    {
        "title": "Gladiator II",
        "primary_genre": "Action",
        "release_year": 2024,
        "runtime_minutes": 150,
        "rating": Decimal("7.5"),
        "star_rating": 4,
        "status": Movie.STATUS_COMING_SOON,
        "badge": Movie.BADGE_NEW,
        "cast": "Paul Mescal, Pedro Pascal, Denzel Washington",
        "synopsis": "Years after Maximus's death, a new warrior rises in the Roman arena.",
    },
    {
        "title": "Avatar 3",
        "primary_genre": "Sci-Fi",
        "release_year": 2025,
        "runtime_minutes": 180,
        "rating": Decimal("0"),
        "star_rating": 4,
        "status": Movie.STATUS_COMING_SOON,
        "badge": Movie.BADGE_NEW,
        "cast": "Sam Worthington, Zoe Saldaña",
        "synopsis": "Jake Sully and his family continue their journey on Pandora.",
    },
    {
        "title": "Mission Impossible",
        "primary_genre": "Action",
        "release_year": 2022,
        "runtime_minutes": 148,
        "rating": Decimal("7.9"),
        "star_rating": 4,
        "status": Movie.STATUS_PENDING,
        "badge": "",
        "cast": "Tom Cruise",
        "synopsis": "Ethan Hunt races against time to stop a new global threat.",
    },
    {
        "title": "Finding Nemo",
        "primary_genre": "Animation",
        "release_year": 2003,
        "runtime_minutes": 100,
        "rating": Decimal("8.2"),
        "star_rating": 5,
        "status": Movie.STATUS_NOW_SHOWING,
        "badge": "",
        "cast": "Albert Brooks, Ellen DeGeneres",
        "synopsis": "A clownfish sets out across the ocean to rescue his son.",
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample movies, cinemas, showtimes, seats, plans, and admin user."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        # Admin + customer users
        if not User.objects.filter(email="admin@plotpick.com").exists():
            admin = User.objects.create_user(
                username="admin@plotpick.com",
                email="admin@plotpick.com",
                password="admin123",
                full_name="Admin User",
                role=User.ROLE_ADMIN,
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(f"  ✔ Created admin: admin@plotpick.com / admin123")
        if not User.objects.filter(email="aliza@plotpick.com").exists():
            User.objects.create_user(
                username="aliza@plotpick.com",
                email="aliza@plotpick.com",
                password="demo12345",
                full_name="Aliza Demo",
            )
            self.stdout.write("  ✔ Created customer: aliza@plotpick.com / demo12345")

        # Genres
        for name in ["Action", "Drama", "Horror", "Romance", "Sci-Fi", "Comedy", "Animation", "Thriller"]:
            Genre.objects.get_or_create(name=name)

        # Subscription plans
        plans = [
            (SubscriptionPlan.NAME_FREE, "Free", Decimal("0"), 0, 0, "5 movies/mo, SD only", False),
            (SubscriptionPlan.NAME_STANDARD, "Standard", Decimal("9.99"), 7, 10, "Unlimited, HD, 10% seats", True),
            (SubscriptionPlan.NAME_PREMIUM, "Premium", Decimal("17.99"), 14, 20, "Unlimited, 4K, downloads", False),
        ]
        for slug, name, price, trial, discount, features, popular in plans:
            SubscriptionPlan.objects.update_or_create(
                slug=slug,
                defaults={
                    "display_name": name,
                    "price": price,
                    "trial_days": trial,
                    "cinema_discount_pct": discount,
                    "features": features,
                    "is_popular": popular,
                    "is_active": True,
                },
            )

        # Seat types
        seat_types = [
            (SeatType.TYPE_STANDARD, "Standard", "Regular seating, any row", Decimal("8.00"), 80, SeatType.STOCK_AVAILABLE),
            (SeatType.TYPE_PREMIUM, "Premium", "Center section, wider seats", Decimal("13.00"), 24, SeatType.STOCK_AVAILABLE),
            (SeatType.TYPE_VIP, "VIP Recliner", "Fully reclining, front service", Decimal("22.00"), 24, SeatType.STOCK_LIMITED),
            (SeatType.TYPE_COUPLES, "Couples Pod", "Private pod, 2-person sofa", Decimal("35.00"), 16, SeatType.STOCK_LOW),
        ]
        for slug, name, desc, price, count, stock in seat_types:
            SeatType.objects.update_or_create(
                slug=slug,
                defaults={
                    "display_name": name,
                    "description": desc,
                    "price": price,
                    "seat_count": count,
                    "stock_status": stock,
                },
            )

        # Cinemas
        cinema1, _ = Cinema.objects.get_or_create(name="Cineplex Downtown", defaults={"location": "Downtown Plaza"})
        cinema2, _ = Cinema.objects.get_or_create(name="CineMax Arena", defaults={"location": "North Mall"})
        cinema3, _ = Cinema.objects.get_or_create(name="Grand Cineplex", defaults={"location": "East Hills"})
        cinemas = [cinema1, cinema2, cinema3]

        # Movies
        movies = []
        for data in SAMPLE_MOVIES:
            m, created = Movie.objects.update_or_create(
                title=data["title"],
                defaults=data,
            )
            genre, _ = Genre.objects.get_or_create(name=data["primary_genre"])
            m.genres.add(genre)
            movies.append(m)
            if created:
                self.stdout.write(f"  ✔ Added movie: {m.title}")

        # Showtimes + seats for now-showing movies
        showtime_slots = [time(10, 30), time(13, 15), time(16, 0), time(19, 30)]
        today = timezone.now().date()
        for m in movies:
            if m.status != Movie.STATUS_NOW_SHOWING:
                continue
            for i in range(5):
                d = today + timedelta(days=i)
                cinema = random.choice(cinemas)
                for t in showtime_slots:
                    st, created = Showtime.objects.get_or_create(
                        movie=m, cinema=cinema, date=d, time=t,
                        defaults={"is_sold_out": False},
                    )
                    if created:
                        self._generate_seats(st)

        self.stdout.write(self.style.SUCCESS("Seed complete."))

    def _generate_seats(self, showtime):
        rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        seats_per_row = 16
        for row in rows:
            if row in ("A", "B"):
                category = Seat.CATEGORY_VIP
            elif row in ("C", "D", "E"):
                category = Seat.CATEGORY_PREMIUM
            else:
                category = Seat.CATEGORY_REGULAR
            for n in range(1, seats_per_row + 1):
                is_reserved = random.random() < 0.1
                Seat.objects.create(
                    showtime=showtime,
                    row=row,
                    number=n,
                    category=category,
                    is_reserved=is_reserved,
                )
