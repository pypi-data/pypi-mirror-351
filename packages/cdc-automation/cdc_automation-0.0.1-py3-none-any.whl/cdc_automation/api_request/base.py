import requests
from requests.models import Response
import json as JSON
import re
from types import ModuleType
import logging
import inspect
import warnings


class Request:

    def __init__(self, env_info: ModuleType, test_env: str = None):
        """
        Build a Request object
        :param env_info: env_info.py which is record api related info
        :param test_env: if you want to use specific test env in this instance
        """
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        self.session = requests.sessions.Session()
        self.env_info = env_info
        self.url = None
        self.test_config = getattr(env_info, test_env).CONFIG if test_env else getattr(env_info, env_info.TestEnv).CONFIG
        self.logger = logging.getLogger(__name__)

    def re_param(self, url, **kwargs):
        """
        please add own data in env_info.py before used
        """
        if "http" not in url:
            self.url = self.env_info.BuildRequestProperties.build_url(url)
        else:
            self.url = url

        if "headers" not in kwargs:
            self.session.headers = self.env_info.BuildRequestProperties.build_header(url)

    def _custom_logger(self, response):
        def repl(matchobj):
            # print(matchobj.group(0))
            if matchobj.group(0) == "\\":
                return ""
            else:
                return matchobj.group(0)[:-1] + "."
        caller_frame = inspect.currentframe().f_back.f_back
        frame_info = inspect.getframeinfo(caller_frame)
        file_path = re.search(rf"{re.escape(str(self.env_info.project_root_dir))}(.+)", frame_info.filename).group(1)
        function_name = frame_info.function
        line_number = frame_info.lineno

        matched_regex = ".*?\\\\"
        response_log = self.format_res_log(response)
        self.logger.debug(
            f'{re.sub(matched_regex, repl, file_path)}:{function_name}[{line_number}] {JSON.dumps(response_log)}',
            extra=response_log
        )

    def get(self, url, logged=True, **kwargs):
        self.re_param(url, **kwargs)
        res = self.session.get(self.url, **kwargs, verify=False if 'https://' in self.url else None)
        if logged is True:
            self._custom_logger(res)
        return res

    def post(self, url, data=None, json=None, logged=True, **kwargs):
        self.re_param(url, **kwargs)
        res = self.session.post(self.url, data, json, **kwargs, verify=False if 'https://' in self.url else None)
        if logged is True:
            self._custom_logger(res)
        return res

    def put(self, url, data=None, **kwargs):
        self.re_param(url, **kwargs)
        res = self.session.put(self.url, data, **kwargs, verify=False if 'https://' in self.url else None)
        self._custom_logger(res)
        return res

    def delete(self, url, **kwargs):
        self.re_param(url, **kwargs)
        res = self.session.delete(self.url, **kwargs, verify=False if 'https://' in self.url else None)
        self._custom_logger(res)
        return res

    @staticmethod
    def format_res_log(res: Response) -> dict:
        """
        Change Response Obj to log format

        :param res: Response Obj
        :return: log format as dict
        """
        if res.request.method == "GET":
            return {
                "request": {
                    "url": str(res.request.url),
                    "headers": dict(res.request.headers)
                },
                "response": {
                    "headers": dict(res.headers),
                    "body": res.json()
                }
            } if re.search(r"json", res.headers["content-type"]) else {
                "request": {
                    "url": str(res.request.url),
                    "headers": dict(res.request.headers)
                },
                "response": {
                    "headers": dict(res.headers)
                }
            }
        elif res.request.method == "POST":
            return {
                "request": {
                    "url": str(res.request.url),
                    "headers": dict(res.request.headers),
                    "body": JSON.loads(res.request.body) if res.request.headers.get("content-type") == "application/json" else None
                },
                "response": {
                    "headers": dict(res.headers),
                    "body": res.json() if res.headers.get("content-type") and "json" in res.headers.get("content-type") else None
                }
            }
        elif res.request.method == "PUT":
            return {
                "request": {
                    "url": str(res.request.url),
                    "headers": dict(res.request.headers),
                    "body": JSON.loads(res.request.body)
                },
                "response": {
                    "headers": dict(res.headers),
                    "body": res.json() if res.headers.get("content-type") and "json" in res.headers.get("content-type") else None
                }
            }
        elif res.request.method == "DELETE":
            return {
                "request": {
                    "url": str(res.request.url),
                    "headers": dict(res.request.headers)
                },
                "response": {
                    "headers": dict(res.headers),
                    "body": res.json() if res.headers.get("content-type") and "json" in res.headers.get("content-type") else None
                }
            }

