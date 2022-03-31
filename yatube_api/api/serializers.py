from django.db import IntegrityError
from rest_framework import serializers

from posts.models import Comment, Follow, Group, Post, User


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group

        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Post

        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    class Meta:
        model = Comment

        fields = "__all__"


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        required=True,
        slug_field="username",
    )

    def validate(self, attrs):
        attrs["user"] = self.context["request"].user

        if attrs["user"].id == attrs["following"].id:
            raise serializers.ValidationError(
                "Попытка подписаться на самого себя."
            )

        return attrs

    def save(self, **kwargs):
        try:
            super().save(**kwargs)
        except IntegrityError:
            raise serializers.ValidationError("Подписка уже существует.")

    class Meta:
        model = Follow

        fields = "__all__"
