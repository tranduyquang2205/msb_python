import requests
import json
import time
import datetime
from requests.cookies import RequestsCookieJar
import base64
import re
class MSB:
    def __init__(self,username, password, account_number):
        self.keyanticaptcha = "b8246038ce1540888c4314a6c043dcae"
        self.cookies = RequestsCookieJar()
        self.session = requests.Session()
        self.tokenNo = ''
        self.password = password
        self.username = username
        self.account_number = account_number
        self.is_login = False
    def check_error_message(self,html_content):
        pattern = r'<span style="color: black"><strong>(.*?)</strong></span>'
        match = re.search(pattern, html_content)
        return match.group(1) if match else None
    def extract_tokenNo(self,html_content):
        pattern = r'src="/IBSRetail/servlet/CmsImageServlet\?attachmentId=1&&tokenNo=([a-f0-9-]+)"'
        match = re.search(pattern, html_content)
        return match.group(1) if match else None
    def login(self):
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
            result = self.createTaskCaptcha(base64_captcha_img)
            # captchaText = self.checkProgressCaptcha(json.loads(task)['taskId'])
            if 'prediction' in result and result['prediction']:
                captchaText = result['prediction']
            else:
                return {"status": False, "msg": "Error solve captcha", "data": result}
            payload = 'dse_sessionId='+str(match.group(1))+'&dse_applicationId=-1&dse_pageId=2&dse_operationName=retailUserLoginProc&dse_errorPage=index.jsp&dse_processorState=initial&dse_nextEventName=start&orderId=&_userNameEncode='+self.username+'&_userName='+self.username+'&_password='+self.password+'&_verifyCode='+captchaText
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
                return {
                    'code': 200,
                    'success': True,
                    'message': 'Đăng nhập thành công',
                    'data':{
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
        try:
            return json.loads(response.text)
        except:
            return None

    def get_balance(self):
        if not self.is_login:
            login = self.login()
            if not login['success']:
                return login
        accounts_list = self.get_accounts_list()
        if 'data' in accounts_list:
            for account in accounts_list.get('data', []):
                if account.get('acctNo') == self.account_number:
                    return {'code':200,'success': True, 'message': 'Thành công',
                                    'data':{
                                        'account_number':self.account_number,
                                        'balance':int(account.get('availableBalance'))
                            }}
            return {'code':404,'success': False, 'message': 'account_number not found!'} 
        else:
            return {'code':520 ,'success': False, 'message': 'Unknown Error!'} 


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

    def get_transactions(self,fromDate):
        if not self.is_login:
            login = self.login()
            if not login['success']:
                return login
        payload = "fromDate="+fromDate+"&acctNo="+self.account_number+"&page=1&tokenNo="+self.tokenNo+"&lang=vi_VN"
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
        
        if response.status_code == 401:
            return {'code':401,'success': False, 'message': 'Unauthorized!'}
        
        if response.status_code != 200:
            return {'code':response.status_code,'success': False, 'message': 'Unknown error!'}
        try:
            result = response.json()
        except json.decoder.JSONDecodeError:
            result = {
                "status" : "500"
            }
        if result['status'] == "200" and 'data' in result:
                return {'code':200,'success': True, 'message': 'Thành công',
                            'data':{
                                'transactions':result['data']['history'],
                    }}
        else:
                return {'code':400,'success': False, 'message': 'Bad request!'}


username = "0349206113"
password = "Thach686868@"
fromDate="2024-05-13"
account_number = "80000174859"
msb = MSB(username, password,account_number)
session_raw = msb.login()
print(session_raw)

accounts_list = msb.get_accounts_list()
print(accounts_list)

balance = msb.get_balance()
print(balance)

history = msb.get_transactions(fromDate)
print(history)