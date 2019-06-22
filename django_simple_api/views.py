from django.forms import ModelForm
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpRequest
from django.conf import settings
from django.db import models
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.views import View
from django.contrib.auth.decorators import permission_required

from . import restful


class SimpleApiView(View):
    # 不允许跨域的方法列表, 但注意, 只能限制标准浏览器的不可跨域
    # 方法名称均为小写, 例如 ['post', 'delete']
    refused_cors_methods = []

    def set_cors_header(self, request: HttpRequest, response: HttpResponse):
        response['Access-Control-Allow-Methods'] = ', '.join(
            set(self._allowed_methods()) - set(self.refused_cors_methods)
        )

        _headers = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', "")
        response['Access-Control-Allow-Headers'] = _headers
        _hosts = settings.CORS_SETTINGS.get('HOSTS', "*")
        response['Access-Control-Allow-Origin'] = ", ".join(_hosts)
        if settings.CORS_SETTINGS.get("COOKIES", False):
            if _hosts == "*":
                response['Access-Control-Allow-Origin'] = request.META.get("HTTP_ORIGIN")
            response['Access-Control-Allow-Credentials'] = 'true'
        return response

    def dispatch(self, request, *args, **kwargs):
        return self.set_cors_header(request, super().dispatch(request, *args, **kwargs))


class PaginatorMixin:
    """提供分页接口"""
    MAX_NUM_PER_PAGE = 10
    IGNORE_EMPTY = True

    def get_paginator(self, objects, count=None, page=None, ignore=None):
        """
        分页器, page不合法时返回第一页, page超出最大页数时返回最后一页
        :param objects:
        :param page: 指定第几页
        :param count: 指定一页最大有多少数据, 默认为 self.MAX_NUM_PER_PAG
        :param ignore: 是否忽略页码错误，True则在错误时返回最后一页信息，否则抛出一个Http404
        :return: Page对象: https://docs.djangoproject.com/zh-hans/2.2/topics/pagination/
        """
        ignore = self.IGNORE_EMPTY if ignore is None else False
        paginator = Paginator(objects, count or self.MAX_NUM_PER_PAGE)
        try:
            page = paginator.page(page)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            if ignore:
                page = paginator.page(paginator.num_pages)
            else:
                raise Http404()
        return page


class LoginRequiredView(SimpleApiView):
    """
    是否需要登陆权限
    """
    login_required = []

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.login_required:
            if request.user.is_authenticated:
                return super().dispatch(request, *args, **kwargs)
        else:
            return super().dispatch(request, *args, **kwargs)
        return self.set_cors_header(request, restful.unauth_error(message='login required'))


class ModelApiView(LoginRequiredView, PaginatorMixin):
    """
    对模型进行操作的Api视图
    """
    # 此Api操作的模型
    Model: models.Model = None
    # 用于 post 方法中处理数据的Form表单
    CreateForm = None
    # 用于 put, patch 方法中处理数据的Form表单
    UpdateForm = None
    # 指定继承哪些操作方法, 需要一个可迭代对象
    # 例如 ('get', 'post', 'delete')
    inherit_methods = ('get', 'post', 'put', 'patch', 'delete')
    # 需要对应权限的方法
    permission_required = []
    # 读取列表时排除的字段
    list_exclude = []

    def __init__(self, **kwargs):
        for each in self.inherit_methods:
            setattr(self, each, getattr(self, '_' + each))
        super().__init__(**kwargs)

        class DefaultForm(ModelForm):
            class Meta:
                model = self.Model
                fields = '__all__'

        self.UpdateForm = self.UpdateForm or DefaultForm
        self.CreateForm = self.CreateForm or DefaultForm

    def dispatch(self, request, *args, **kwargs):
        self.obj = None
        try:
            if kwargs.get('id') is not None:
                self.obj = self.Model.objects.get(id=kwargs['id'])

            return super().dispatch(request)
        except self.Model.DoesNotExist:
            return self.set_cors_header(
                request,
                restful.notfound(message="The requested resource does not exist.")
            )
        except PermissionDenied:
            return self.set_cors_header(
                request,
                restful.forbidden(message="No access")
            )

    def _get(self, request, perms=None):
        if 'get' in self.permission_required:
            if perms is None:
                perms = f"{self.Model._meta.app_label}.view_{self.Model._meta.object_name}"
        else:
            perms = tuple()

        @permission_required(perms, raise_exception=True)
        def inner(request, self):
            if self.obj is not None:
                return restful.success(data=self.obj.to_dict(relation=True, relation_data=True))

            page = self.get_paginator(self.Model.objects.all(), request.GET.get("page"))
            return restful.success(
                data=[obj.to_dict(exclude=self.list_exclude) for obj in page.object_list],
                has_next=page.has_next(),
                has_previous=page.has_previous()
            )

        return inner(request, self)

    def _post(self, request, perms=None):
        if 'post' in self.permission_required:
            if perms is None:
                perms = f"{self.Model._meta.app_label}.add_{self.Model._meta.object_name}"
        else:
            perms = tuple()

        @permission_required(perms, raise_exception=True)
        def inner(request, self):
            form = self.CreateForm(request.DATA, request.FILES)
            if form.is_valid():
                obj = form.save(commit=True)
                return restful.success(message="Successfully new resource.", data=obj.to_dict())
            return restful.params_error(error=form.errors)

        return inner(request, self)

    def _put(self, request, perms=None):
        if 'put' in self.permission_required:
            if perms is None:
                perms = f"{self.Model._meta.app_label}.change_{self.Model._meta.object_name}"
        else:
            perms = tuple()

        @permission_required(perms, raise_exception=True)
        def inner(request, self):
            form = self.UpdateForm(request.DATA, request.FILES, instance=self.obj)
            if form.is_valid():
                obj = form.save(commit=True)
                return restful.success(message="Saved successfully.", data=obj.to_dict())
            return restful.params_error(error=form.errors)

        return inner(request, self)

    def _patch(self, request, perms=None):
        if 'patch' in self.permission_required:
            if perms is None:
                perms = f"{self.Model._meta.app_label}.change_{self.Model._meta.object_name}"
        else:
            perms = tuple()

        @permission_required(perms, raise_exception=True)
        def inner(request, self):
            init_data = model_to_dict(self.obj)
            init_data.update(request.DATA)
            form = self.UpdateForm(init_data, request.FILES, instance=self.obj)
            if form.is_valid():
                obj = form.save(commit=True)
                return restful.success(message="Changed successfully.", data=obj.to_dict())
            return restful.params_error(error=form.errors, status=400)

        return inner(request, self)

    def _delete(self, request, perms=None):
        if 'delete' in self.permission_required:
            if perms is None:
                perms = f"{self.Model._meta.app_label}.delete_{self.Model._meta.object_name}"
        else:
            perms = tuple()

        @permission_required(perms, raise_exception=True)
        def inner(request, self):
            try:
                self.obj.delete()
            except Exception as e:
                return restful.server_error(error=e)
            return restful.success(message="Deleted successfully.")

        return inner(request, self)
