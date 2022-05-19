from django.utils import deprecation
from bffile_data import tools as ts
from bfresource_platform import settings as config
from rest_framework.response import Response
from rest_framework import status

class Exception_Middleware(deprecation.MiddlewareMixin):
    def process_exception(self, request, exception):
        result = ts.result_data(status=status.HTTP_500_INTERNAL_SERVER_ERROR,json_date=None,message=str(exception))
        return Response(result)

class ExceptionChange:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if hasattr(response, 'data'):
            data = response.data
            if isinstance(data, dict) is True:
                if "detail" in data.keys():
                    # 用户名或密码错误
                    if data.get("detail") == "Person_info matching query does not exist.":
                        del response.data["detail"]
                        response.data["code"] = 402
                        response.data["msg"] = "用户名或者密码错误"

                    # 验证信息过期 token 过期
                    elif data.get("code") == "token_not_valid":
                        del response.data["detail"]
                        del response.data["messages"]
                        response.data["code"] = 401
                        response.data["msg"] = "登录已过期，请重新登录"

                    else:
                        del response.data["detail"]
                        response.data["code"] = 401
                        response.data["msg"] = "登录已过期，请重新登录"
        return response