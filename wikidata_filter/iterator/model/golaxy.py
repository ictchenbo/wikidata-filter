"""
中国科学院计算所天玑团队自主研发训练的大模型服务

注意，接口与OpenAI不兼容
"""
import sys
import requests
from .base import LLM


class GoGPT(LLM):
    def __init__(self,
                 api_base: str = "localhost:8888",
                 field: str = None,
                 ignore_errors: bool = True,
                 prompt: str = None,
                 target_key: str = '_llm'):
        super().__init__(api_base=api_base, field=field, ignore_errors=ignore_errors, prompt=prompt, target_key=target_key)

    def request_service(self, query: str):
        try:
            res = requests.post(self.api_base, json={'prompt': query})
            if res.status_code == 200:
                return res.json()['response'].strip()
            print(res.text, file=sys.stderr)
            return None
        except:
            print("Request Error")
            if self.ignore_errors:
                return None
            raise Exception(f"Access {self.api_base} Error!")
