import os
import requests
import json
import time
import datetime
from requests.cookies import RequestsCookieJar
import base64
import re
import random
from itertools import cycle
import pickle


class BNAK_MSB:

    def __init__(self, username, password, account_number, proxy_list=None):
        self.bank_code = 'MSB'
        self.UserInfoFolter = os.path.dirname(os.path.abspath(__file__)) + '/data/'+self.bank_code
        if not os.path.exists(self.UserInfoFolter):
            os.makedirs(self.UserInfoFolter)

        self.cookies_file = f"{self.UserInfoFolter}/{account_number}_cookies.pkl"
        self.file = f"{self.UserInfoFolter}/{account_number}.json"
        self.password = password
        self.username = username
        self.account_number = account_number
        self.request_count = 0

        self.cookies = RequestsCookieJar()
        self.session = requests.Session()
        self.tokenNo = ''
        self.is_login = False
        self.time_login = time.time()
        self.proxy_list = proxy_list
        self.proxy_failures = {}  # Track failures for each proxy
        self.proxy_cycle = None  # Initialize as None

        if not os.path.exists(self.file):
            self.save_data()
        else:
            self.parse_data()
            self.username = username
            self.password = password
            self.account_number = account_number
            self.proxy_list = proxy_list
            self.save_data()
            self.load_cookies()

        if self.proxy_list:
            self._reset_proxy_cycle()
        else:
            self.proxies = None

    def _reset_proxy_cycle(self):
        """Reset the proxy cycle with current proxy list"""
        if self.proxy_list:
            self.proxy_cycle = cycle(self.proxy_list)
            self.current_proxy = next(self.proxy_cycle)
            self._set_proxy(self.current_proxy)
        else:
            self.proxies = None
            self.current_proxy = None

    def _set_proxy(self, proxy_info):
        """Helper method to set proxy configuration"""
        if proxy_info:
            proxy_host, proxy_port, username_proxy, password_proxy = proxy_info.split(':')
            self.proxies = {
                'http': f'http://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}',
                'https': f'http://{username_proxy}:{password_proxy}@{proxy_host}:{proxy_port}'
            }
            print(f"Using proxy: {self.proxies}")
        else:
            self.proxies = None
            print("No proxy configured")

    def _handle_request(self, method, url, **kwargs):
        """Handle request with proxy error handling"""
        retry_count = 0
        max_retries = 2
        
        # Always change proxy for new request
        if self.proxy_list:
            try:
                self.current_proxy = next(self.proxy_cycle)
            except StopIteration:
                # If we've gone through all proxies, reset the cycle
                self._reset_proxy_cycle()
            self._set_proxy(self.current_proxy)
        
        while retry_count < max_retries:
            try:
                # Add proxies to kwargs if available
                if self.proxies:
                    kwargs['proxies'] = self.proxies
                response = self.session.request(method, url, **kwargs)
                # Reset failure count on success
                if self.current_proxy:
                    self.proxy_failures[self.current_proxy] = 0
                return response
            except (requests.exceptions.ProxyError, 
                    requests.exceptions.ConnectTimeout,
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.ConnectionError) as e:
                print(f"Proxy error (attempt {retry_count + 1}/{max_retries}): {str(e)}")
                if self.current_proxy and self.proxy_list:
                    # Increment failure count
                    self.proxy_failures[self.current_proxy] = self.proxy_failures.get(self.current_proxy, 0) + 1
                    
                    # Only remove proxy after 2 failures
                    if self.proxy_failures[self.current_proxy] >= 2:
                        self._remove_failed_proxy(self.current_proxy)
                    
                    if self.proxy_list:  # Check if we still have proxies after removal
                        retry_count += 1
                        try:
                            # Get next proxy for retry
                            self.current_proxy = next(self.proxy_cycle)
                        except StopIteration:
                            # If we've gone through all proxies, reset the cycle
                            self._reset_proxy_cycle()
                        self._set_proxy(self.current_proxy)
                        continue
                
                # If no proxies left or no proxy list, try without proxy
                kwargs.pop('proxies', None)
                try:
                    return self.session.request(method, url, **kwargs)
                except Exception as e:
                    print(f"Direct connection error: {str(e)}")
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise
                    continue
            except Exception as e:
                print(f"Request error (attempt {retry_count + 1}/{max_retries}): {str(e)}")
                retry_count += 1
                if retry_count >= max_retries:
                    raise
                continue

    def _remove_failed_proxy(self, proxy_info):
        """Remove a failed proxy from the list"""
        if not self.proxy_list or not proxy_info:
            return
            
        if proxy_info in self.proxy_list:
            self.proxy_list.remove(proxy_info)
            # Remove from failures tracking
            self.proxy_failures.pop(proxy_info, None)
            print(f"Removed failed proxy after 2 failures: {proxy_info}")
            print(f"Remaining proxies: {len(self.proxy_list)}")
            self.save_data()
            
            # Reset proxy cycle with remaining proxies
            self._reset_proxy_cycle()

    def save_data(self):
        data = {
            'username': self.username,
            'password': self.password,
            'account_number': self.account_number,
            'is_login': self.is_login,
            'time_login': self.time_login,
            'tokenNo': self.tokenNo,
            'request_count': self.request_count,
            'proxy_list': self.proxy_list,
            'proxy_failures': self.proxy_failures
        }
        with open(self.file, 'w') as file:
            json.dump(data, file)

    def parse_data(self):
        with open(self.file, 'r') as file:
            data = json.load(file)
            self.username = data['username']
            self.password = data['password']
            self.account_number = data['account_number']
            self.is_login = data['is_login']
            self.time_login = data['time_login']
            self.tokenNo = data['tokenNo']
            self.request_count = data['request_count']
            self.proxy_list = data.get('proxy_list', None)
            self.proxy_failures = data.get('proxy_failures', {})

    def save_cookies(self, s):
        """Save the current session to a file."""
        with open(self.cookies_file, 'wb') as file:
            pickle.dump(self.session.cookies, file)

    def load_cookies(self):
        """Load a session from a file."""
        try:
            with open(self.cookies_file, 'rb') as file:
                loaded_cookies = pickle.load(file)
            self.session.cookies.update(loaded_cookies)
        except Exception as e:
            return False

    def check_error_message(self, html_content):
        pattern = r'<span style="color: black"><strong>(.*?)</strong></span>'
        match = re.search(pattern, html_content)
        return match.group(1) if match else None

    def extract_tokenNo(self, html_content):
        pattern = r'src="/IBSRetail/servlet/CmsImageServlet\?attachmentId=(\d*)&&tokenNo=([a-f0-9-]+?)"'
        match = re.search(pattern, html_content)
        return match.group(2) if match else None

    def doLogin(self):
        url = "https://ebank.msb.com.vn/IBSRetail/Request"
        payload = {}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        response = self._handle_request('GET', url, headers=headers, data=payload, allow_redirects=True, timeout=30)
        pattern = r'dse_sessionId=(.*?)&dse_applicationId=(.*?)&dse_pageId=(.*?)&dse_operationName=(.*?)&dse_errorPage=(.*?)&dse_processorState=(.*?)&dse_nextEventName=(.*?)\';'
        pattern_url = r'window.location.href = \'(.*?)\';'
        match = re.search(pattern, response.text)
        match_url = re.search(pattern_url, response.text)
        if match_url:
            url1 = 'https://ebank.msb.com.vn' + match_url.group(1)
            payload = {}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://ebank.msb.com.vn/IBSRetail/EstablishSession?&fromOpName=retailIndexProc&fromStateName=initial&fromEventName=start',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }
            response = self._handle_request('GET', url1, headers=headers, data=payload, timeout=15)
            base64_captcha_img = self.getCaptcha()
            result = self.createTaskCaptcha(base64_captcha_img)
            if 'prediction' in result and result['prediction']:
                captchaText = result['prediction']
            else:
                return {"status": False, "msg": "Error solve captcha", "data": result}
            payload = 'dse_sessionId=' + str(match.group(1)) + '&dse_applicationId=-1&dse_pageId=2&dse_operationName=retailUserLoginProc&dse_errorPage=index.jsp&dse_processorState=initial&dse_nextEventName=start&orderId=&_userNameEncode=' + self.username + '&_userName=' + self.username + '&_password=' + self.password + '&_verifyCode=' + captchaText
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://ebank.msb.com.vn',
                'Connection': 'keep-alive',
                'Referer': url1,
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }

            response = self._handle_request('POST', "https://ebank.msb.com.vn/IBSRetail/Request", headers=headers, data=payload, timeout=15)
            pattern2 = r'dse_sessionId=(.*?)&dse_applicationId=(.*?)&dse_pageId=(.*?)&dse_operationName=(.*?)&dse_errorPage=(.*?)&dse_processorState=(.*?)&dse_nextEventName=(.*?)&toOpName=(.*?)\';'
            pattern_url2 = r'window.location.href = \'(.*?)\';'
            match2 = re.search(pattern2, response.text)
            match_url2 = re.search(pattern_url2, response.text)
            url2 = 'https://ebank.msb.com.vn' + match_url2.group(1)
            payload = {}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://ebank.msb.com.vn/IBSRetail/Request',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache'
            }
            response = self._handle_request('GET', url2, headers=headers, data=payload, timeout=15)
            check_error_message = self.check_error_message(response.text)
            if check_error_message:
                if 'Tài khoản hoặc mật khẩu không đúng' in check_error_message:
                    return {
                        'code': 444,
                        'success': False,
                        'message': check_error_message
                    }
                if 'Mã Tiếp tục không hợp lệ' in check_error_message:
                    return {
                        'code': 422,
                        'success': False,
                        'message': check_error_message
                    }
                if 'Tài khoản của quý khách đã bị khóa' in check_error_message:
                    return {
                        'code': 449,
                        'success': False,
                        'message': 'Blocked account!'
                    }
                return {
                    'code': 400,
                    'success': False,
                    'message': check_error_message
                }
            else:
                self.tokenNo = self.extract_tokenNo(response.text)
                self.is_login = True
                self.time_login = time.time()
                self.save_data()
                self.save_cookies(self.session.cookies)
                return {
                    'code': 200,
                    'success': True,
                    'message': 'Đăng nhập thành công',
                    'data': {
                        'tokenNo': self.tokenNo
                    }
                }
        else:
            return {
                'code': 520,
                'success': False,
                'message': "Unknown Error!"
            }

    def get_accounts_list(self):
        payload = "acctType='CA'%2C'LN'%2C'SA'&status='ACTV'%2C'DORM'%2C'MATU'&tokenNo=" + self.tokenNo + "&lang=vi_VN"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://ebank.msb.com.vn',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        response = self._handle_request('POST', "https://ebank.msb.com.vn/IBSRetail/account/list.do", headers=headers, data=payload, timeout=10)
        try:
            return json.loads(response.text)
        except:
            return None

    def getBalance(self,retry=0):
        if not self.is_login:
            login = self.doLogin()
            if not login['success']:
                return login
        accounts_list = self.get_accounts_list()
        if accounts_list and 'data' in accounts_list:
            for account in accounts_list.get('data', []):
                if account.get('acctNo') == self.account_number:
                    return {'code': 200, 'success': True, 'message': 'Thành công',
                            'data': {
                                'account_number': self.account_number,
                                'balance': int(account.get('availableBalance')),
                                'totalBalance': int(account.get('availableBalance')),
                            }}
            return {'code': 404, 'success': False, 'message': 'account_number not found!'}
        else:
            retry+=1
            if retry < 2:
                return self.getBalance(retry)
            else:
                self.is_login = False
                self.save_data()
                return {'code': 520, 'success': False, 'message': 'Unknown Error!'}

    def createTaskCaptcha1(self, base64_img):
        url = 'https://ecaptcha.sieuthicode.net/api/captcha/captchatext'
        data = {
            "api_key": "9bf19cdde5b4a2823228da8203e11950",
            "img_base64": base64_img
        }
        response = requests.post(url, data=data)
        return response.text

    def createTaskCaptcha(self, base64_img):
        url_1 = 'https://captcha.pay2world.vip//ibsr'
        url_2 = 'https://captcha1.pay2world.vip//ibsr'
        url_3 = 'https://captcha2.pay2world.vip//ibsr'
        payload = json.dumps({
            "image_base64": base64_img
        })
        headers = {
            'Content-Type': 'application/json'
        }
        for _url in [url_1, url_2, url_3]:
            try:
                response = requests.request("POST", _url, headers=headers, data=payload, timeout=10)
                if response.status_code in [404, 502]:
                    continue
                return json.loads(response.text)
            except:
                continue
        return {}

    def checkProgressCaptcha(self, task_id):
        url = 'https://api.anti-captcha.com/getTaskResult'
        data = {
            "clientKey": "f3a44e66302c61ffec07c80f4732baf3",
            "taskId": task_id
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
        response_json = json.loads(response.text)
        if response_json["status"] != "ready":
            time.sleep(1)
            return self.checkProgressCaptcha(task_id)
        else:
            return response_json["solution"]["text"]

    def getCaptcha(self):
        url = 'https://ebank.msb.com.vn/IBSRetail/servlet/ImageServlet'
        headers = {}
        response = self.session.get(url, headers=headers, proxies=self.proxies, timeout=15)
        return base64.b64encode(response.content).decode('utf-8')

    def getHistories(self, fromDate, toDate,retry=0):
        
        if not self.is_login:
            login = self.doLogin()
            if not login['success']:
                return login
        payload = "fromDate=" + fromDate + "&toDate=" + toDate + "&acctNo=" + self.account_number + "&page=1&tokenNo=" + self.tokenNo + "&lang=vi_VN"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.100.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://ebank.msb.com.vn',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
        response = self._handle_request('POST', "https://ebank.msb.com.vn/IBSRetail/history/byAccount.do", headers=headers, data=payload, timeout=15)
        if response.status_code == 401:
            return {'code': 401, 'success': False, 'message': 'Unauthorized!'}
        if response.status_code != 200:
            return {'code': response.status_code, 'success': False, 'message': 'Unknown error!'}
        try:
            result = response.json()
        except json.decoder.JSONDecodeError:
            result = {
                "status": "500"
            }
        if result and 'status' in result and  result['status'] == "200" and 'data' in result:
            return {'code': 200, 'success': True, 'message': 'Thành công',
                    'data': {
                        'transactions': result['data']['history'],
                    }}
        else:
            retry+=1
            if retry < 2:
                return self.getHistories(fromDate, toDate, retry)
            else:
                self.is_login = False
                self.save_data()
                return {'code': 520, 'success': False, 'message': 'Unknown Error!'}


