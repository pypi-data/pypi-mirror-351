# coding: utf-8
# Project：xbsTestTools
# File：format_execution.py
# Author：张炼武
# Date ：2025/5/15 14:15
# IDE：PyCharm
import subprocess
import uiautomator2 as u2

class FormatExecution:
    def __init__(self, dev):
        self.dev = dev

    def library(self, widget_info):
        """控件类型识别"""
        d = self.connect()
        if widget_info['library_type'] == "resourceId":
            return d(resourceId=widget_info['library'])
        else:
            return d(text=widget_info['library'])

    def connect(self):
        return u2.connect(self.dev)

    def click(self, widget_info, preconditions=None):
        """
        控件点击
        widget_info: {"name": "同意", "library_type": "resourceId","library": "com.so.stn.lar:id/pri"}
        preconditions: [{"name": "同意", "library_type": "resourceId","library": "com.so.stn.lar:id/pri"},{"name": "同意", "library_type": "resourceId","library": "com.so.stn.lar:id/pri"}]
        """
        if preconditions:
            for precondition in preconditions:
                self.library(precondition).click()

        library = self.library(widget_info)
        if not library.info['checked']:
            print("控件checked 值为 false 无法点击")
            return False

        self.library(widget_info).click()
        return True

    def set_text(self, widget_info, text):
        """控件写入值"""
        self.library(widget_info).set_text(text)
        return True

    def operation_analysis(self, widget_info):
        """"""
        d = self.connect()
        if widget_info.get("operate") == "click":
            # 点击
            try:
                self.library(widget_info).click()
            except u2.exceptions.UiObjectNotFoundError:
                print(f"当前页面没有 “{widget_info['name']}” 的控件")
                return False
            return True

        elif widget_info.get("operate") == "seek_click":
            # 滑动找到目标再点击
            try:
                if widget_info.get("library_type") == "resourceId":
                    seek_result = d(scrollable=True).scroll.to(resourceId=widget_info.get("library"))
                else:
                    seek_result = d(scrollable=True).scroll.to(text=widget_info.get("library"))
                if not seek_result:
                    return False
                self.library(widget_info).click()
            except u2.exceptions.UiObjectNotFoundError:
                print(f"当前页面没有 “{widget_info['name']}” 的控件")
                return False
            return True
        elif widget_info.get("operate") == "set_text":
            # 写入
            try:
                d.set_fastinput_ime(True)
                self.library(widget_info).set_text(widget_info['value'])
                d.set_fastinput_ime(False)
            except u2.exceptions.UiObjectNotFoundError:
                print(f"当前页面没有 “{widget_info['name']}” 的控件")
                return False
            return True
        elif widget_info.get("operate") == "positioning":
            # 定位
            try:
                if self.library(widget_info).exists(timeout=3):
                    return True
            except u2.exceptions.UiObjectNotFoundError:
                print(f"当前页面没有 “{widget_info['name']}” 的控件")
                ...
            return False

    def actuator(self, widget_list, retry_count=3):
        """控件执行操作"""
        start_type = False
        for retry in range(1, retry_count + 1):
            print(f"执行ID: {retry}")
            subprocess.run(f"adb -s {self.dev} shell input keyevent 266")
            for widget in widget_list:
                # 循环遍历执行前置操作
                if widget.get("preconditions"):
                    if not isinstance(widget.get("preconditions"), list):
                        widget.get("preconditions")()
                    else:
                        # 前置操作时一个list
                        for pre in widget.get("preconditions"):
                            self.operation_analysis(pre)
                result = self.operation_analysis(widget)
                # 后置操作
                if widget.get("post_operation"):
                    # 后置操作时一个方法的话执行方法
                    if not isinstance(widget.get("post_operation"), list):
                        widget.get("post_operation")()
                    else:
                        # 后置操作时一个list
                        for post_oper in widget.get("post_operation"):
                            self.operation_analysis(post_oper)
                if "最终结果" in widget.get('name') and result:
                    start_type = True
                    break
            if start_type:
                break
        return start_type


