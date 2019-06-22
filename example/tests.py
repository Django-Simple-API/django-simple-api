import datetime
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.timezone import now
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
        self.assertDictEqual(
            self.client.get(reverse('api_articles')).json(),
            {
                "data": [
                    {'id': 1, 'title': 'test-title-0', 'create_time': datetime.date.today().strftime("%Y-%m-%d"),
                     'update_time': now().strftime("%Y-%m-%d %H:%M:%S"),
                     'is_draft': True},
                    {'id': 2, 'title': 'test-title-1', 'create_time': datetime.date.today().strftime("%Y-%m-%d"),
                     'update_time': now().strftime("%Y-%m-%d %H:%M:%S"),
                     'is_draft': True},
                    {'id': 3, 'title': 'test-title-2', 'create_time': datetime.date.today().strftime("%Y-%m-%d"),
                     'update_time': now().strftime("%Y-%m-%d %H:%M:%S"),
                     'is_draft': True}],
                'has_next': False,
                'has_previous': False
            }
        )
        self.assertDictEqual(
            self.client.get(reverse('api_article', kwargs={"id": 1})).json(),
            {'data': {'articleview': {'id': 1, 'views': 0}, 'image': [], 'id': 1, 'title': 'test-title-0',
                      'create_time': datetime.date.today().strftime("%Y-%m-%d"),
                      'update_time': now().strftime("%Y-%m-%d %H:%M:%S"),
                      'body': 'testtesttest',
                      'corpus': None, 'is_draft': True, 'tags': []}}
        )
        self.assertDictEqual(
            self.client.get(reverse('api_article', kwargs={"id": 2})).json(),
            {'data': {'articleview': None, 'image': [], 'id': 2, 'title': 'test-title-1',
                      'create_time': datetime.date.today().strftime("%Y-%m-%d"),
                      'update_time': now().strftime("%Y-%m-%d %H:%M:%S"), 'body': 'testtesttest', 'corpus': None,
                      'is_draft': True,
                      'tags': []}}
        )
        self.assertDictEqual(
            self.client.post(reverse('api_articles'), data={'title': 'test-title-3'}).json(),
            {'message': 'login required'}
        )
        self.assertIs(self.client.login(username='Test', password='Test'), True)
        self.assertDictEqual(
            self.client.post(reverse('api_articles'), data={'title': 'test-title-3'}).json(),
            {'message': 'Successfully new resource.',
             'data': {'id': 4, 'title': 'test-title-3', 'body': '',
                      'create_time': datetime.date.today().strftime("%Y-%m-%d"),
                      'update_time': now().strftime("%Y-%m-%d %H:%M:%S"), 'is_draft': False}}
        )
