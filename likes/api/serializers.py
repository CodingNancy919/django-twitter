from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from tweets.models import Tweet
from comments.models import Comment
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import ValidationError
from accounts.api.serializers import UserSerializerForTweet


class LikeSerializerForCreate(ModelSerializer):
    content_type = serializers.ChoiceField(['tweet', 'comment'])
    object_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('content_type', 'object_id',)

    def _get_model_class(self, data):
        if data['content_type'] == 'tweet':
            return Tweet
        if data['content_type'] == 'comment':
            return Comment
        return None

    def validate(self, data):
        model_class = self._get_model_class(data)
        if model_class is None:
            raise ValidationError({'content_type': 'Content type does not exist'})
        content_object = model_class.objects.filter(id=data['object_id']).first()
        if content_object is None:
            raise ValidationError({'object_id': 'Object does not exist'})
        return data

    def create(self, validated_data):
        model_class = self._get_model_class(validated_data)
        instance, _ = Like.objects.get_or_create(
            user=self.context['request'].user,
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'])
        return instance


class LikeSerializer(ModelSerializer):
    user = UserSerializerForTweet

    class Meta:
        model = Like
        fields = ('user', 'created_at',)


