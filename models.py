from django.db import models

# Create your models here.
from django.db import models
import datetime


# Create your models here.


class Organizational_structure(models.Model):
    classify_id = models.AutoField(primary_key=True)
    classify_choices = (
        (0, '分组'),
        (1, '个人'),
    )
    fclassify_type = models.IntegerField(choices=classify_choices, null=True, blank=True)
    fclassify_id = models.IntegerField(null=True, blank=True)
    classify_name = models.CharField(verbose_name='分类名称', max_length=32, null=True, blank=True)

    class Meta:
        verbose_name = '组织架构'
        verbose_name_plural = verbose_name
        db_table = 'organizational_structure'


class Person_info(models.Model):
    person_id = models.AutoField(primary_key=True)
    person_name = models.CharField(verbose_name='姓名', max_length=32, unique=True)
    password = models.CharField(verbose_name='密码', max_length=32, unique=True)

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    class Meta:
        verbose_name = '个人信息'
        verbose_name_plural = verbose_name
        db_table = 'person_info'

class Person_relationship(models.Model):
    permission_id = models.AutoField(primary_key=True)
    person_id = models.ForeignKey('Person_info', to_field='person_id', db_column='person_id',
                                      verbose_name='个人信息主键id', related_name='prperson_id', on_delete=models.CASCADE)
    person_classify_id = models.ForeignKey('Organizational_structure', to_field='classify_id',
                                            db_column='person_classify_id', verbose_name='组织架构主键id',
                                            related_name='pclassify_label', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "人员关系"
        verbose_name_plural = verbose_name
        db_table = 'person_relationship'


class File_info(models.Model):
    file_id = models.AutoField(primary_key=True)
    ffile_id = models.IntegerField(null=True, blank=True)
    file_name = models.CharField(verbose_name='文件姓名', max_length=255, null=True, blank=True)
    type = models.CharField(verbose_name='文件类型', max_length=32, null=True, blank=True)
    person_id = models.ForeignKey('Person_info', to_field='person_id', db_column='person_id',
                                      verbose_name='个人信息主键id', related_name='fperson_id', on_delete=models.CASCADE)
    is_delete = models.CharField(choices=(('1', '是'), ('0', '否')), max_length=10, default='0', verbose_name='逻辑删除')

    class Meta:
        verbose_name = "文件信息"
        verbose_name_plural = verbose_name
        db_table = 'file_info'
        ordering = ['-file_name']


class File_version(models.Model):
    fversion_id = models.AutoField(primary_key=True)
    file_info_id = models.ForeignKey('File_info', to_field='file_id', verbose_name='文件信息表主键id',
                                     db_column='file_info_id', related_name='fvfile_id', on_delete=models.CASCADE)
    handlers_id = models.ForeignKey('Person_info', to_field='person_id', verbose_name='个人信息主键id',
                                      db_column='handlers_id', related_name='fvperson_id', on_delete=models.CASCADE)
    update_time = models.DateTimeField(verbose_name='更新时间', default=datetime.datetime.now)
    file_url = models.CharField(verbose_name='文件地址', max_length=64, null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)
    file_version = models.IntegerField(null=True, blank=True)
    file_remark = models.TextField(verbose_name='文件备注', null=True, blank=True)
    is_delete = models.CharField(choices=(('1', '是'), ('0', '否')), max_length=10, default='0', verbose_name='逻辑删除')

    class Meta:
        verbose_name = "文件版本"
        verbose_name_plural = verbose_name
        db_table = 'file_version'
        ordering = ['-update_time', '-size']


class Project_details(models.Model):
    project_id = models.AutoField(primary_key=True)
    file_info_id = models.ForeignKey('File_info', to_field='file_id', verbose_name='文件信息表主键id',
                                     db_column='file_info_id', related_name='pdfile_id', on_delete=models.CASCADE)
    is_template = models.CharField(verbose_name='是否套用模板', max_length=32, null=True, blank=True)
    version_num = models.CharField(verbose_name='版本数量', max_length=32, null=True, blank=True)
    remind_info = models.JSONField(verbose_name='提醒信息', null=True, blank=True)

    class Meta:
        verbose_name = "项目明细"
        verbose_name_plural = verbose_name
        db_table = 'project_details'


class Person_permission(models.Model):
    permission_id = models.AutoField(primary_key=True)
    file_info_id = models.ForeignKey('File_info', to_field='file_id', verbose_name='文件信息表主键id',
                                     db_column='file_info_id', related_name='pfile_id', on_delete=models.CASCADE)
    person_id = models.ForeignKey('Person_info', to_field='person_id', verbose_name='个人信息主键id',
                                      db_column='person_id', related_name='pperson_id', on_delete=models.CASCADE)
    permission_choices = (
        (0, '管理者'),
        (1, '负责人'),
        (2, '编辑者'),
        (3, '查看者'),
    )
    fclassify_type = models.IntegerField(choices=permission_choices, null=True, blank=True)

    class Meta:
        verbose_name = '人员权限'
        verbose_name_plural = verbose_name
        db_table = 'person_permission'
