from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from pyautogui import size
import subprocess
r'''

==========求职端搜索字段==========
搜索词----search_terms【0】

名企------famous_enterprise【1】
城市------target_city（default-全国）【2】
薪资------expected_salary【3】
发布时间--release_time（default-不限）【4】
经验------work_experience【5】

====更多====
学历------education【6】
行业------expected_industry【7】
职位类型--expected_position【8】
企业规模--enterprise_scale【9】
融资阶段--financing_stage【10】
企业性质--enterprise_nature【11】

chrome.exe --remote-debugging-port=9222 --user-date-dir="D:\soft\Python\debugchrome"
--new-window liepin.com
'''


# 登入参数
class LoginParameter:
    def __init__(self, ua=None, pd=None):
        self.username = ua
        self.password = pd

    def get_parameter(self):
        return self.username, self.password


# username = '15570335378'
# password = 'pjy13026282913'
# login_result = LoginParameter(username, password)


# 写入基本职位参数
class PositionFundamentalParameter:
    def __init__(self, kw=None):
        self.search_terms = kw['search_terms']
        self.famous_enterprise = kw['famous_enterprise']
        self.target_city_section = kw['target_city_section']
        self.expected_salary = kw['expected_salary']
        self.release_time = kw['release_time']
        self.work_experience = kw['work_experience']
        self.education = kw['education']
        self.expected_industry = kw['expected_industry']
        self.expected_position = kw['expected_position']
        self.enterprise_scale = kw['enterprise_scale']
        self.financing_stage = kw['financing_stage']
        self.enterprise_nature = kw['enterprise_nature']

    # 返回tuple
    def get_parameter(self):
        return self.search_terms, self.famous_enterprise, self.target_city_section, self.expected_salary, self.release_time, \
               self.work_experience, self.education, self.expected_industry, self.expected_position, self.enterprise_scale, \
               self.financing_stage, self.enterprise_nature


# PFP_dict = {
#     'search_terms': '',
#     'famous_enterprise': '',
#     'target_city_section': ['', ''],
#     'expected_salary': ['', '', ''],
#     'release_time': '',
#     'work_experience': '',
#     'education': '',
#     'expected_industry': ['', ''],
#     'expected_position': '',
#     'enterprise_scale': '',
#     'financing_stage': '',
#     'enterprise_nature': ''
# }
#
# position_result = PositionFundamentalParameter(PFP_dict)


# 配置浏览器驱动基本数据
class ConfigureSeleniumParameter:
    def __init__(self, dd, ua, a_eo, s):
        self.dd = dd
        self.ua = ua
        self.a_eo = a_eo
        self.s = s

    # 返回tuple
    def get_value(self):
        return self.dd, self.ua, self.a_eo, self.s


# 配置使用chrome默认用户数据防检测 r'C:\Users\彭家屹\AppData\Local\Google\Chrome\User Data\Default'
default_data = ''
# 配置UA防检测
user_agent = \
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
# 配置接管dos启动debug模式chrome
aeo = ['debuggerAddress', '127.0.0.1:9222']
# aeo = ['--remote-debugging-address', '127.0.0.1:9222']
# 配置消除window.navigator.webdriver值
script = '''
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
})
'''
configure_result = ConfigureSeleniumParameter(default_data, user_agent, aeo, script)


# 调用cmd，命令行远程启动chrome开发模式 https://www.baidu.com/ https://c.liepin.com/
# def cmd_switch(status=True):
#     # 自动获取屏幕大小，窗口最大化（无头模式使用）
#     screen_width, screen_height = size()
#     if status:
#         subprocess.Popen(f'chrome.exe --headless --disable-gpu --window-size="{screen_width},{screen_height}" --remote-debugging-port=9222 https://c.liepin.com/',
#                          shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     else:
#         subprocess.Popen('taskkill /f /t /im chrome.exe', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


# 配置浏览器驱动
def configure_browse_driver():
    options = Options()
    options.add_argument('--user-data-dir=' + configure_result.get_value()[0])
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # options.add_argument('--disable-infobars')
    # options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument('User-Agent=' +
                         configure_result.get_value()[1])
    options.add_argument('--window-size=1920,1080')
    options.add_experimental_option(configure_result.get_value()[2][0], configure_result.get_value()[2][1])
    driver = Chrome(options=options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': configure_result.get_value()[3]})
    return driver
