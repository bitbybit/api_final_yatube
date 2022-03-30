from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from posts.models import Comment, Follow, Group, Post, User
from rest_framework import filters, permissions, response, status, viewsets
from rest_framework.pagination import LimitOffsetPagination

from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CommentSerializer,
    FollowSerializer,
    GroupSerializer,
    PostSerializer,
)
from .viewsets import CreateListModelViewSet


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.action == "retrieve" or self.action == "list":
            return (permissions.IsAuthenticatedOrReadOnly(),)

        return super().get_permissions()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated, IsAuthorOrReadOnly)
    pagination_class = LimitOffsetPagination

    def get_permissions(self):
        if self.action == "retrieve" or self.action == "list":
            return (permissions.IsAuthenticatedOrReadOnly(),)

        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated, IsAuthorOrReadOnly)

    def get_permissions(self):
        if self.action == "retrieve" or self.action == "list":
            return (permissions.IsAuthenticatedOrReadOnly(),)

        return super().get_permissions()

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])

        return post.comments

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])

        serializer.save(author=self.request.user, post=post)


class FollowViewSet(CreateListModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )
    search_fields = ("following__username",)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        following_username = self.request.data.get("following")

        if following_username is None:
            return response.Response(
                {"message": "Отсутствует поле following."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        following = get_object_or_404(User, username=following_username)

        if self.request.user.id == following.id:
            return response.Response(
                {"message": "Попытка подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except IntegrityError:
            return response.Response(
                {"message": "Подписка уже существует."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        following = User.objects.get(username=self.request.data["following"])

        serializer.save(user=self.request.user, following=following)
