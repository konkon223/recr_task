from rest_framework import serializers

from movies.models import Movie, Comment


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` and `read_only_fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        read_only_fields = kwargs.pop("read_only_fields", None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        #  Take care of read_only fields
        if read_only_fields is not None:
            for f in read_only_fields:
                try:
                    self.fields[f].read_only = True
                except KeyError:
                    # not in fields anyway
                    pass


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for the comment object"""

    class Meta:
        model = Comment
        fields = ("movie", "body", "created")
        read_only_fields = ("created",)


class MovieSerializer(DynamicFieldsModelSerializer):
    """Serializer for the movie object"""

    comments = serializers.StringRelatedField(many=True)
    total_comments = serializers.IntegerField()
    rank = serializers.IntegerField()
    movie_id = serializers.IntegerField(source="id")

    class Meta:
        model = Movie
        fields = ("id", "movie_id", "title", "data", "total_comments", "rank", "comments")
        read_only_fields = ("id", "movie_id", "total_comments", "rank", "comments")

    def create(self, validated_data):
        """Create a new movie with and return it"""
        return Movie.objects.create(**validated_data)
