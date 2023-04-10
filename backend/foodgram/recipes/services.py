from io import BytesIO
from typing import Optional, Union

import pdfkit
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.models.query import QuerySet
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from recipes.models import CartItem, Favorite, Recipe, RecipeIngredient
from recipes.serializers.nested import RecipeShorthandSerializer

User = get_user_model()


class FavoriteCartCreateDelete:
    ERRORS_KEY: str = 'errors'

    def __init__(self, request: Request, recipe_queryset: QuerySet,
                 recipe_id: Optional[int],
                 model_class: Union[Favorite, CartItem],
                 already_exists_error_message: str,
                 model_not_exists_error_message: str) -> None:
        self.request: Request = request
        self.user: User = self.request.user
        self.recipe_queryset: QuerySet = recipe_queryset
        self.recipe_id: Optional[int] = recipe_id
        self.model_class: Union[Favorite, CartItem] = model_class
        self.already_exists_error_message: str = already_exists_error_message
        self.model_not_exists_error_message: str = (
            model_not_exists_error_message
        )

    def create(self) -> Response:
        recipe = self._get_recipe_or_404()
        if self._is_model_exists(recipe):
            return Response(
                {self.ERRORS_KEY: self.already_exists_error_message},
                status.HTTP_400_BAD_REQUEST
            )
        obj = self.model_class.objects.create(owner=self.user,
                                              recipe=recipe)
        serializer = RecipeShorthandSerializer(obj.recipe)
        return Response(serializer.data, status.HTTP_201_CREATED)

    def delete(self) -> Response:
        recipe = self._get_recipe_or_404()
        if not self._is_model_exists(recipe):
            return Response(
                {self.ERRORS_KEY: self.model_not_exists_error_message},
                status.HTTP_400_BAD_REQUEST
            )
        self.model_class.objects.get(owner=self.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _is_model_exists(self, recipe: Recipe) -> bool:
        return self.model_class.objects.filter(
            owner=self.user, recipe=recipe
        ).exists()

    def _get_recipe_or_404(self) -> Recipe:
        return get_object_or_404(
            self.recipe_queryset,
            id=self.recipe_id,
        )


class ShoppingCartPdfGenerator:

    def generate_pdf(self, request):
        recipes_in_shopping_cart = request.user.shopping_cart.values('recipe')
        unique_ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes_in_shopping_cart
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))
        template = get_template('recipes/shopping_cart.html')
        html = template.render({'unique_ingredients': unique_ingredients})
        options = {
            'page-size': 'Letter',
            'encoding': "UTF-8",
        }
        pdf = pdfkit.from_string(html, False, options)
        buffer = BytesIO(pdf)
        return FileResponse(buffer, filename='shopping_cart.pdf',
                            content_type='application/pdf')
