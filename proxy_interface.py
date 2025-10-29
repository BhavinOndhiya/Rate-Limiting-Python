import requests
import json
import os
from dotenv import load_dotenv
from helper_class import *

class CWEBSHARE:

    def __init__(self):
        # Load .env variables
        load_dotenv()

        self.API_KEY = os.getenv("API_KEY")
        self.BASE_URL = os.getenv("BASE_URL")
        self.PROFILE_URL = os.getenv("PROFILE_URL")
        self.SUBSCRIPTION_URL = os.getenv("SUBSCRIPTION_URL")
        self.CONFIG_URL = os.getenv("CONFIG_URL")
        self.PROXY_LIST_URL = os.getenv("PROXY_LIST_URL")
        self.PROXY_STATS_URL = os.getenv("PROXY_STATS_URL")

        self.helper = Helper()
        self.proxy_list_file = ''

        if not self.API_KEY:
            raise ValueError("❌ API_KEY not found in .env file!")

    def authenticate(self):
        response = requests.get(self.BASE_URL, headers={"Authorization": f"Token {self.API_KEY}"})
        return response.status_code == 200

    def get_user_profile_info(self):
        response = requests.get(self.PROFILE_URL, headers={"Authorization": f"Token {self.API_KEY}"})
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=4))
            return response.json()
        return False

    def get_subscription_info(self):
        response = requests.get(self.SUBSCRIPTION_URL, headers={"Authorization": f"Token {self.API_KEY}"})
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=4))
            return response.json()
        return False

    def get_proxy_configuration_info(self):
        response = requests.get(self.CONFIG_URL, headers={"Authorization": f"Token {self.API_KEY}"})
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=4))
            return response.json()
        return False

    def get_proxy_list(self, proxy_filename):
        self.proxy_list_file = proxy_filename
        page_num = 1
        total_count = 0
        proxies_data = {'date': str(self.helper.get_time_stamp()).split()[0]}
        proxies_list = []

        while True:
            url = f"{self.PROXY_LIST_URL}?page={page_num}"
            response = requests.get(url, headers={"Authorization": f"Token {self.API_KEY}"})
            if response.status_code == 200:
                response = response.json()
                total_count = response['count']
                proxies_list.extend(response['results'])
                if len(proxies_list) >= total_count:
                    break
                page_num += 1
            else:
                return False
        
        proxies_data['proxies'] = proxies_list
        self.helper.write_json_file(proxies_data, self.proxy_list_file)
        return self.proxy_list_file

    def get_proxy_stats(self):
        response = requests.get(self.PROXY_STATS_URL, headers={"Authorization": f"Token {self.API_KEY}"})
        print("CWEBSHARE Proxy Interface Test", response)
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=4))
            return response.json()
        return False


if __name__ == "__main__":
    handle = CWEBSHARE()
    # handle.authenticate()
    # handle.get_user_profile_info()
    handle.get_subscription_info()
    # handle.get_proxy_configuration_info()
    handle.get_proxy_list('proxy.json')
    handle.get_proxy_stats()
