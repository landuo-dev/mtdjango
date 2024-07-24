import time

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

class My1(MiddlewareMixin):

    def process_request(self, request):
        print("process_request")
        # 这里可以对request进行处理
        self.start = time.time()

    def process_response(self, request, response):
        print("process_response", time.time() - self.start)
        # 这里可以对response进行处理

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        print("process_view")
        # 这里可以对view进行处理

    def process_exception(self, request, exception):
        print("process_exception")
        # 这里可以对异常进行处理

    def process_template_response(self, request, response):
        print("process_template_response")
        # 这里可以对template进行处理
        return response





