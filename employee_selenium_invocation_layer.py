from employee_selenium_base_parameter_driver_layer import LoginParameter, PositionFundamentalParameter, configure_browse_driver
from employee_selenium_element_layer import SpiderLiePinWeb_Search_Terms, SpiderLiePinWeb_Position_Terms, SpiderLiePinWeb_Login_Terms, SpiderLiePinWeb_Personal_Terms
from PyQt5.QtWidgets import QApplication, QWidget
from employee_selenium_graphical_layer import Ui_widget_main_window, Ui_Form_login
from time import sleep
import sys


# 主窗口UI
class MainWindow(QWidget, Ui_widget_main_window):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)


# 登录窗口UI
class LoginWindow(QWidget, Ui_Form_login):
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)


# 传递登录参数，判断是否切换窗口
def switch_window(up):
    login_window.logging_in()
    login_result = LoginParameter(up[0], up[1])
    login_status = invocation_login_terms(login_result)
    if login_status:
        main_window.show()
        login_window.close()
        invocation_personal_terms()
    else:
        login_window.login_determine()


# 传递搜索项参数
def transmit_parameters(kw):
    position_result = PositionFundamentalParameter(kw)
    invocation_search_terms(position_result)
    num = invocation_position_terms()
    main_window.position_num(num)


# 调用登录方法
def invocation_login_terms(lr):
    slt = SpiderLiePinWeb_Login_Terms(lr, driver)
    slt.login()
    status = slt.slider()   # return False or True
    print('===登录项完成===')
    return status


# 个人简历项方法
def invocation_personal_terms():
    spt = SpiderLiePinWeb_Personal_Terms(driver)
    spt.resume_content()
    print('===个人简历项完成===')


# 调用搜索项方法
def invocation_search_terms(pr):
    stt = SpiderLiePinWeb_Search_Terms(pr, driver)
    # 根据get_parameter方法返回的字段是否为空判断是否执行具体方法
    if pr.get_parameter()[0] != '':
        stt.operation_search_position()
        sleep(1)
    if pr.get_parameter()[1] != '':
        stt.famous_enterprise(stt.search_lists())
        sleep(1)
    if pr.get_parameter()[2][0] != '':
        stt.target_city(stt.search_lists())
        sleep(1)
    if pr.get_parameter()[3][0] != '':
        stt.expected_salary(stt.search_lists())
        sleep(1)
    if pr.get_parameter()[4] != '':
        stt.release_time(stt.search_lists())
        sleep(1)
    if pr.get_parameter()[5] != '':
        stt.work_experience(stt.search_lists())
        sleep(1)
    if pr.get_parameter()[6] != '':
        stt.education()
        sleep(1)
    if pr.get_parameter()[7][0] != '':
        stt.expected_industry()
        sleep(1)
    if pr.get_parameter()[8] != '':
        stt.expected_position()
        sleep(1)
    if pr.get_parameter()[9] != '':
        stt.enterprise_scale()
        sleep(1)
    if pr.get_parameter()[10] != '':
        stt.financing_stage()
        sleep(1)
    if pr.get_parameter()[11] != '':
        stt.enterprise_nature()
        sleep(1)
    print('===搜索项完成===')


# 调用职位项方法
def invocation_position_terms():
    srt = SpiderLiePinWeb_Position_Terms(driver)
    # srt.position_turn_page()  # 翻页功能
    pe = srt.position_existence()
    # 判断是否存在职位卡片
    # if pe[0]:
    #     # 对此页的所有职位卡片遍历
    #     for item in pe[1][:1]:
    #         handles = srt.position_choice(item)
    #         sleep(2)
    #         srt.position_collection()
    #         driver.switch_to.window(handles[0])
    #         sleep(2)
    print('===职位项完成===')
    return len(pe[1])


if __name__ == '__main__':
    # cmd_switch()
    driver = configure_browse_driver()
    try:

        app = QApplication(sys.argv)
        login_window = LoginWindow()
        main_window = MainWindow()
        login_window.show()
        login_window.pushButton_login.clicked.connect(lambda: switch_window(login_window.login_submit()))
        main_window.pushButton_main_submit.clicked.connect(lambda: transmit_parameters(main_window.main_submit()))

        # print(driver.current_window_handle)
        # print(driver.window_handles)

        sys.exit(app.exec_())
    # except TypeError as e:
    #     print(e)
    # except Exception as e:
    #     print(e)
    finally:
        # driver.save_screenshot('D:/soft/Python/SpiderProject/img/image.png')
        driver.quit()
        # cmd_switch(False)
        # driver.close()
