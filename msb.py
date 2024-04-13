import requests
import json
import time
import datetime
from requests.cookies import RequestsCookieJar
import base64
import re
class MSB:
    def __init__(self):
        self.keyanticaptcha = "b8246038ce1540888c4314a6c043dcae"
        self.cookies = RequestsCookieJar()
        self.session = requests.Session()
        self.tokenNo = ''
    def check_error_message(self,html_content):
        pattern = r'<span style="color: black"><strong>(.*?)</strong></span>'
        match = re.search(pattern, html_content)
        return match.group(1) if match else None
    def extract_tokenNo(self,html_content):
        pattern = r'src="/IBSRetail/servlet/CmsImageServlet\?attachmentId=1&&tokenNo=([a-f0-9-]+)"'
        match = re.search(pattern, html_content)
        return match.group(1) if match else None
    def login(self, username, password):
        url = "https://ebank.msb.com.vn/IBSRetail/Request?&dse_sessionId=s2xe-FimkVx4j9lPeztr8eF&dse_applicationId=-1&dse_pageId=1&dse_operationName=retailIndexProc&dse_errorPage=error_page.jsp&dse_processorState=initial&dse_nextEventName=start"

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

        response = self.session.get(url, headers=headers, data=payload,allow_redirects=True)
        pattern = r'dse_sessionId=(.*?)&dse_applicationId=(.*?)&dse_pageId=(.*?)&dse_operationName=(.*?)&dse_errorPage=(.*?)&dse_processorState=(.*?)&dse_nextEventName=(.*?)\';'
        pattern_url = r'window.location.href = \'(.*?)\';'
        match = re.search(pattern, response.text)
        match_url = re.search(pattern_url, response.text)
        
        if match_url:
            url1 = 'https://ebank.msb.com.vn'+match_url.group(1)
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
            response = self.session.get(url1, headers=headers, data=payload)
            base64_captcha_img = self.getCaptcha()
            task = self.createTaskCaptcha(base64_captcha_img)
            time.sleep(1)
            captchaText = self.checkProgressCaptcha(json.loads(task)['taskId'])
            payload = 'dse_sessionId='+str(match.group(1))+'&dse_applicationId=-1&dse_pageId=2&dse_operationName=retailUserLoginProc&dse_errorPage=index.jsp&dse_processorState=initial&dse_nextEventName=start&orderId=&_userNameEncode='+username+'&_userName='+username+'&_password='+password+'&_verifyCode='+captchaText
            # payload = 'dse_sessionId='+str(match.group(1))+'&dse_applicationId=-1&dse_pageId=2&dse_operationName=retailUserLoginProc&dse_errorPage=index.jsp&dse_processorState=initial&dse_nextEventName=start&orderId=&_userNameEncode=11111&_userName=11111&_password=2222&_verifyCode=8461'            
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

            response = self.session.post("https://ebank.msb.com.vn/IBSRetail/Request", headers=headers, data=payload)

            pattern2 = r'dse_sessionId=(.*?)&dse_applicationId=(.*?)&dse_pageId=(.*?)&dse_operationName=(.*?)&dse_errorPage=(.*?)&dse_processorState=(.*?)&dse_nextEventName=(.*?)&toOpName=(.*?)\';'
            pattern_url2 = r'window.location.href = \'(.*?)\';'
            match2 = re.search(pattern2, response.text)
            match_url2 = re.search(pattern_url2, response.text)
            url2 = 'https://ebank.msb.com.vn'+match_url2.group(1)
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
            response = self.session.get(url2, headers=headers, data=payload)
            check_error_message = self.check_error_message(response.text)
            if check_error_message:
                return {
                    'code': 400,
                    'success': False,
                    'message': check_error_message
                }
            else:
                self.tokenNo = self.extract_tokenNo(response.text)
                return {
                    'code': 200,
                    'success': True,
                    'message': 'Đăng nhập thành công',
                    'tokenNo': self.tokenNo
                }

    def get_accounts_list(self):
        payload = "acctType='CA'%2C'LN'%2C'SA'&status='ACTV'%2C'DORM'%2C'MATU'&tokenNo="+self.tokenNo+"&lang=vi_VN"
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

        response = self.session.post("https://ebank.msb.com.vn/IBSRetail/account/list.do", headers=headers, data=payload)

        return json.loads(response.text)

    def get_balance(self,account_number):
        accounts_list = self.get_accounts_list()
        for account in accounts_list.get('data', []):
            if account.get('acctNo') == account_number:
                return {
                    'account_number':account_number,
                    'available_balance':account.get('availableBalance')
                }
        return None


    def createTaskCaptcha1(self, base64_img):
        url = 'https://ecaptcha.sieuthicode.net/api/captcha/captchatext'
        data = {
            "api_key": "9bf19cdde5b4a2823228da8203e11950",
            "img_base64": base64_img
        }
        response = requests.post(url, data=data)
        return response.text
    def createTaskCaptcha(self, base64_img):
            url = "https://api.anti-captcha.com/createTask"

            payload = json.dumps({
            "clientKey": "f3a44e66302c61ffec07c80f4732baf3",
            "task": {
                "type": "ImageToTextTask",
                "body": base64_img,
                "phrase": False,
                "case": False,
                "numeric": 0,
                "math": False,
                "minLength": 0,
                "maxLength": 0
            },
            "softId": 0
            })
            headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)
            return(response.text)

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
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_json = json.loads(response.text)
        print(response_json)
        if response_json["status"] != "ready":
            time.sleep(1)
            return self.checkProgressCaptcha(task_id)
        else:
            return response_json["solution"]["text"]
    def getCaptcha(self):
        url = 'https://ebank.msb.com.vn/IBSRetail/servlet/ImageServlet'
        headers = {}
        response = self.session.get(url, headers=headers)
        return base64.b64encode(response.content).decode('utf-8')

    def get_transactions(self,account_number,fromDate):
        payload = "fromDate="+fromDate+"&acctNo="+account_number+"&page=1&tokenNo="+self.tokenNo+"&lang=vi_VN"
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

        response = self.session.post("https://ebank.msb.com.vn/IBSRetail/history/byAccount.do", headers=headers, data=payload)

        return(response.text)

msb = MSB()
username = "0972841903"
password = "Khai4455@"
fromDate="2024-04-12"
account_number = "02001016649139"

session_raw = msb.login(username, password)
print(session_raw)

# accounts_list = msb.get_accounts_list()
# print(accounts_list)

# balance = msb.get_balance(account_number)
# print(balance)

# history = msb.get_transactions(account_number,fromDate)
# print(history)