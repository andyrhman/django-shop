# services.py
import os
import requests

class UserService:
    # base_url = os.getenv('USERS_MS').rstrip('/')
    base_url = 'http://shop_users:8000'

    @staticmethod
    def get(path, *, headers=None, cookies=None, timeout=None):
        url = f"{UserService.base_url}/api/{path.lstrip('/')}"
        return requests.get(url, headers=headers, cookies=cookies, timeout=timeout)

    @staticmethod
    def post(path, *, json=None, headers=None, cookies=None, timeout=None):
        url = f"{UserService.base_url}/api/{path.lstrip('/')}"
        # ensure Host header has no port
        hdrs = {} if headers is None else dict(headers)
        hdrs['Host'] = 'shop_users'
        return requests.post(
            url,
            json=json,
            headers=hdrs,
            cookies=cookies,
            timeout=timeout,
        )
        
    @staticmethod
    def put(path, *, json=None, headers=None, cookies=None, timeout=None):
        url = f"{UserService.base_url}/api/{path.lstrip('/')}"
        return requests.put(
            url, json=json, headers=headers, cookies=cookies, timeout=timeout
        )
