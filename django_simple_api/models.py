import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import models
from django.core.files import File


class ModelSerializationMixin:

    def get_m2m_qs(self, field_name: str, field):
        return field.all()

    def get_o2m_qs(self, field_name: str, field):
        return field.all()

    def get_exclude(self, exclude: [str]) -> []:
        return exclude if exclude else []

    @staticmethod
    def _to_dict(
            self: models.Model,
            fields: [str] = None,
            exclude: [str] = None,
            relation: bool = False,
            relation_data: bool = None,
            raw_data: bool = False
    ):
        """
        将Model对象序列化

        * int, str, float, bool 等对象正常解析
        * DateTimeField 解析为 get_datetime_format 的格式,
        * DateField 解析为 get_date_format 格式
        * FileField, ImageField 等解析为路径字符串

        :param self: 需要序列化的对象
        :param fields: str[] 需要序列化的字段名, 不给值时默认序列化所有字段
        :param exclude: str[] 不需要序列化的字段名
        :param relation: Boolean 为真时序列化关系字段
        :param relation_data: Boolean 为假时仅序列化关系字段的 id, 默认值等于 relation
        :param raw_data: Boolean 为真时将不再将 datetime 等特殊对象转为字符串,而提供原始对象
        :return: dict
        """
        if self is None:
            return None

        result = dict()  # 返回结果
        exclude = getattr(self, "get_exclude", lambda x: [] if x is None else x)(exclude)
        relation_data = relation_data if relation_data is not None else relation

        def get_all_fields():
            if fields is None:
                for field in self._meta.get_fields():
                    if field.name in exclude:
                        continue
                    yield field
            else:
                for field_name in fields:
                    if field_name in exclude:
                        continue
                    yield self._meta.get_field(field_name)

        def if_relation(func):
            # 仅在relation为真时才执行
            def inline(field):
                if not relation:
                    return None
                return func(field)

            return inline

        @if_relation
        def m2m(field):
            if isinstance(field, models.ManyToManyRel):
                if field.related_name is None:
                    field_name = field.name + '_set'
                else:
                    field_name = field.related_name
            else:
                field_name = field.name

            # 自定义规则筛选
            query_set = self.get_m2m_qs(field_name, getattr(self, field_name))

            if relation_data:
                result[field.name] = [self._to_dict(each) for each in query_set]
            else:
                result[field.name] = [each.id for each in query_set]

        @if_relation
        def o2m(field):
            if field.related_name is None:
                field_name = field.name + '_set'
            else:
                field_name = field.related_name

            # 自定义规则筛选
            query_set = self.get_o2m_qs(field_name, getattr(self, field_name))

            if relation_data:
                result[field.name] = [self._to_dict(each) for each in query_set]
            else:
                result[field.name] = [each.id for each in query_set]

        @if_relation
        def o2o(field):
            try:
                if relation_data:
                    result[field.name] = self._to_dict(getattr(self, field.name))
                else:
                    result[field.name] = getattr(self, field.name + '_id')
            except ObjectDoesNotExist:
                result[field.name] = None

        @if_relation
        def m2o(field):
            if relation_data:
                result[field.name] = self._to_dict(getattr(self, field.name))
            else:
                result[field.name] = getattr(self, field.name + '_id')

        def normal(field):
            result[field.name] = getattr(self, field.name)
            if raw_data:
                return
            # 将不能直接用json解析的对象转为字符串
            if isinstance(result[field.name], datetime.datetime):
                result[field.name] = result[field.name].strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(result[field.name], datetime.date):
                result[field.name] = result[field.name].strftime("%Y-%m-%d")
            elif isinstance(result[field.name], (File,)):
                result[field.name] = settings.MEDIA_URL + str(result[field.name])

        for field in get_all_fields():
            if field.many_to_many:
                m2m(field)
            elif field.one_to_many:
                o2m(field)
            elif field.one_to_one:
                o2o(field)
            elif field.many_to_one:
                m2o(field)
            else:
                normal(field)

        return result

    def to_dict(self, *, fields=None, exclude=None, relation=False, relation_data=None, raw_data=False):
        return self._to_dict(
            self,
            fields=fields,
            exclude=exclude,
            relation=relation,
            relation_data=relation_data,
            raw_data=raw_data
        )
