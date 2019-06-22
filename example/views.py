from django_simple_api.views import ModelApiView
from example.models import Article, Tag, Corpus, Image

__all__ = [
    'ArticleView',
    'TagView',
    'CorpusView',
    'ImageView',
]


class ArticleView(ModelApiView):
    """
    对文章的操作
    """
    Model = Article
    list_exclude = ('body',)
    login_required = ('post', 'put', 'delete', 'patch')
    inherit_method_list = ('get', 'post', 'put', 'delete', 'patch')


class TagView(ModelApiView):
    """
    对标签的操作
    """
    Model = Tag
    login_required = ('post', 'delete')
    inherit_method_list = ['get', 'post', 'delete']


class CorpusView(ModelApiView):
    """
    对文集的操作
    """
    Model = Corpus
    login_required = ('post', 'delete')
    inherit_method_list = ['get', 'post', 'delete']


class ImageView(ModelApiView):
    """
    对引用链接的操作
    """
    Model = Image
    login_required = ('post', 'patch', 'delete')
    inherit_method_list = ['post', 'patch', 'delete']
