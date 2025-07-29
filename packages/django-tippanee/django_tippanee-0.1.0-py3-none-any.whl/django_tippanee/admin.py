from .models import Comment
from django.contrib import admin


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "content_object",
        "content",
        # "is_approved",
        # "is_flagged",
        "created_at",
    )
    # list_filter = ("is_approved", "is_flagged")
