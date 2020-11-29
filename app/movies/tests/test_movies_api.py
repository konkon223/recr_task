from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from movies.models import Movie, Comment
from movies.api.serializers import MovieSerializer

LIST_CREATE_MOVIES_URL = reverse("list_create_movie")
LIST_TOP_MOVIES_URL = reverse("list_top_movies")


def detail_url(movie_id):
    return reverse("retrieve_update_destroy_movie", kwargs={"id": movie_id})


def sample_movie(title="Great Movie", data={"Year": "1999", "Genre": "Drama"}):
    """Create a sample movie"""
    return Movie.objects.create(title=title, data=data)


def sample_comment(movie, body="Test comment"):
    """Create a sample comment"""
    return Comment.objects.create(movie=movie, body=body)


class MoviesAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_movies(self):
        """Test retrieving a list of movies"""
        sample_movie()
        sample_movie(title="Another Great movie")

        res = self.client.get(LIST_CREATE_MOVIES_URL)

        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True, fields=["id", "title", "data"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_movie_successful(self):
        """Test creating a new movie"""
        payload = {"title": "Test movie"}
        self.client.post(LIST_CREATE_MOVIES_URL, payload)

        exists = Movie.objects.filter(title=payload["title"]).exists()
        self.assertTrue(exists)

    def test_create_movie_invalid(self):
        """Test creating a new movie with invalid payload"""
        payload = {"title": ""}
        res = self.client.post(LIST_CREATE_MOVIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_movie_detail(self):
        """Test retrieving a movie detail"""
        movie = sample_movie()
        movie.comments.add(sample_comment(movie))

        url = detail_url(movie.id)
        res = self.client.get(url)

        serializer = MovieSerializer(movie, fields=["id", "title", "data", "comments"])
        self.assertEqual(res.data, serializer.data)

    def test_update_movie(self):
        """Test updating a movie"""
        movie = sample_movie()
        payload = {"data": {"Year": "2005", "Genre": "Comedy"}}

        url = detail_url(movie.id)
        self.client.put(url, payload, format="json")

        movie.refresh_from_db()

        self.assertEqual(movie.data, payload["data"])

    def test_destroy_movie(self):
        """Test destroying a movie"""
        movie = sample_movie()
        url = detail_url(movie.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_movies_by_genre(self):
        """Test returning movies with specific genre"""
        sample_movie()
        sample_movie(title="Another Great Movie", data={"Year": "1999", "Genre": "Comedy"})
        sample_movie(title="Yet Another Great Movie", data={"Year": "2001", "Genre": "Drama"})

        movies = Movie.objects.all()
        filtered_movies = Movie.objects.filter(data__Genre="Drama")

        res = self.client.get(LIST_CREATE_MOVIES_URL, {"genre": "Drama"})

        serializer = MovieSerializer(movies, many=True, fields=["id", "title", "data"])
        filtered_serializer = MovieSerializer(filtered_movies, many=True, fields=["id", "title", "data"])
        self.assertEqual(filtered_serializer.data, res.data)
        self.assertNotEqual(filtered_serializer.data, serializer.data)

    def test_order_movies_by_year(self):
        """Test returning movies ordered by year"""
        sample_movie()
        sample_movie(title="Another Great Movie", data={"Year": "1989", "Genre": "Comedy"})
        sample_movie(title="Yet Another Great Movie", data={"Year": "2001", "Genre": "Drama"})

        movies = Movie.objects.all()
        ordered_movies = Movie.objects.order_by("data__Year")
        res = self.client.get(LIST_CREATE_MOVIES_URL, {"order_by": "Year"})

        serializer = MovieSerializer(movies, many=True, fields=["id", "title", "data"])
        ordered_serializer = MovieSerializer(ordered_movies, many=True, fields=["id", "title", "data"])
        self.assertEqual(ordered_serializer.data, res.data)
        self.assertNotEqual(ordered_serializer, serializer)

    def test_list_top_movies_successful(self):
        """Test retrieving top movies by amount of comments for specific date"""
        movie1 = sample_movie()
        movie2 = sample_movie(title="Another Great Movie", data={"Year": "1989", "Genre": "Comedy"})
        sample_comment(movie1, body="Test comment")
        sample_comment(movie2, body="Test comment 2")

        movies = Movie.objects.create_ranking(start_date="2010-11-27", end_date="3020-11-29")

        res = self.client.get(LIST_TOP_MOVIES_URL, {"start": "2010-11-27", "end": "3020-11-29"})
        serializer = MovieSerializer(movies, many=True, fields=["movie_id", "total_comments", "rank"])

        self.assertEqual(serializer.data, res.data)
        self.assertNotEqual([], res.data)

    def test_list_top_movies_invalid_params(self):
        """Test retrieving top movies by amount of comments for specific date range with invalid query params"""
        res = self.client.get(LIST_TOP_MOVIES_URL, {"start": "2020-11-999", "end": "2020-11-999"})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_top_movies_no_params(self):
        """Test retrieving top movies by amount of comments for specific date range without query params"""
        res = self.client.get(LIST_TOP_MOVIES_URL, {"start": "", "end": ""})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_top_movies_empty(self):
        """Test retrieving top movies by amount of comments for specific date range without any comments"""
        movie1 = sample_movie()
        movie2 = sample_movie(title="Another Great Movie", data={"Year": "1989", "Genre": "Comedy"})
        sample_comment(movie1, body="Test comment")
        sample_comment(movie2, body="Test comment 2")

        res = self.client.get(LIST_TOP_MOVIES_URL, {"start": "1800-11-27", "end": "1800-11-29"})

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
