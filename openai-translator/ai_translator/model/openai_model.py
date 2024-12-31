#The user wants me to add comments to the selected Python code. I need to go through the code and add meaningful comments to explain its functionality.```
# Start of Selection
import requests
import simplejson
import time
import os
import openai

from model import Model
from utils import LOG
from openai import OpenAI

class OpenAIModel(Model):
    def __init__(self, model: str, api_key: str):
        """
        初始化 OpenAI 模型。

        Args:
            model (str): 使用的 OpenAI 模型名称。
            api_key (str): OpenAI API 密钥。
        """
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def make_request(self, prompt):
        """
        向 OpenAI API 发送请求并获取翻译结果。

        Args:
            prompt (str): 要发送给 OpenAI 模型的提示。

        Returns:
            tuple[str, bool]: 包含翻译结果和请求是否成功的布尔值的元组。
        """
        attempts = 0
        while attempts < 3:
            try:
                if self.model == "gpt4o":
                    # 使用 chat completions API
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    translation = response.choices[0].message.content.strip()
                else:
                    # 使用 completions API
                    response = self.client.completions.create(
                        model=self.model,
                        prompt=prompt,
                        max_tokens=150,
                        temperature=0
                    )
                    translation = response.choices[0].text.strip()

                return translation, True
            except openai.RateLimitError as e:
                # 达到速率限制时的处理
                attempts += 1
                if attempts < 3:
                    LOG.warning("Rate limit reached. Waiting for 60 seconds before retrying.")
                    time.sleep(60)
                else:
                    raise Exception("Rate limit reached. Maximum attempts exceeded.")
            except openai.APIConnectionError as e:
                # 无法连接到服务器时的处理
                print("The server could not be reached")
                print(e.__cause__)  # an underlying Exception, likely raised within httpx.            except requests.exceptions.Timeout as e:
            except openai.APIStatusError as e:
                # 接收到非 200 范围状态代码时的处理
                print("Another non-200-range status code was received")
                print(e.status_code)
                print(e.response)
            except Exception as e:
                # 处理其他未知异常
                raise Exception(f"发生了未知错误：{e}")
        return "", False
