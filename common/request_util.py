import requests
from common.log_util import logger


class HttpRequest:
    def __init__(self,base_url:str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def set_token(self,token:str):
        self.session.headers.update({"Authorization":f"Bearer {token}"})

    def send(self,method: str,path: str,**kwargs)->requests.Response:
        url= self.base_url + path
        method= method.upper()
        logger.info(f">>> {method} {url}")
        if "json" in kwargs:
            logger.info(f">>> {kwargs['json']}")
        if "params" in kwargs:
            logger.info(f">>> {kwargs['params']}")

        try:
            resp= self.session.request(method,url,timeout=10,**kwargs)
        except requests.exceptions.Timeout:
            logger.error(f"请求超时：{method} {url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"连接失败：{method} {url}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常：{method} {url} | {e}")
            raise

        logger.info(f"<<< {resp.status_code} | {resp.text[:500]}")
        return resp





