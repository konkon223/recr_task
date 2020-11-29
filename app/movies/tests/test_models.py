from django.test import TestCase

from movies.models import Movie, Comment
from movies.api.serializers import MovieSerializer


def sample_movie(title="Great Movie", data={"Year": "1999", "Genre": "Drama"}):
    """Create a sample movie"""
    return Movie.objects.create(title=title, data=data)


def sample_comment(movie, body="Test comment"):
    """Create a sample comment"""
    return Comment.objects.create(movie=movie, body=body)


class ModelTests(TestCase):
    def test_movie_str(self):
        """Test the movie string representation"""
        movie = sample_movie()

        self.assertEqual(str(movie), movie.title)

    def test_comment_str(self):
        """Test the comment string representation"""
        comment = sample_comment(movie=sample_movie())

        self.assertEqual(str(comment), comment.body)

    def test_movie_create_ranking(self):
        """Test creating a top movies ranking"""
        movie1 = sample_movie()
        movie2 = sample_movie(title="Another Great Movie", data={"Year": "2000", "Genre": "Drama"})
        movie3 = sample_movie(title="Yet Another Great Movie", data={"Year": "2001", "Genre": "Comedy"})
        sample_comment(movie1, body="Test comment")
        sample_comment(movie2, body="Test comment 2")
        sample_comment(movie2, body="Test comment 3")
        sample_comment(movie3, body="Test comment 4")

        correct_ranking = [
            {
                "movie_id": movie2.id,
                "total_comments": 2,
                "rank": 1,
            },
            {
                "movie_id": movie1.id,
                "total_comments": 1,
                "rank": 2,
            },
            {
                "movie_id": movie3.id,
                "total_comments": 1,
                "rank": 2,
            },
        ]

        movies = Movie.objects.create_ranking(start_date="2010-11-27", end_date="3020-11-29")
        serializer = MovieSerializer(movies, many=True, fields=["movie_id", "total_comments", "rank"])
        self.assertEqual(serializer.data, correct_ranking)
