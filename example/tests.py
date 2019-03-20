import datetime
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import Article


class ModelTests(TestCase):

    def setUp(self):
        super().setUp()
        get_user_model().objects.create_superuser('Test', 'Test@qq.com', 'Test')
        a0 = Article.objects.create(title="test-title-0", body="testtesttest")
        a1 = Article.objects.create(title="test-title-1", body="testtesttest")
        a1.articleview.delete()
        a2 = Article.objects.create(title="test-title-2", body="testtesttest")
        self.client = Client()

    def test_model_to_dict(self):
        """
        测试模型的to_dict方法
        """
        article = Article.objects.create(title="test-title", body="testtesttest")

        self.assertEquals(article.to_dict()['create_time'], datetime.date.today().strftime('%Y-%m-%d'))

        self.assertDictEqual(article.to_dict(fields=['title']), {"title": 'test-title'})

        self.assertDictEqual(
            article.to_dict(exclude=['id', 'create_time', 'update_time']),
            {'title': 'test-title', 'body': 'testtesttest', 'is_draft': True}
        )

    def test_api(self):
        print(self.client.get(reverse('api_article')).json())
        print(self.client.get(reverse('api_article') + '?id=1').json())
        print(self.client.get(reverse('api_article') + '?id=2').json())
        print(self.client.post(reverse('api_article'), data={'title': 'test-title-3'}).json())
        self.assertIs(self.client.login(username='Test', password='Test'), True)
        print(self.client.post(reverse('api_article'), data={'title': 'test-title-3'}).json())
