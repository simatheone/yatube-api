from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from posts.models import Comment, Follow, Group, Post, User

SELF_FOLLOWING_ERROR = 'Пользователь не может подписаться сам на себя.'
DOUBLE_FOLLOWING_ERROR = 'Нельзя дважды подписаться на одного юзера.'


class PostSerializer(serializers.ModelSerializer):
    """Cериализатор для модели Post."""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'text', 'group', 'author', 'pub_date', 'image')
        read_only_fields = ('id', 'pub_date', 'image')


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Group."""

    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description')
        read_only_fields = ('id', 'title', 'slug', 'description')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Comment."""
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'post', 'text', 'created')
        read_only_fields = ('id', 'post', 'created')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализотор модели Follow."""
    following = serializers.SlugRelatedField(
        slug_field='username', queryset=User.objects.all()
    )
    user = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Follow
        fields = ['user', 'following']

    def validate(self, data):
        following_request_value = data.get('following')
        request_user = self.context.get('request').user
        subscription_in_db_exists = Follow.objects.filter(
            user=request_user, following=following_request_value).exists()

        if following_request_value == request_user:
            raise serializers.ValidationError(SELF_FOLLOWING_ERROR)
        elif subscription_in_db_exists:
            raise serializers.ValidationError(DOUBLE_FOLLOWING_ERROR)
        return data
