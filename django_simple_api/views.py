from django.forms import ModelForm
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpRequest
from django.conf import settings
from django.views import View

from .response import jsonify

__all__ = [
    'SimpleApiView',
    'LoginRequiredView',
    'ModelApiView'
]


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
        _hosts = settings.CORS_SETTINGS.get('hosts', "*")
        response['Access-Control-Allow-Origin'] = ", ".join(_hosts)
        if settings.CORS_SETTINGS.get('cookie', False):
            if _hosts == "*":
                response['Access-Control-Allow-Origin'] = request.META.get("HTTP_ORIGIN")
            response['Access-Control-Allow-Credentials'] = 'true'
        return response

    def dispatch(self, request, *args, **kwargs):
        return self.set_cors_header(request, super().dispatch(request, *args, **kwargs))


class LoginRequiredView(SimpleApiView):
    """
    是否需要登陆权限
    """
    # 为真时, 需要request.user.is_authenticated为真才可访问api
    login_required = True
    # 不需要限制访问的方法
    # 例如 ['get']
    login_unrequired_list = []

    def dispatch(self, request, *args, **kwargs):
        if self.login_required:
            if request.user.is_authenticated or \
                request.method.lower() == "options" or \
                request.method.lower() in self.login_unrequired_list:
                return super().dispatch(request, *args, **kwargs)
        else:
            return super().dispatch(request, *args, **kwargs)
        return self.set_cors_header(request, jsonify(message='未登录', status=401))


class ModelApiView(LoginRequiredView):
    """
    实验性ApiView，随时可能会更改！
    对模型进行操作的Api视图
    """
    # 此Api操作的模型
    Model = None
    # 用于post, put, patch方法中处理数据的Form表单
    Form = None
    # 排除(读取全部数据/创建数据)时返回的部分字段, 需要一个可迭代对象
    # 例如 ('password', 'email')
    # 设计此属性的原因是,模型中可能存在大文本,在读取列表等情况下无需获取
    list_exclude = None
    # 指定继承哪些操作方法, 需要一个可迭代对象
    # 例如 ('get', 'post', 'delete')
    inherit_method_list = tuple()

    def __init__(self, **kwargs):
        for each in self.inherit_method_list:
            setattr(self, each, getattr(self, '_' + each))
        super().__init__(**kwargs)

        if self.Form is None:
            class DefaultForm(ModelForm):
                class Meta:
                    model = self.Model
                    fields = '__all__'

            self.Form = DefaultForm

    def dispatch(self, request, *args, **kwargs):
        self.obj = None
        try:
            if request.GET.get('id') is not None:
                self.obj = self.Model.objects.get(id=request.GET['id'])
            return super().dispatch(request, *args, **kwargs)
        except self.Model.DoesNotExist:
            return self.set_cors_header(
                request,
                jsonify(message="The requested resource does not exist.", status=404)
            )

    def _get(self, request):
        if self.obj is not None:
            return jsonify(data=self.obj.to_dict(relation=True))

        return jsonify([
            obj.to_dict(exclude=self.list_exclude)
            for obj in self.Model.objects.all()
        ])

    def _post(self, request):
        form = self.Form(request.DATA, request.FILES)
        if form.is_valid():
            obj = form.save(commit=True)
            return jsonify(message="Successfully new resource.", data=obj.to_dict(exclude=self.list_exclude))
        return jsonify(error=form.errors, status=400)

    def _put(self, request):
        form = self.Form(request.DATA, request.FILES, instance=self.obj)
        if form.is_valid():
            obj = form.save(commit=True)
            return jsonify(message="Saved successfully.")
        return jsonify(error=form.errors, status=400)

    def _patch(self, request):
        init_data = model_to_dict(self.obj)
        init_data.update(request.DATA)
        form = self.Form(init_data, request.FILES, instance=self.obj)
        if form.is_valid():
            obj = form.save(commit=True)
            return jsonify(message="Changed successfully.")
        return jsonify(error=form.errors, status=400)

    def _delete(self, request):
        try:
            self.obj.delete()
        except Exception as e:
            return jsonify(error=e, status=500)
        return jsonify(message="Deleted successfully.")
