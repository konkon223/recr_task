from django.db import models
from django.db.models.aggregates import Count
from django.db.models import F, Window
from django.db.models.functions.window import DenseRank


class MovieManager(models.Manager):
    def create_ranking(self, start_date, end_date):
        """Create movies ranking for specified date range, based on amount of comments"""
        dense_rank = Window(expression=DenseRank(), order_by=F("total_comments").desc())
        queryset = Movie.objects.filter(comments__created__date__range=[start_date, end_date])

        return queryset.annotate(total_comments=Count("comments")).annotate(rank=dense_rank)


class Movie(models.Model):

    title = models.CharField(max_length=250, unique=True)
    data = models.JSONField()
    # There are also other options, such as:
    # - rewriting manually every key/value pair from the json response into
    # the Model fields but I don't think it's needed for the task
    # - dynamically create fields based on the response but I believe it's
    # too complicated and it's not the purpose of the task

    objects = MovieManager()

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title


# This class and all other logic like serializers, views etc. could be also in a different Django app,
# but I believe it's not necessary for this task
class Comment(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.body
