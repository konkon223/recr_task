from django.urls import path

from movies.api.views import (
    ListCreateMovieAPIView,
    RetrieveUpdateDestroyMovieAPIView,
    ListCreateCommentAPIView,
    ListTopMoviesAPIView,
)

urlpatterns = [
    path("movies/", ListCreateMovieAPIView.as_view(), name="list_create_movie"),
    path("movies/<int:id>", RetrieveUpdateDestroyMovieAPIView.as_view(), name="retrieve_update_destroy_movie"),
    path("comments/", ListCreateCommentAPIView.as_view(), name="list_create_comment"),
    path("top/", ListTopMoviesAPIView.as_view(), name="list_top_movies"),
]
