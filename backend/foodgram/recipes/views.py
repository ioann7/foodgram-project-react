from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Prefetch, Subquery
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from core.pagination import LimitPagionation
from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import CartItem, Favorite, Ingredient, Recipe, Tag
from recipes.serializers.common import (IngredientSerializer,
                                        RecipeCreateSerializer,
                                        RecipeSerializer, TagSerializer)
from recipes.services import (FavoriteCartCreateDelete,
                              ShoppingCartPdfGenerator)
from users.models import Follow

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = LimitPagionation
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_url_kwarg = 'recipe_id'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        user_queryset = User.objects.all()
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(Subquery(
                    Favorite.objects.filter(owner=user, recipe=OuterRef('pk'))
                ))
            ).annotate(
                is_in_shopping_cart=Exists(Subquery(
                    CartItem.objects.filter(owner=user, recipe=OuterRef('pk'))
                ))
            )
            user_queryset = user_queryset.annotate(
                is_subscribed=Exists(Subquery(
                    Follow.objects.filter(user=user, following=OuterRef('pk'))
                ))
            )
        if self.action == 'list':
            return queryset.prefetch_related(
                Prefetch('author', user_queryset)
            ).prefetch_related(
                'tags'
            ).prefetch_related(
                'recipe_ingredient'
            ).prefetch_related(
                'recipe_ingredient__ingredient'
            )
        return queryset

    def get_permissions(self):
        if self.action in ('favorite', 'shopping_cart',
                           'download_shopping_cart',):
            return (IsAuthenticated(),)
        return (IsAuthenticatedOrReadOnly(),)

    def get_serializer_class(self):
        if self.action in ('create', 'update'):
            return RecipeCreateSerializer
        return RecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = RecipeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(author=request.user)
        context = self.get_serializer_context()
        serializer = RecipeSerializer(recipe, context=context)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RecipeCreateSerializer(instance=instance,
                                            data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = serializer.save(author=request.user)
        context = self.get_serializer_context()
        serializer = RecipeSerializer(recipe, context=context)
        return Response(serializer.data)

    @action(methods=('post', 'delete',), detail=True)
    def favorite(self, request, *args, **kwargs):
        favorite = FavoriteCartCreateDelete(
            request,
            self.get_queryset(),
            self.kwargs.get('recipe_id'),
            Favorite,
        )
        if request.method == 'POST':
            return favorite.create()
        return favorite.delete()

    @action(methods=('post', 'delete',), detail=True)
    def shopping_cart(self, request, *args, **kwargs):
        cart_item = FavoriteCartCreateDelete(
            request,
            self.get_queryset(),
            self.kwargs.get('recipe_id'),
            CartItem,
        )
        if request.method == 'POST':
            return cart_item.create()
        return cart_item.delete()

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request, *args, **kwargs):
        pdf_generator = ShoppingCartPdfGenerator()
        return pdf_generator.generate_pdf(request)