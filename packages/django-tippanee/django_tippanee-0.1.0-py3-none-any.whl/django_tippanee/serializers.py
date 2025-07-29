# django_tippanee/serializers.py
from rest_framework import serializers
from .models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class CommentSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(), slug_field="model"
    )
    author = UserSerializer(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(), allow_null=True, write_only=True
    )
    replies = serializers.SerializerMethodField()
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "content_type",
            "object_id",
            "content_object",
            "author",
            "content",
            "created_at",
            "updated_at",
            "parent",
            "replies",
        ]

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True).data

    def get_content_object(self, obj):
        # Return basic content object info
        return {"content_type": obj.content_type.model, "object_id": obj.object_id}

    def validate(self, attrs):
        content_type = attrs.get("content_type")
        object_id = attrs.get("object_id")
        parent = attrs.get("parent")

        try:
            content_type.get_object_for_this_type(id=object_id)
        except content_type.model_class().DoesNotExist:
            raise serializers.ValidationError("Invalid content object.")

        if parent:
            if parent.content_type != content_type or parent.object_id != object_id:
                raise serializers.ValidationError(
                    "Parent comment must belong to the same content object."
                )
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["author"] = request.user if request else None
        return super().create(validated_data)
