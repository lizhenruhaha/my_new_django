import json
from bfresource_platform import settings as config
from bffile_data.models import Person_info, Person_permission, \
    Person_relationship, Project_details, File_info, File_version, Organizational_structure
import django_filters
from rest_framework import serializers
from django.db.models.query import QuerySet
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import exceptions
from bffile_data import tools as ts

class File_infoSerializers(serializers.ModelSerializer):
    file_detail = serializers.SerializerMethodField()

    def get_file_detail(self, obj):
        file_version_obj = obj.fvfile_id.filter(is_delete="0").order_by("-file_version").first()
        update_time = str(file_version_obj.update_time)[:16]
        fversion_id = file_version_obj.fversion_id
        handlers_id = file_version_obj.handlers_id.person_id
        handlers_name = file_version_obj.handlers_id.person_name
        size = file_version_obj.size
        file_version = file_version_obj.file_version
        file_url = file_version_obj.file_url
        return {"fversion_id":fversion_id,"update_time": update_time, "handlers_id": handlers_id, "handlers_name": handlers_name, "size": size,
                "file_version": file_version, "file_url": file_url}

    class Meta:
        model = File_info
        fields = ["file_id", "file_name", "type", "file_detail"]


class File_infoFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = File_info
        fields = ['ffile_id']


class File_versionSerializers(serializers.ModelSerializer):
    handlers_id = serializers.SerializerMethodField(read_only=True, required=False)
    handlers_name = serializers.SerializerMethodField(read_only=True, required=False)
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)

    def get_handlers_id(self, obj):
        return obj.handlers_id.person_id if obj.handlers_id else None

    def get_handlers_name(self, obj):
        return obj.handlers_id.person_name if obj.handlers_id else None

    class Meta:
        model = File_version
        fields = ["fversion_id", "file_url", "handlers_id", "handlers_name", "update_time", "file_remark",
                  "file_version", "size"]


class Organizational_structureSerializers(serializers.ModelSerializer):
    members_list = serializers.SerializerMethodField()

    def get_members_list(self, obj):
        cperson_objs = obj.pclassify_label.all()
        members_list = []
        for cperson_obj in cperson_objs:
            person_name = cperson_obj.person_id.person_name
            person_id = cperson_obj.person_id.person_id
            members_list.append({"person_id": person_id, "person_name": person_name})
        return members_list

    class Meta:
        model = Organizational_structure
        fields = ["fclassify_id","classify_id","classify_name","members_list"]

class Person_permissionSerializers(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()
    project_id = serializers.SerializerMethodField()

    def get_project_name(self, obj):
        return obj.file_info_id.file_name if obj.file_info_id else None

    def get_project_id(self, obj):
        return obj.file_info_id.file_id if obj.file_info_id else None

    class Meta:
        model = Person_permission
        fields = ["project_id","project_name"]

class Person_permissionFilter(django_filters.rest_framework.FilterSet):
    project_name = django_filters.CharFilter('file_info_id__file_name',lookup_expr='icontains')

    class Meta:
        model = Person_permission
        fields = ['person_id','project_name']

class Project_detailsSerializers(serializers.ModelSerializer):
    person_permission = serializers.SerializerMethodField()

    def get_person_permission(self,obj):
        file_info_id = obj.file_info_id
        person_permission_objs = Person_permission.objects.filter(file_info_id=file_info_id).query
        person_permission_objs.group_by = ["fclassify_type"]
        person_permission_obj = QuerySet(query=person_permission_objs, model=Person_permission)
        person_permission = {"management_member_list":[],"principal_member_list":[],"redactor_member_list":[],"viewer_member_list":[]}
        for person_permission_ob in person_permission_obj:
            person_id = person_permission_ob.person_id.person_id
            person_name = person_permission_ob.person_id.person_name
            fclassify_type = person_permission_ob.fclassify_type
            if fclassify_type == 0:
                person_permission["management_member_list"].append({"person_id":person_id,"person_name":person_name})
        return person_permission

    class Meta:
        model = Project_details
        fields = ["project_id","file_info_id","is_template","version_num","remind_info","person_permission"]

class Project_detailsFilter(django_filters.rest_framework.FilterSet):

    class Meta:
        model = Project_details
        fields = ['file_info_id']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义登录认证，使用自有用户表
    """
    username_field = 'person_name'

    def validate(self, attrs):
        password = ts.md5_encryption(attrs['password'])
        authenticate_kwargs = {self.username_field: attrs[self.username_field], 'password': password}
        try:
            user = Person_info.objects.get(**authenticate_kwargs)
        except Exception as e:
            raise exceptions.NotFound(e.args[0])
        refresh = self.get_token(user)
        refresh["name"] = user.person_name

        data = {"user_id": user.person_id, "token": str(refresh.access_token), "refresh": str(refresh)}
        return data


class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(label='确认密码', help_text='确认密码',
                                             min_length=6, max_length=20,
                                             write_only=True,
                                             error_messages={
                                                 'min_length': '仅允许6~20个字符的确认密码',
                                                 'max_length': '仅允许6~20个字符的确认密码', })

    class Meta:
        model = Person_info
        fields = ('person_name', 'password', 'password_confirm')
        extra_kwargs = {
            'person_name': {
                'label': '用户名',
                'help_text': '用户名',
                'min_length': 6,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许6-20个字符的用户名',
                    'max_length': '仅允许6-20个字符的用户名',
                }
            },
            'password': {
                'label': '密码',
                'help_text': '密码',
                'write_only': True,
                'min_length': 6,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许6-20个字符的密码',
                    'max_length': '仅允许6-20个字符的密码',
                }
            }
        }

    # 多字段校验：直接使用validate，但是必须返回attrs
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError('密码与确认密码不一致')
        user = Person_info.objects.filter(person_name=attrs.get('person_name')).first()
        if user:
            raise serializers.ValidationError('用户已经存在')
        return attrs
