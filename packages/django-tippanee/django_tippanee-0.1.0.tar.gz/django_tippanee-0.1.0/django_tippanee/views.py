# django_tippanee/views.py
from rest_framework import viewsets, filters, serializers
from django_filters.rest_framework import DjangoFilterBackend
from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsAuthorOrStaff


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrStaff]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["content_type", "object_id", "parent"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["created_at"]

    def get_queryset(self):
        return self.queryset.select_related(
            "content_type", "author", "parent"
        ).prefetch_related("replies")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if self.request.user == serializer.instance.author:
            serializer.save()
        else:
            raise serializers.ValidationError("You can only update your own comments.")

    def perform_destroy(self, instance):
        if self.request.user == instance.author:
            instance.delete()
        else:
            raise serializers.ValidationError("You can only delete your own comments.")
