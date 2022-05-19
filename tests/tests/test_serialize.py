from django.test import TestCase
from django.contrib.auth.models import User


class TestSerialize(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='Zhang', email="111@163.com")

    def test_serialize_model(self):
        user = User.objects.get(username='Zhang')
        assert isinstance(user.to_json(), dict)

    def test_serialize_queryset(self):
        users = User.objects.filter(username='Li')
        assert isinstance(users.to_json(), list)
