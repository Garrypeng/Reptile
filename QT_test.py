import sys
from PyQt5.QtWidgets import QApplication, QWidget
from employee_selenium_graphical_layer import Ui_widget_main_window, Ui_Form_login
from One import A, T
from Two import B, RPT


# class MainWindow(QWidget, Ui_widget_main_window):
#     def __init__(self, parent=None):
#         super(QWidget, self).__init__(parent)
#         self.setupUi(self)


# class LoginWindow(QWidget, Ui_Form_login):
#     def __init__(self, parent=None):
#         super(QWidget, self).__init__(parent)
#         self.setupUi(self)


# def switch_window(up):
#     bb = B(up[0], up[1])
#     # bb.un = up[0]
#     # bb.pw = up[1]
#     # print(bb.get_parameter())
#     aa = A(bb)
#     if aa.get_parameter():
#         main_window.show()
#         login_window.close()
#     else:
#         login_window.login_determine()


# def transmit_parameters(kw):
#     rr = RPT(kw)
#     tt = T(rr)
#     print(tt.get_parameter())


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     login_window = LoginWindow()
#     main_window = MainWindow()
#     login_window.show()
#     login_window.pushButton_login.clicked.connect(lambda: switch_window(login_window.login_submit()))
#     main_window.pushButton_main_submit.clicked.connect(lambda: transmit_parameters(main_window.main_submit()))
#     sys.exit(app.exec_())
