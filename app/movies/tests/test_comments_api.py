from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from movies.models import Movie, Comment
from movies.api.serializers import CommentSerializer

LIST_CREATE_COMMENTS_URL = reverse("list_create_comment")


def sample_movie(title="Great Movie", data={"Year": "1999", "Genre": "Drama"}):
    """Create a sample movie"""
    return Movie.objects.create(title=title, data=data)


def sample_comment(movie, body="Test comment"):
    """Create a sample comment"""
    return Comment.objects.create(movie=movie, body=body)


class CommentsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_comments(self):
        """Test retrieving a list of comments"""
        movie = sample_movie()
        sample_comment(movie)
        sample_comment(movie, body="Test comment 2")

        res = self.client.get(LIST_CREATE_COMMENTS_URL)

        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_comment_successful(self):
        """Test creating a new comment"""
        movie = sample_movie()
        payload = {"movie": movie.id, "body": "Test movie"}
        self.client.post(LIST_CREATE_COMMENTS_URL, payload)

        exists = Comment.objects.filter(movie=payload["movie"]).exists()
        self.assertTrue(exists)

    def test_create_comment_invalid_movie(self):
        """Test creating a new comment with invalid payload"""
        payload = {"movie": "", "body": "Test comment"}
        res = self.client.post(LIST_CREATE_COMMENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_comment_invalid_body(self):
        """Test creating a new comment with invalid payload"""
        movie = sample_movie()
        payload = {"movie": movie.id, "body": ""}
        res = self.client.post(LIST_CREATE_COMMENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_comments_by_movie(self):
        """Test returning comment with specific movie id"""
        movie1 = sample_movie()
        movie2 = sample_movie(title="Another Great Movie", data={"Year": "2000", "Genre": "Comedy"})
        sample_comment(movie1, body="Test comment")
        sample_comment(movie1, body="Test comment 2")
        sample_comment(movie2, body="Test comment 3")

        comments = Comment.objects.filter(movie=movie1.id)

        res = self.client.get(LIST_CREATE_COMMENTS_URL, {"movie_id": movie1.id})

        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(serializer.data, res.data)
