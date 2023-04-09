from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError
from rest_framework import serializers

from recipes.serializers.nested import RecipeShorthandSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Be sure to annotate `is_subscribed`
    when many=True for optimized queries.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        if hasattr(obj, 'is_subscribed'):
            return obj.is_subscribed
        user = self.context['request'].user
        return (user.is_authenticated
                and obj.following.filter(user=user).exists())


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    default_error_messages = {
        'cannot_create_user': 'Не получается создать пользователя!',
    }

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {'password': serializer_error['non_field_errors']}
            )

        return attrs

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail('cannot_create_user')

        return user

    def perform_create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate_new_password(self, value):
        try:
            validate_password(value, User)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_current_password(self, value):
        is_password_valid = self.context['request'].user.check_password(value)
        if not is_password_valid:
            raise serializers.ValidationError('Invalid password')
        return value


class SubscriptionsSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        queryset = obj.recipes.all()
        recipes_limit = self.context.get('recipes_limit')
        if isinstance(recipes_limit, int) and recipes_limit > 0:
            recipes_limit = min(recipes_limit,
                                settings.RECIPES_MAX_LIMIT_IN_SUBSCRIPTIONS)
            queryset = queryset[:recipes_limit]
        return RecipeShorthandSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
