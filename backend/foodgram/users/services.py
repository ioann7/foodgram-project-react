from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from users.models import Follow
from users.serializers import SubscriptionsSerializer

User = get_user_model()


class SubsriptionCreateDelete:
    ERRORS_KEY: str = 'errors'
    CANNOT_SUBSCRIBE_TO_YOURSELF = 'Нельзя подписаться на самого себя!'
    CANNOT_SUBSCRIBE_TWICE = 'Нельзя подписаться дважды!'
    CANNOT_UNSUBSCRIBED_IF_NOT_SUBSCRIBED = (
        'Нельзя отписаться, если не подписан!'
    )

    def __init__(self, request: Request, user_queryset: QuerySet,
                 following_user_id: Optional[int]) -> None:
        self.request: Request = request
        self.user: User = request.user
        self.user_queryset: QuerySet = user_queryset
        self.following_user_id: Optional[int] = following_user_id

    def get_subscription_serializer(self) -> SubscriptionsSerializer:
        queryset = self.user_queryset.prefetch_related('recipes')
        following = self._get_following_or_404(queryset)
        return SubscriptionsSerializer(instance=following)

    def create_subscribe(self) -> Response:
        following = self._get_following_or_404()
        if self.user == following:
            return Response(
                {self.ERRORS_KEY: self.CANNOT_SUBSCRIBE_TO_YOURSELF},
                status.HTTP_400_BAD_REQUEST,
            )
        if self._is_follow_exists(following):
            return Response(
                {self.ERRORS_KEY: self.CANNOT_SUBSCRIBE_TWICE},
                status.HTTP_400_BAD_REQUEST,
            )

        Follow.objects.create(user=self.user, following=following)
        serializer = self.get_subscription_serializer()
        return Response(serializer.data, status.HTTP_201_CREATED)

    def delete_subscribe(self) -> Response:
        following = self._get_following_or_404()
        if not self._is_follow_exists(following):
            return Response(
                {self.ERRORS_KEY: self.CANNOT_UNSUBSCRIBED_IF_NOT_SUBSCRIBED},
                status.HTTP_400_BAD_REQUEST,
            )
        Follow.objects.get(user=self.user, following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _is_follow_exists(self, following: User) -> bool:
        return Follow.objects.filter(
            user=self.user,
            following=following
        ).exists()

    def _get_following_or_404(self,
                              queryset: QuerySet = User.objects.all()) -> User:
        return get_object_or_404(
            queryset,
            id=self.following_user_id,
        )
