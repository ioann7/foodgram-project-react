from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Subquery
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from core.pagination import LimitPagionation
from core.viewsets import CreateListRetrieveModelViewSet
from users.models import Follow
from users.serializers import (PasswordSerializer, SubscriptionsSerializer,
                               UserCreateSerializer, UserSerializer)
from users.services import SubsriptionCreateDelete

User = get_user_model()


class UserViewSet(CreateListRetrieveModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPagionation
    lookup_url_kwarg = 'user_id'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if user.is_anonymous:
            return queryset
        if self.action in ('retrieve', 'list', 'subscribe',
                           'subscriptions',):
            return queryset.annotate(
                is_subscribed=Exists(Subquery(
                    Follow.objects.filter(user=user, following=OuterRef('pk'))
                ))
            )
        return queryset

    def get_permissions(self):
        if self.action in ('retrieve', 'me', 'set_password',
                           'subscriptions', 'subscribe',):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return PasswordSerializer
        if self.action == 'subscriptions':
            return SubscriptionsSerializer
        return super().get_serializer_class()

    @action(detail=False)
    def me(self, request, *args, **kwargs):
        self.kwargs[self.lookup_url_kwarg] = self.request.user.id
        return self.retrieve(request, *args, **kwargs)

    @action(methods=('post',), detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('get',), detail=False)
    def subscriptions(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset().filter(
                is_subscribed=True
            ).prefetch_related('recipes')
        )

        recipes_limit = request.query_params.get('recipes_limit', '')
        if recipes_limit.isdigit():
            recipes_limit = int(recipes_limit)
        context = self.get_serializer_context()
        context.update({'recipes_limit': recipes_limit})

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)

    @action(methods=('post', 'delete'), detail=True)
    def subscribe(self, request, *args, **kwargs):
        subscription = SubsriptionCreateDelete(request, self.get_queryset(),
                                               self.kwargs.get('user_id'))
        if request.method == 'POST':
            return subscription.create_subscribe()
        return subscription.delete_subscribe()
