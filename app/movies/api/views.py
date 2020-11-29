import requests
from datetime import datetime

from django.shortcuts import get_object_or_404, get_list_or_404
from django.http.response import Http404

from rest_framework import generics, status
from rest_framework.response import Response

from config.settings import API_URL, API_KEY
from .serializers import CommentSerializer, MovieSerializer
from movies.models import Movie, Comment


class ListCreateMovieAPIView(generics.ListCreateAPIView):
    """Create a new movie in the system, List all movies in the system"""

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()

        kwargs["fields"] = ("id", "title", "data")
        # Pass`data` as ready_only_field so it's not required in the post request
        kwargs["read_only_fields"] = (
            "id",
            "data",
        )
        return MovieSerializer(*args, **kwargs)

    def get_queryset(self):
        """Retrieve the movies"""
        genre = self.request.query_params.get("genre")
        orderby = self.request.query_params.get("orderby")

        # Simple filter based on genres, url example: movies/?genre=Drama, movies/?genre=Drama&genre=Fantasy etc.
        if genre:
            queryset = get_list_or_404(Movie, data__Genre__icontains=genre)
        else:
            queryset = get_list_or_404(Movie)

        # Simple sort by any numeric value, best to use Year or Metascore, url example: movies/?orderby=Year,
        # movies/?orderby=Metascore etc.
        if orderby:
            queryset = queryset.order_by(f"data__{orderby}")

        return queryset

    def create(self, request):
        """Create a movie in database with data fetched from external api"""
        try:
            fetched_data = fetch_movie_data(self.request.data["title"])
        except KeyError:
            return Response({"message": "Movie not found, try different title"}, status=status.HTTP_404_NOT_FOUND)
        except ConnectionError:
            return Response(
                {"message": "Movies database is currently unavailable, please try again later"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Fill the `data` field with fetched data
        serializer.validated_data["data"] = fetched_data
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RetrieveUpdateDestroyMovieAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Update or delete a movie in the system"""

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()

        kwargs["fields"] = (
            "id",
            "title",
            "data",
            "comments",
        )
        kwargs["read_only_fields"] = ("id", "title", "comments")
        return MovieSerializer(*args, **kwargs)

    def get_object(self):
        """Retrieve and return the movie"""
        return get_object_or_404(Movie, pk=self.kwargs.get("id"))

    def destroy(self, *args, **kwargs):
        super().destroy(*args, **kwargs)
        return Response(
            {"message": f"Movie with id {self.kwargs.get('id')} has been deleted."}, status=status.HTTP_200_OK
        )


class ListTopMoviesAPIView(generics.ListAPIView):
    """Retrieve top movies ranked on amount of comments"""

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()

        kwargs["fields"] = ("movie_id", "total_comments", "rank")
        kwargs["read_only_fields"] = ("movie_id", "total_comments", "rank")
        return MovieSerializer(*args, **kwargs)

    def get_queryset(self):
        """Retrieve the ranking"""
        date_format = "%Y-%m-%d"
        date_range_start, date_range_end = (
            datetime.strptime(self.request.query_params.get("start"), date_format),
            datetime.strptime(self.request.query_params.get("end"), date_format),
        )

        if date_range_start > date_range_end:
            raise ValueError
        return Movie.objects.create_ranking(date_range_start, date_range_end)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
        except ValueError:
            return Response(
                {
                    "message": "Date range parameters are invalid. Make sure they have a correct "
                    "format: (YYYY-MM-DD) and Start Date is before End Date. "
                    "Example: top/?start=2020-11-29&end=2020-12-25"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError:
            return Response(
                {
                    "message": (
                        "Please provide date range for which you want to generate a ranking "
                        "Correct format: (YYYY-MM-DD). Example: top/?start=2020-11-29&end=2020-12-25"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if queryset:
            return super().list(request, *args, **kwargs)
        else:
            return Response(
                {"message": "There are no comments for provided date range"},
                status=status.HTTP_404_NOT_FOUND,
            )


class ListCreateCommentAPIView(generics.ListCreateAPIView):
    """Create a new comment in the system, List all comments in the system"""

    serializer_class = CommentSerializer

    def get_queryset(self):
        """Retrieve the comments"""

        # Simple filter based on movie_id, url example: comments/?movie_id=5
        movie_id = self.request.query_params.get("movie_id")
        if movie_id:
            try:
                queryset = get_list_or_404(Comment, movie=int(movie_id))
                return queryset
            except (ValueError, TypeError):
                raise Http404()

        queryset = get_list_or_404(Comment)
        return queryset


def fetch_movie_data(title: str):
    """Fetch data from external movie API"""
    r = requests.get(f"{API_URL}{API_KEY}&t={title}")
    fetched_data = r.json()
    # If movie doesn't exist, field Title also doesn't exist and it
    # raises KeyError which is cought in the create function
    del fetched_data["Title"]

    return fetched_data
