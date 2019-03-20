from django.db import models

from django_simple_api.models import ModelSerializationMixin

__all__ = (
    "Tag", 'Corpus', 'Article', 'Image'
)


class Tag(models.Model, ModelSerializationMixin):
    name = models.CharField("标签名", max_length=20, unique=True)

    def __str__(self):
        return self.name


class Corpus(models.Model, ModelSerializationMixin):
    name = models.CharField("文集名", max_length=20, unique=True)

    def __str__(self):
        return self.name


class Article(models.Model, ModelSerializationMixin):
    title = models.CharField("标题", max_length=25, unique=True)
    create_time = models.DateField("创建时间", auto_now_add=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    body = models.TextField("文章内容", blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    corpus = models.ForeignKey(Corpus, on_delete=models.SET_NULL, blank=True, null=True)
    is_draft = models.BooleanField("暂不发表", default=True)

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        ArticleView.objects.create(article=self)


class ArticleView(models.Model, ModelSerializationMixin):
    article = models.OneToOneField(Article, on_delete=models.CASCADE)
    views = models.IntegerField('阅读量', default=0)

    def __str__(self):
        return "{0} - {1}".format(self.article.title, self.views)


class Image(models.Model, ModelSerializationMixin):
    file = models.ImageField('图片', upload_to="upload/")
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.file)
