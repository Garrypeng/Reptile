from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
from time import sleep
import cv2
import requests


# 登录界面定位操作
class SpiderLiePinWeb_Login_Terms:
    def __init__(self, lr, driver):
        self.lr = lr
        self.driver = driver

    # 用户密码登录 Web登陆失败提示class：anticon anticon-close-circle
    def login(self):
        sleep(2)
        # 判断是否勾选同意协议框
        if 'ant-checkbox-checked' not in self.driver.find_element(By.CLASS_NAME, 'ant-checkbox').get_attribute('class'):
            self.driver.find_element(By.CLASS_NAME, 'login-agreement-text').click()
        # 判断是否是“密码登录界面”
        if self.driver.find_element(By.CLASS_NAME, 'active').get_attribute('textContent') in '登录/注册':
            self.driver.find_elements(By.CLASS_NAME, 'jsx-1730583093')[3].click()
        # 删除用户/密码框所有内容
        else:
            self.driver.find_element(By.ID, 'login').send_keys(Keys.CONTROL, 'a')
            self.driver.find_element(By.ID, 'login').send_keys(Keys.DELETE)
            self.driver.find_element(By.ID, 'pwd').send_keys(Keys.CONTROL, 'a')
            self.driver.find_element(By.ID, 'pwd').send_keys(Keys.DELETE)
        self.driver.find_element(By.ID, 'login').send_keys(self.lr.get_parameter()[0])
        self.driver.find_element(By.ID, 'pwd').send_keys(self.lr.get_parameter()[1])
        self.driver.find_element(By.CLASS_NAME, 'login-submit-btn').click()

    # 滑块信息获取/验证
    def slider(self):
        self.driver.implicitly_wait(5)
        self.driver.switch_to.frame('tcaptcha_iframe')
        # [-11:] height: 68px; width: 68px; top: 15px; left: 26px;
        block_subscript = 0
        block_position_left = ''
        sleep(2)
        block_position_str = self.driver.find_element(By.ID, 'slideBlock').get_attribute('style')
        # 获取滑块左边界距离
        if 'left' in block_position_str:
            for item in block_position_str:
                block_subscript += 1
                if item == 'l':
                    block_position_left = block_position_str[block_subscript+5:block_subscript+7]
                    break
        else:
            print('未能获取到滑块左边距')
        solid = self.driver.find_element(By.ID, 'tcaptcha_drag_thumb')
        # 获取渲染的背景图尺寸
        bg_rendered_width = self.driver.find_element(By.ID, 'slideBg').size['width']
        # 匹配小于350px为失败，刷新图片重新匹配
        while True:
            # 获取背景图和缺口图
            bg_url = self.driver.find_element(By.ID, 'slideBg').get_attribute('src')
            tp_url = self.driver.find_element(By.ID, 'slideBlock').get_attribute('src')
            SpiderLiePinWeb_Login_Terms.download_img(bg_url, tp_url)
            bg_gap = SpiderLiePinWeb_Login_Terms.identify_gap('img/bg.jpg', 'img/tp.png', 'img/result.jpg')
            # 获得原图尺寸
            bg_width = Image.open('img/bg.jpg').size[0]
            # 渲染图和原图比例
            rate = (bg_rendered_width * 1.0) / bg_width
            if bg_gap < 350:
                self.driver.find_element(By.CLASS_NAME, 'tc-action-icon').click()
                sleep(2)
            else:
                # 背景图缺口距离左边界的距离
                move_gap = int(rate * bg_gap)
                break
        # 最终滑块移动距离
        final_distance = move_gap-int(block_position_left)
        # 移动滑块
        ActionChains(self.driver).drag_and_drop_by_offset(solid, final_distance, 0).release(solid).perform()
        self.driver.switch_to.parent_frame()
        sleep(3)
        # 成功登录后获取姓名，成功Tru，失败False
        name = False
        try:
            self.driver.find_element(By.CLASS_NAME, 'header-quick-menu-username').get_attribute('textContent')
            name = True
        except NoSuchElementException:
            pass
        finally:
            return name

    @staticmethod
    # opencv处理图片得到实际需要滑行的距离，bg-背景图片 tp-缺口图片
    def identify_gap(bg, tp, out):
        try:
            # 读取背景图片和缺口图片
            bg_img = cv2.imread(bg)  # 背景图片
            tp_img = cv2.imread(tp)  # 缺口图片
            # 识别图片边缘
            bg_edge = cv2.Canny(bg_img, 100, 200)
            tp_edge = cv2.Canny(tp_img, 100, 200)
            # 转换图片格式
            bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
            tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
            # 缺口匹配
            res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
            # 绘制方框
            th, tw = tp_pic.shape[:2]
            tl = max_loc  # 左上角点的坐标
            br = (tl[0] + tw, tl[1] + th)  # 右下角点的坐标
            cv2.rectangle(bg_img, tl, br, (0, 0, 255), 2)  # 绘制矩形
            cv2.imwrite(out, bg_img)  # 保存在本地
            # 返回缺口的X坐标
            return tl[0]
        except cv2.error:
            print('图片距离计算方法错误（identify_gap）')
        finally:
            pass

    @staticmethod
    # requests获取保存背景图和缺口图
    def download_img(bg_url=None, tp_url=None):
        try:
            bg_r = requests.get(bg_url, stream=True)
            tp_r = requests.get(tp_url, stream=True)
            if bg_r.status_code == 200:
                # 背景图
                with open('img/bg.jpg', 'wb') as file:
                    file.write(bg_r.content)
                # 缺口图
            if tp_r.status_code == 200:
                with open('img/tp.png', 'wb') as file:
                    file.write(tp_r.content)
        except requests.exceptions.MissingSchema:
            print('图片地址获取失败（download_img）')
        finally:
            pass


# 个人简历项定位操作
class SpiderLiePinWeb_Personal_Terms:
    def __init__(self, driver):
        self.driver = driver

    def resume_content(self):
        # https://c.liepin.com/resume/getdefaultresume/
        # 获取个人简历链接
        # personal_resume_url = self.driver.find_element(By.ID, 'header-quick-menu-resume').get_attribute('href')
        # parent_window = self.driver.current_window_handle
        # 创建新的标签页
        # self.driver.switch_to.new_window('tab')
        # windows = self.driver.window_handles
        # self.driver.switch_to.window(windows[0])
        # self.driver.switch_to.window(parent_window)

        # 鼠标悬浮显示下拉框
        ActionChains(self.driver).move_to_element(self.driver.find_element(By.ID, 'header-quick-menu-user-info')).perform()
        self.driver.find_element(By.ID, 'header-quick-menu-resume').click()
        sleep(2)

        # 个人优势
        personal_advantages = self.driver.find_element(By.CLASS_NAME, 'assess-content').get_attribute('textContent')
        # print(personal_advantages, end='\n')

        # 工作经验
        work_experience = self.driver.find_element(By.CLASS_NAME, 'item-content-duty').get_attribute('textContent')
        # print(work_experience, end='\n')

        # 项目经验标题
        project_experience_titles = self.driver.find_element(By.CLASS_NAME, 'project-exp-container').find_elements(By.CLASS_NAME, 'item-title')
        project_experience_title = []
        for title_item in project_experience_titles:
            project_experience_title.append(title_item.get_attribute('textContent'))
        # print(project_experience_title, end='\n')

        # 项目经验内容
        project_experience_contents = self.driver.find_element(By.CLASS_NAME, 'project-exp-container').find_elements(By.CLASS_NAME, 'item-content')
        project_experience_content = []
        for content_item in project_experience_contents:
            project_experience_content.append(content_item.get_attribute('textContent'))
        # print(project_experience_content, end='\n')

        # 技能卡片
        skill_labels = self.driver.find_elements(By.CLASS_NAME, 'skill-label')
        skill_label = []
        for skill_item in skill_labels:
            skill_label.append(skill_item.get_attribute('textContent'))
        # print(skill_label, end='\n')


# 搜索项元素定位操作
class SpiderLiePinWeb_Search_Terms:
    def __init__(self, pr, driver):
        self.pr = pr
        self.driver = driver
        self.driver.find_element(By.ID, 'header-nav-menu-job').click()

    # 字段可选项汇聚为列表
    def search_lists(self):
        div = self.driver.find_elements(By.CLASS_NAME, 'options-row')
        # for item in div:
        #     print(item.find_element(By.CLASS_NAME, 'row-title').get_attribute('textContent'))
        return div

    # 操作搜寻相关职位模块【0】
    def operation_search_position(self):
        # self.driver.refresh()
        sleep(3)
        move = self.driver.find_element(By.CLASS_NAME, 'jsx-3599059289')
        ActionChains(self.driver).move_to_element(move).click().perform()
        search_value = move.find_element(By.TAG_NAME, 'input').get_attribute('value')
        if search_value:
            ActionChains(self.driver).key_down(Keys.CONTROL).perform()
            ActionChains(self.driver).send_keys('a').perform()
            ActionChains(self.driver).key_up(Keys.CONTROL).perform()
            ActionChains(self.driver).send_keys(Keys.DELETE).perform()
        # search_terms字段
        ActionChains(self.driver).send_keys(self.pr.get_parameter()[0]).send_keys(Keys.ENTER).perform()

    # famous_enterprise字段【1】
    def famous_enterprise(self, div):
        if '公司' in div[0].find_element(By.CLASS_NAME, 'row-title').get_attribute('textContent'):
            li = div[1].find_elements(By.CLASS_NAME, 'options-item')
        else:
            li = div[0].find_elements(By.CLASS_NAME, 'options-item')
        if '财富中国500强' in self.pr.get_parameter()[1]:
            li[0].click()
        elif '创新企业100强' in self.pr.get_parameter()[1]:
            li[1].click()
        elif '制造业500强' in self.pr.get_parameter()[1]:
            li[2].click()
        elif '专精特新企业' in self.pr.get_parameter()[1]:
            li[3].click()
        elif '高新技术企业' in self.pr.get_parameter()[1]:
            li[4].click()
        elif '独角兽' in self.pr.get_parameter()[1]:
            li[5].click()
        else:
            print('未能匹配到相关"名企"选项！请更正字段值！')

    # target_city（default-全国）字段【2】
    def target_city(self, div):
        section_val = 1
        if '名企' in div[1].find_element(By.CLASS_NAME, 'row-title').get_attribute('textContent'):
            li = div[2].find_elements(By.CLASS_NAME, 'options-item')
        else:
            li = div[1].find_elements(By.CLASS_NAME, 'options-item')
        if '北京' in self.pr.get_parameter()[2][0]:
            li[1].click()
        elif '上海' in self.pr.get_parameter()[2][0]:
            li[2].click()
        elif '天津' in self.pr.get_parameter()[2][0]:
            li[3].click()
        elif '重庆' in self.pr.get_parameter()[2][0]:
            li[4].click()
        elif '广州' in self.pr.get_parameter()[2][0]:
            li[5].click()
        else:
            section_val = 0
            print('未能匹配到相关"城市"选项！请更正字段值！')
        sleep(3)
        if section_val != 0:
            # section_div = self.driver.find_element(By.XPATH, '//*[@id="lp-search-job-box"]/div[2]/div[1]/div[4]')
            # section_li = section_div.find_elements(By.CLASS_NAME, 'options-item')
            # for item in section_li:
            #     print(item.get_attribute('textContent'))
            section_div = self.driver.find_elements(By.CLASS_NAME, 'options-row')
            section_li = section_div[3].find_elements(By.CLASS_NAME, 'options-item')
            # for item in section_li:
            #     print(item.get_attribute('textContent'))
            if '黄浦区' in self.pr.get_parameter()[2][1]:
                section_li[1].click()
            elif '徐汇区' in self.pr.get_parameter()[2][1]:
                section_li[2].click()
            elif '长宁区' in self.pr.get_parameter()[2][1]:
                section_li[3].click()
            elif '普陀区' in self.pr.get_parameter()[2][1]:
                section_li[4].click()
            elif '虹口区' in self.pr.get_parameter()[2][1]:
                section_li[5].click()
            elif '杨浦区' in self.pr.get_parameter()[2][1]:
                section_li[6].click()
            elif '闵行区' in self.pr.get_parameter()[2][1]:
                section_li[7].click()
            else:
                print('未能匹配到相关"区域"选项！请更正字段值！')

    # expected_salary字段【3】————自定义为活标签
    def expected_salary(self, div):
        if '城市' in div[2].find_element(By.CLASS_NAME, 'row-title').get_attribute('textContent'):
            li = div[3].find_elements(By.CLASS_NAME, 'options-item')
        else:
            li = div[2].find_elements(By.CLASS_NAME, 'options-item')
        if '3K以下' in self.pr.get_parameter()[3][0]:
            li[0].click()
        elif '3K-5k' in self.pr.get_parameter()[3][0]:
            li[1].click()
        elif '5K-10k' in self.pr.get_parameter()[3][0]:
            li[2].click()
        elif '10K-20k' in self.pr.get_parameter()[3][0]:
            li[3].click()
        elif '20K-40k' in self.pr.get_parameter()[3][0]:
            li[4].click()
        elif '40K-60k' in self.pr.get_parameter()[3][0]:
            li[5].click()
        elif '60K以上' in self.pr.get_parameter()[3][0]:
            li[6].click()
        elif '自定义' in self.pr.get_parameter()[3][0]:
            if 'on' in self.driver.find_element(By.CLASS_NAME, 'salary-name').get_attribute('class'):
                self.driver.find_elements(By.CLASS_NAME, 'ant-input-number-input')[0].send_keys(Keys.CONTROL, 'a')
                self.driver.find_elements(By.CLASS_NAME, 'ant-input-number-input')[0].send_keys(Keys.DELETE)
                self.driver.find_elements(By.CLASS_NAME, 'ant-input-number-input')[1].send_keys(Keys.CONTROL, 'a')
                self.driver.find_elements(By.CLASS_NAME, 'ant-input-number-input')[1].send_keys(Keys.DELETE)
                # jquery从input框中获取value的值
                # self.driver.execute_script('return $(".ant-input-number-input").attr("value");')
                self.driver.find_elements(By.CLASS_NAME, 'ant-input-number-input')[0].send_keys(
                    self.pr.get_parameter()[3][1])
                self.driver.find_elements(By.CLASS_NAME, 'ant-input-number-input')[1].send_keys(
                    self.pr.get_parameter()[3][2])
            else:
                self.driver.find_element(By.CLASS_NAME, 'salary-name').click()
                self.driver.find_elements(By.CLASS_NAME, 'ant-input-number-input')[0].send_keys(
                    self.pr.get_parameter()[3][1])
                self.driver.find_elements(By.CLASS_NAME, 'ant-input-number-input')[1].send_keys(
                    self.pr.get_parameter()[3][2])
            self.driver.find_element(By.CLASS_NAME, 'ant-btn-primary').click()
        else:
            print('未能匹配到相关"薪资"选项！请更正字段值！')

    # release_time（default-不限）字段【4】
    def release_time(self, div):
        if '薪资' in div[3].find_element(By.CLASS_NAME, 'row-title').get_attribute('textContent'):
            li = div[4].find_elements(By.CLASS_NAME, 'options-item')
        else:
            li = div[3].find_elements(By.CLASS_NAME, 'options-item')
        if '一天以内' in self.pr.get_parameter()[4]:
            li[1].click()
        elif '三天以内' in self.pr.get_parameter()[4]:
            li[2].click()
        elif '一周以内' in self.pr.get_parameter()[4]:
            li[3].click()
        elif '一个月以内' in self.pr.get_parameter()[4]:
            li[4].click()
        else:
            print('未能匹配到相关"发布时间"选项！请更正字段值！')

    # work_experience字段【5】
    def work_experience(self, div):
        if '发布时间' in div[4].find_element(By.CLASS_NAME, 'row-title').get_attribute('textContent'):
            li = div[5].find_elements(By.CLASS_NAME, 'options-item')
        else:
            li = div[4].find_elements(By.CLASS_NAME, 'options-item')
        if '应届生' in self.pr.get_parameter()[5]:
            li[0].click()
        elif '实习生' in self.pr.get_parameter()[5]:
            li[1].click()
        elif '1年以内' in self.pr.get_parameter()[5]:
            li[2].click()
        elif '1-3年' in self.pr.get_parameter()[5]:
            li[3].click()
        elif '3-5年' in self.pr.get_parameter()[5]:
            li[4].click()
        elif '5-10年' in self.pr.get_parameter()[5]:
            li[5].click()
        elif '10年以上' in self.pr.get_parameter()[5]:
            li[6].click()
        else:
            print('未能匹配到相关"经验"选项！请更正字段值！')

    # education字段【6】
    def education(self):
        ed = self.driver.find_elements(By.CLASS_NAME, 'select-box')[0].find_elements(By.TAG_NAME, 'span')[0]
        ActionChains(self.driver).move_to_element(ed).click().perform()
        if '博士' in self.pr.get_parameter()[6]:
            ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif ('MBA/EMBA') in self.pr.get_parameter()[6]:
            for item in range(2):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '硕士' in self.pr.get_parameter()[6]:
            for item in range(3):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '本科' in self.pr.get_parameter()[6]:
            for item in range(4):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '大专' in self.pr.get_parameter()[6]:
            for item in range(5):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif ('中专/中技') in self.pr.get_parameter()[6]:
            for item in range(6):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '高中' in self.pr.get_parameter()[6]:
            for item in range(7):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '初中及以下' in self.pr.get_parameter()[6]:
            for item in range(8):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        else:
            print('未能匹配到相关"学历"选项！请更正字段值！')
        # 使用JS来进行点击操作 self.driver.execute_script('arguments[0].click();', ed)
        # for item in self.driver.find_elements(By.CLASS_NAME, 'select-box'):
        #     item.find_elements(By.TAG_NAME, 'span')[1].click()

    # expected_industry字段【7】
    def expected_industry(self):
        ei = self.driver.find_elements(By.CLASS_NAME, 'select-box')[1].find_elements(By.TAG_NAME, 'span')[0]
        ActionChains(self.driver).move_to_element(ei).click().perform()
        if ('互联网' or '游戏' or '软件') in self.pr.get_parameter()[7][0]:
            ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.RIGHT).perform()
            if '不限' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '互联网' or '电商' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '游戏产业' in self.pr.get_parameter()[7][1]:
                for item in range(2):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '计算机软件' in self.pr.get_parameter()[7][1]:
                for item in range(3):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif 'IT服务' in self.pr.get_parameter()[7][1]:
                for item in range(4):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif ('电子' or '通信' or '硬件') in self.pr.get_parameter()[7][0]:
            for item in range(2):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.RIGHT).perform()
            if '不限' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '电子/芯片/半导体' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '通信业' in self.pr.get_parameter()[7][1]:
                for item in range(2):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '计算机/网络设备' in self.pr.get_parameter()[7][1]:
                for item in range(3):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif ('房地产' or '建筑' or '物业') in self.pr.get_parameter()[7][0]:
            for item in range(3):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.RIGHT).perform()
            if '不限' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '房地产/建筑' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '房地产服务' in self.pr.get_parameter()[7][1]:
                for item in range(2):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '规划/设计/装潢' in self.pr.get_parameter()[7][1]:
                for item in range(3):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '金融' in self.pr.get_parameter()[7][0]:
            for item in range(4):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.RIGHT).perform()
            if '不限' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '银行' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '保险' in self.pr.get_parameter()[7][1]:
                for item in range(2):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '基金/证券/投资' in self.pr.get_parameter()[7][1]:
                for item in range(3):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '会计/审计' in self.pr.get_parameter()[7][1]:
                for item in range(4):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '信托/担保/拍卖' in self.pr.get_parameter()[7][1]:
                for item in range(5):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '消费品' in self.pr.get_parameter()[7][0]:
            for item in range(5):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.RIGHT).perform()
            if '不限' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '食品/饮料/日化' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '批发零售' in self.pr.get_parameter()[7][1]:
                for item in range(2):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '服装纺织' in self.pr.get_parameter()[7][1]:
                for item in range(3):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '家具/家电' in self.pr.get_parameter()[7][1]:
                for item in range(4):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '办公设备' in self.pr.get_parameter()[7][1]:
                for item in range(5):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '奢侈品/收藏品' in self.pr.get_parameter()[7][1]:
                for item in range(6):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '珠宝/玩具/工艺品' in self.pr.get_parameter()[7][1]:
                for item in range(7):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif ('汽车' or '机械' or '制造') in self.pr.get_parameter()[7][0]:
            for item in range(6):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.RIGHT).perform()
            if '不限' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '汽车/摩托车' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '机械/机电/重工' in self.pr.get_parameter()[7][1]:
                for item in range(2):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '印刷/包装/造纸' in self.pr.get_parameter()[7][1]:
                for item in range(3):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '仪器/电气/自动化' in self.pr.get_parameter()[7][1]:
                for item in range(4):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '原材料加工' in self.pr.get_parameter()[7][1]:
                for item in range(5):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif ('服务' or '外包' or '中介') in self.pr.get_parameter()[7][0]:
            for item in range(7):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.RIGHT).perform()
            if '不限' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '中介服务' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '专业服务' in self.pr.get_parameter()[7][1]:
                for item in range(2):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '外包服务' in self.pr.get_parameter()[7][1]:
                for item in range(3):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '检测/认证' in self.pr.get_parameter()[7][1]:
                for item in range(4):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '餐饮/酒旅/服务' in self.pr.get_parameter()[7][1]:
                for item in range(5):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '租赁服务' in self.pr.get_parameter()[7][1]:
                for item in range(6):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif ('广告' or '传媒' or '教育' or '文化') in self.pr.get_parameter()[7][0]:
            for item in range(8):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.RIGHT).perform()
            if '不限' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '文体娱乐' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '广告/市场/会展' in self.pr.get_parameter()[7][1]:
                for item in range(2):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '影视文化' in self.pr.get_parameter()[7][1]:
                for item in range(3):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '教育培训' in self.pr.get_parameter()[7][1]:
                for item in range(4):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif ('交通' or '贸易' or '物流') in self.pr.get_parameter()[7][0]:
            for item in range(9):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.RIGHT).perform()
            if '不限' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '交通/物流/运输' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '贸易/进出口' in self.pr.get_parameter()[7][1]:
                for item in range(2):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '航空/航天' in self.pr.get_parameter()[7][1]:
                for item in range(3):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif ('制药' or '医疗') in self.pr.get_parameter()[7][0]:
            for item in range(10):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.RIGHT).perform()
            if '不限' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '制药/生物工程' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '医疗/保健/美容' in self.pr.get_parameter()[7][1]:
                for item in range(2):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '医疗器械' in self.pr.get_parameter()[7][1]:
                for item in range(3):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif ('能源' or '化工' or '环保') in self.pr.get_parameter()[7][0]:
            for item in range(11):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.RIGHT).perform()
            if '不限' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '环保' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '石油/化工' in self.pr.get_parameter()[7][1]:
                for item in range(2):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '采掘/冶炼/矿产' in self.pr.get_parameter()[7][1]:
                for item in range(3):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '能源/水利' in self.pr.get_parameter()[7][1]:
                for item in range(4):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '新能源' in self.pr.get_parameter()[7][1]:
                for item in range(5):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif ('政府' or '农林渔牧') in self.pr.get_parameter()[7][0]:
            for item in range(12):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.RIGHT).perform()
            if '不限' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '政务/公共服务' in self.pr.get_parameter()[7][1]:
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '农林牧渔' in self.pr.get_parameter()[7][1]:
                for item in range(2):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '计算机软件' in self.pr.get_parameter()[7][1]:
                for item in range(3):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            elif '其他行业' in self.pr.get_parameter()[7][1]:
                for item in range(4):
                    ActionChains(self.driver).send_keys(Keys.DOWN).perform()
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        else:
            print('未能匹配到相关"行业"选项！请更正字段值！')

    # expected_position【8】
    def expected_position(self):
        ep = self.driver.find_elements(By.CLASS_NAME, 'select-box')[2].find_elements(By.TAG_NAME, 'span')[0]
        ActionChains(self.driver).move_to_element(ep).click().perform()
        if '猎头职位' in self.pr.get_parameter()[8]:
            ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '企业职位' in self.pr.get_parameter()[8]:
            ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        else:
            print('未能匹配到相关"职位类型"选项！请更正字段值！')

    # enterprise_scale字段【9】
    def enterprise_scale(self):
        es = self.driver.find_elements(By.CLASS_NAME, 'select-box')[3].find_elements(By.TAG_NAME, 'span')[0]
        ActionChains(self.driver).move_to_element(es).click().perform()
        if '1-49人' in self.pr.get_parameter()[9]:
            ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '50-99人' in self.pr.get_parameter()[9]:
            for item in range(2):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '100-499人' in self.pr.get_parameter()[9]:
            for item in range(3):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '500-999人' in self.pr.get_parameter()[9]:
            for item in range(4):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '1000-2000人' in self.pr.get_parameter()[9]:
            for item in range(5):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '2000-5000人' in self.pr.get_parameter()[9]:
            for item in range(6):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '5000-10000人' in self.pr.get_parameter()[9]:
            for item in range(7):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '10000人以上' in self.pr.get_parameter()[9]:
            for item in range(8):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        else:
            print('未能匹配到相关"企业规模"选项！请更正字段值！')

    # financing_stage字段【10】
    def financing_stage(self):
        fs = self.driver.find_elements(By.CLASS_NAME, 'select-box')[4].find_elements(By.TAG_NAME, 'span')[0]
        ActionChains(self.driver).move_to_element(fs).click().perform()
        if '天使轮' in self.pr.get_parameter()[10]:
            ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif 'A轮' in self.pr.get_parameter()[10]:
            for item in range(2):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif 'B轮' in self.pr.get_parameter()[10]:
            for item in range(3):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif 'C轮' in self.pr.get_parameter()[10]:
            for item in range(4):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif 'D轮及以上' in self.pr.get_parameter()[10]:
            for item in range(5):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '已上市' in self.pr.get_parameter()[10]:
            for item in range(6):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '战略融资' in self.pr.get_parameter()[10]:
            for item in range(7):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '融资未公开' in self.pr.get_parameter()[10]:
            for item in range(8):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '其他' in self.pr.get_parameter()[10]:
            for item in range(9):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        else:
            print('未能匹配到相关"融资阶段"选项！请更正字段值！')

    # enterprise_nature字段【11】
    def enterprise_nature(self):
        en = self.driver.find_elements(By.CLASS_NAME, 'select-box')[5].find_elements(By.TAG_NAME, 'span')[0]
        ActionChains(self.driver).move_to_element(en).click().perform()
        if '外商独资·外企办事处' in self.pr.get_parameter()[11]:
            ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '中外合营(合资·合作)' in self.pr.get_parameter()[11]:
            for item in range(2):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '私营·民营企业' in self.pr.get_parameter()[11]:
            for item in range(3):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '国有企业' in self.pr.get_parameter()[11]:
            for item in range(4):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '国内上市公司' in self.pr.get_parameter()[11]:
            for item in range(5):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '政府机关／非盈利机构' in self.pr.get_parameter()[11]:
            for item in range(6):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '事业单位' in self.pr.get_parameter()[11]:
            for item in range(7):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        elif '其他' in self.pr.get_parameter()[11]:
            for item in range(8):
                ActionChains(self.driver).send_keys(Keys.DOWN).perform()
            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        else:
            print('未能匹配到相关"企业性质"选项！请更正字段值！')


# 职位项元素定位操作
class SpiderLiePinWeb_Position_Terms:
    def __init__(self, driver):
        self.driver = driver

    # 判断搜索后是否有可操作职位
    def position_existence(self):
        # 判断是否存在职位卡片
        val = 1
        try:
            if '非常抱歉！暂时没有合适的职位' in self.driver.find_element(By.CLASS_NAME, 'ant-empty-description').get_attribute('textContent'):
                val = 0
                print('===请重新配置搜索基础参数(PFP_dict)！现参数无法匹配简历！===')
                # return val
        except NoSuchElementException as e:
            print('(===position_existence方法异常，可忽略此异常。===)')
        finally:
            # 返回此页所有的职位卡片元素定位
            position_list = self.driver.find_elements(By.CLASS_NAME, 'job-card-left-box')
            return val, position_list

    # 职位卡片选择
    def position_choice(self, position):
        # 点击每个卡片
        position.click()
        # 获取所有页面句柄
        windows = [item for item in self.driver.window_handles]
        self.driver.switch_to.window(windows[-1])
        return windows

    # 职位详情信息收集，再由算法匹配度决定是否收藏
    def position_collection(self):
        sleep(2)
        position_label = 'position_label:NULL'
        paragraph = self.driver.find_elements(By.CLASS_NAME, 'paragraph')
        position_name = self.driver.find_element(By.CLASS_NAME, 'name').get_attribute('textContent')
        try:
            position_label = [item.get_attribute('textContent') for item in paragraph[0].find_elements(By.TAG_NAME, 'li')]
        except NoSuchElementException:
            print('(===position_label变量定位异常，可忽略此异常。===)')
        finally:
            # print(position_name, position_label)
            position_describe = paragraph[0].find_element(By.TAG_NAME, 'dd').get_attribute('textContent')
            # print(position_describe)
            position_other_requirement = []
            for other_item in paragraph[1].find_elements(By.TAG_NAME, 'dd'):
                position_other_requirement.append(other_item.get_attribute('textContent'))
            # print(position_other_requirement)

            # position_requirement_language = paragraph[1].find_elements(By.TAG_NAME, 'dd')[0].get_attribute('textContent')
            # position_requirement_major = paragraph[1].find_elements(By.TAG_NAME, 'dd')[1].get_attribute('textContent')

            # if '收藏' in self.driver.find_element(By.CLASS_NAME, 'favor-box').find_element(By.TAG_NAME, 'span').get_attribute('textContent'):
            #     self.driver.find_element(By.CLASS_NAME, 'favor-box').click()
            # print(position_name, position_label, position_requirement_language, position_requirement_major)
            self.driver.close()
            # return position_name, position_label, position_describe, position_requirement_language, position_requirement_major
        # self.driver.close()

    # 页面跳转点击
    def position_turn_page(self):
        # 定位显示的所有跳转页码的textContent
        position_pages = self.driver.find_elements(By.CLASS_NAME, 'ant-pagination-item')
        list_pages = [item.get_attribute('textContent') for item in position_pages]
        # 从页码2开始跳转,跳转至最后一页
        for item in range(2, int(list_pages[-1]) + 1):
            self.driver.find_element(By.CLASS_NAME, f'ant-pagination-item-{item}').click()
            # print(self.driver.find_element(By.CLASS_NAME, 'ant-pagination-item-active').get_attribute('textContent'))
            sleep(2)
