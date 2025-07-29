# tests/test_comments.py
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from django_tippanee.models import Comment


class CommentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "password")
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.content_type = ContentType.objects.get(model="user")  # For testing

    def test_create_comment(self):
        data = {
            "content_type": "user",
            "object_id": self.user.id,
            "content": "Test comment",
            "parent": None,
        }
        response = self.client.post("/api/comments/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)

    def test_unauthenticated_create(self):
        self.client.credentials()
        data = {
            "content_type": "user",
            "object_id": self.user.id,
            "content": "Test comment",
            "parent": None,
        }
        response = self.client.post("/api/comments/", data, format="json")
        self.assertEqual(response.status_code, 401)
