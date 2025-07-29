"""
Author: Xiaoqiang
WeChatOfficialAccount: XiaoqiangClub
Date: 2025-05-21 08:30:44
LastEditTime: 2025-05-28 10:24:34
Description: 浏览器自动化
FilePath: /AutoChrome/AutoChrome/auto_chrome.py
Copyright: © 2025 Xiaoqiang. All Rights Reserved.
"""

import time
import platform
from AutoChrome.logger import LoggerBase
from http.cookiejar import Cookie, CookieJar
from typing import Callable, List, Tuple, Union, Optional, Literal


# 导入说明：https://drissionpage.cn/get_start/import
from DrissionPage._units.listener import DataPacket
from DrissionPage import Chromium, ChromiumOptions, SessionOptions
from DrissionPage.items import ChromiumTab, ChromiumElement, SessionElement, MixTab


class AutoChrome:
    def __init__(
        self,
        start_url: Optional[str] = None,
        dp_chrome: Optional[Chromium] = None,
        chrome_options: Union[str, int, ChromiumOptions, None] = None,
        session_options: Union[SessionOptions, None, bool] = None,
        headless: bool = False,
        user_data_path: Optional[str] = None,
        auto_port: bool = False,
        auto_handle_alert: bool = False,
        alert_accept: bool = True,
        auto_close: bool = False,
        console_log_level: Literal[
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
        ] = "INFO",
        log_file_level: Literal[
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
        ] = "WARNING",
        log_file: Optional[str] = None,
        log_debug_format: bool = False,
    ):
        """
        网页自动化
        多浏览器操作文档：
        https://drissionpage.cn/browser_control/connect_browser/#%EF%B8%8F-%E5%A4%9A%E6%B5%8F%E8%A7%88%E5%99%A8%E5%85%B1%E5%AD%98

        :param start_url: 启动页面
        :param dp_chrome: DrissionPage 的 Chromium 对象：https://drissionpage.cn/browser_control/connect_browser#%EF%B8%8F-chromium%E5%88%9D%E5%A7%8B%E5%8C%96%E5%8F%82%E6%95%B0
        :param chrome_options: Chromium 的 addr_or_opts 参数，注意：仅当 dp_chrome=None 时有效！
        :param session_options: Chromium 的 session_options 参数，注意：仅当 dp_chrome=None 时有效！
        :param headless: 是否启用无头模式
        :param user_data_path: 设置用户数据路径：https://drissionpage.cn/browser_control/connect_browser#-%E5%8D%95%E7%8B%AC%E6%8C%87%E5%AE%9A%E6%9F%90%E4%B8%AA%E7%94%A8%E6%88%B7%E6%96%87%E4%BB%B6%E5%A4%B9
        :param auto_port: 是否自动分配端口，仅当 chrome_options=None 时生效：https://drissionpage.cn/browser_control/connect_browser#-auto_port%E6%96%B9%E6%B3%95
        :param auto_handle_alert: 是否设置所有标签页都自动处理 alert 弹窗，默认为 False
        :param alert_accept: 自动处理 alert 弹窗时，是否默认点击“确定”，默认为 True，否则点击“取消”
        :param auto_close: 是否自动关闭浏览器
        :param console_log_level: 终端显示的日志等级，默认为："INFO"
        :param log_file: 日志文件路径，默认为: None 不保存
        :param log_file_level: 日志文件保存的日志等级，默认为："WARNING"
        :param log_debug_format: 是否使用调试格式，默认为：False
                                - False："%(asctime)s - [%(name)s %(filename)s:%(lineno)d] - %(levelname)s：%(message)s"
                                - True："%(asctime)s - %(levelname)s：%(message)s"
        """
        # 设置日志显示的等级
        self.log = self._logger_init(
            console_log_level=console_log_level,
            log_file_level=log_file_level,
            log_file=log_file,
            log_debug_format=log_debug_format,
        )

        # 启动页面
        self.start_url = start_url
        self.auto_close = auto_close

        # 浏览器参数
        chrome_options = chrome_options or ChromiumOptions()
        chrome_options.headless(headless)  # 启用无头模式
        chrome_options = chrome_options.auto_port(auto_port)  # 自动分配端口
        if user_data_path:  # 设置用户数据路径
            chrome_options = chrome_options.set_user_data_path(user_data_path)

        # 创建浏览器对象
        self.browser = dp_chrome or Chromium(
            addr_or_opts=chrome_options, session_options=session_options
        )
        self.latest_tab = self.browser.latest_tab

        if auto_handle_alert:  # 自动处理 alert 弹窗
            self.browser.set.auto_handle_alert(accept=alert_accept)

        #  启动页面
        if self.start_url:
            self.latest_tab.get(self.start_url)

    def _logger_init(
        self,
        console_log_level: str = "INFO",
        log_file_level: str = "WARNING",
        log_file: Optional[str] = None,
        log_debug_format: bool = False,
    ) -> LoggerBase:
        """
        日志初始化

        :param console_log_level: 终端显示的日志等级，默认为: "INFO"
        :param log_file_level: 日志文件保存的日志等级，默认为: "WARNING"
        :param log_file: 日志保存文件路径，默认为: None 不保存
        :param log_format: 默认为: False
                            - False："%(asctime)s - [%(name)s %(filename)s:%(lineno)d] - %(levelname)s：%(message)s"
                            - True："%(asctime)s - %(levelname)s：%(message)s"
        """
        logger = LoggerBase(
            "AutoChrome",
            console_log_level=console_log_level,
            log_file_level=log_file_level,
            log_file=log_file,
            log_format=(
                "%(asctime)s - [%(name)s %(filename)s:%(lineno)d] - %(levelname)s： %(message)s"
                if log_debug_format
                else "%(asctime)s - %(levelname)s： %(message)s"
            ),
        )
        return logger.logger

    def get_cookies(
        self,
        tab: Optional[Chromium] = None,
        all_info: bool = False,
        return_type: Literal["list", "str", "dict", "json"] = "list",
    ) -> Union[List[dict], str, dict]:
        """
        获取 标签页的cookies
        https://drissionpage.cn/SessionPage/get_page_info/#%EF%B8%8F%EF%B8%8F-cookies-%E4%BF%A1%E6%81%AF

        :param tab: 标签页，默认为: None, 使用 self.latest_tab
        :param all_info: 是否获取所有信息，默认为: False, 仅获取 name、value、domain 的值
        :param return_type: 返回类型，默认为: list, 可选值：list、str、dict、json, 注意：str 和 dict 都只会保留 'name'和 'value'字段; json 返回的是 json格式的字符串
        :return:
        """
        tab = tab or self.latest_tab
        c = tab.cookies(all_info=all_info)
        if return_type == "list":
            return c
        elif return_type == "str":
            return c.as_str()
        elif return_type == "dict":
            return c.as_dict()
        elif return_type == "json":
            return c.as_json()
        else:
            raise ValueError("return_type 参数错误！")

    def set_cookies(
        self,
        cookies: Union[Cookie, str, dict, list, tuple, CookieJar],
        tab: Optional[Chromium] = None,
        refresh: bool = True,
        verify_str: Optional[str] = None,
    ) -> Optional[bool]:
        """
        给标签页设置 cookies
        https://drissionpage.cn/tutorials/functions/set_cookies

        :param cookies: cookies 的值，支持字符串和字典格式
        :param tab: 标签页，默认为: None, 使用 self.latest_tab
        :param refresh: 是否刷新页面，默认为: True, 刷新页面
        :param verify: 是否验证 cookies 设置成功，默认为: None, 不验证; 为 字符串 时会自动刷新页面。并且验证页面是否包含 verify_str 字符串.
        :return: 如果 verify=True，则返回一个布尔值，表示 cookies 是否设置成功；否则返回 None
        """
        tab = tab or self.latest_tab
        tab.set.cookies(cookies)

        if refresh or verify_str:
            self.log.info("🔄 刷新页面...")
            tab.refresh()

        if verify_str:
            self.log.info("🔍 正在验证 cookies 是否设置成功...")
            if verify_str in tab.html:
                self.log.info("✅ cookies 设置成功！")
                return True
            else:
                self.log.error("❌ cookies 设置失败/已失效！")
                return False

    @property
    def is_windows(self) -> bool:
        """
        检查当前操作系统是否为 Windows
        :return: 如果是 Windows 系统，返回 True；否则返回 False
        """
        return platform.system() == "Windows"

    def hide_tab(self, tab: Optional[Chromium] = None) -> None:
        """
        此方法用于隐藏签页窗口，但是会导致整个浏览器窗口被隐藏。
        与 headless 模式不一样，这个方法是直接隐藏浏览器进程。在任务栏上也会消失。
        只支持 Windows 系统，并且必需已安装 pypiwin32 库才可使用。
        pip install -i https://mirrors.aliyun.com/pypi/simple/ -U pypiwin32
        https://drissionpage.cn/browser_control/page_operation/#-setwindowhide

        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :return:
        """
        if not self.is_windows:
            self.log.error("❌ 此方法仅支持 Windows 系统！")
            return

        self.log.info("🙈 隐藏浏览器窗口...")
        tab = tab or self.latest_tab
        tab.set.window.hide()

    def show_tab(self, tab: Optional[Chromium] = None) -> None:
        """
        显示标签页，该操作会显示整个浏览器。
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :return:
        """
        if not self.is_windows:
            self.log.error("❌ 此方法仅支持 Windows 系统！")
            return

        self.log.info("👀 显示浏览器窗口...")
        tab = tab or self.latest_tab
        tab.set.window.show()

    def close_browser(
        self,
        close_current_tab=False,
        close_other_tabs=False,
        close_session=False,
        timeout: float = 3,
        kill_process=False,
        del_user_data=False,
    ) -> List[bool]:
        """
        关闭浏览器
        :param close_current_tab: 关闭当前标签页
        :param close_other_tabs: 关闭其他标签页，仅当 close_current_tab=True 时生效
        :param close_session: 是否同时关闭内置 Session 对象，只对自己有效，仅当 close_current_tab=True 时生效
        :param timeout: 关闭浏览器超时时间，单位秒
        :param kill_process: 是否立刻强制终止进程
        :param del_user_data: 是否删除用户数据
        :return:
        """
        try:
            if close_current_tab:  # 关闭当前标签页
                self.log.info("🗂️ 正在关闭标签页，请稍等...")
                self.latest_tab.close(others=close_other_tabs, session=close_session)
            close_tab = True
        except Exception as e:
            self.log.error(f"❌ 关闭标签页出错: {e}")
            close_tab = False

        try:
            # 关闭浏览器
            self.log.info("🛑 正在关闭浏览器，请稍等...")
            self.browser.quit(
                timeout=timeout, force=kill_process, del_data=del_user_data
            )
            self.log.info("✅ 浏览器已关闭！")
            close_browser = True
        except Exception as e:
            self.log.error(f"❌ 关闭浏览器出错: {e}")
            close_browser = False

        return [close_tab, close_browser]

    def __del__(self) -> None:
        """
        关闭浏览器
        """
        if not self.auto_close:
            return

        self.close_browser()

    def ele_for_data(
        self,
        selector: Union[str, Tuple[str]],
        tab: Optional[ChromiumTab] = None,
        index: int = 1,
        timeout: Optional[float] = None,
    ) -> SessionElement:
        """
        获取单个静态元素用于提取数据
        https://drissionpage.cn/get_start/concept#-%E5%85%83%E7%B4%A0%E5%AF%B9%E8%B1%A1
        https://drissionpage.cn/browser_control/get_elements/find_in_object/#-s_ele

        :param selector: 元素的定位信息。可以是查询字符串，或 loc 元组：https://drissionpage.cn/browser_control/get_elements/syntax#%EF%B8%8F%EF%B8%8F-%E5%9F%BA%E6%9C%AC%E6%A6%82%E5%BF%B5
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :return: 元素对象
        """
        tab = tab or self.latest_tab

        return tab.s_ele(selector, index=index, timeout=timeout)

    def eles_for_data(
        self,
        selector: Union[str, Tuple[str]],
        tab: Optional[ChromiumTab] = None,
        timeout: Optional[float] = None,
    ) -> List[SessionElement]:
        """
        获取静态元素用于提取数据
        https://drissionpage.cn/browser_control/get_elements/find_in_object/#-s_eles

        :param selector: 元素的定位信息。可以是查询字符串，或 loc 元组
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :return: 元素对象
        """
        tab = tab or self.latest_tab

        return tab.s_eles(selector, timeout=timeout)

    def xpath_for_data(
        self,
        xpath: str,
        tab: Optional[ChromiumTab] = None,
        index: Optional[int] = 1,
        timeout: Optional[float] = None,
    ) -> Union[SessionElement, List[SessionElement]]:
        """
        使用 Xpath 获取单个静态元素用于提取数据
        https://drissionpage.cn/browser_control/get_elements/syntax/#-xpath-%E5%8C%B9%E9%85%8D%E7%AC%A6-xpath

        :param xpath: Xpath表达式，可 F12 下直接鼠标右键——复制XPath; 用 xpath 在元素下查找时，最前面 // 或 / 前面的 . 可以省略。
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1。当 index=None 时，返回所有匹配的元素，相当于 s_eles。
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :return: 元素对象
        """
        tab = tab or self.latest_tab
        if index is None:
            return tab.s_eles(f"xpath:{xpath}", timeout=timeout)

        return tab.s_ele(f"xpath:{xpath}", index=index, timeout=timeout)

    def xpath_for_action(
        self,
        xpath: str,
        tab: Optional[ChromiumTab] = None,
        index: Optional[int] = 1,
        timeout: Optional[float] = None,
    ) -> ChromiumElement:
        """
        使用 Xpath 定位单个元素用于执行操作
        https://drissionpage.cn/get_start/concept#-%E5%85%83%E7%B4%A0%E5%AF%B9%E8%B1%A1
        https://drissionpage.cn/browser_control/get_elements/find_in_object/#-ele

        :param xpath: Xpath表达式，可 F12 下直接鼠标右键——复制XPath; 用 xpath 在元素下查找时，最前面 // 或 / 前面的 . 可以省略。
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :return: 元素对象
        """
        tab = tab or self.latest_tab

        return tab.ele(f"xpath:{xpath}", index=index, timeout=timeout)

    def ele_for_action(
        self,
        selector: Union[str, Tuple[str]],
        tab: Optional[ChromiumTab] = None,
        index: Optional[int] = 1,
        timeout: Optional[float] = None,
    ) -> ChromiumElement:
        """
        定位单个元素用于执行操作
        https://drissionpage.cn/browser_control/get_elements/find_in_object/#-ele

        :param selector: 元素的定位信息。可以是查询字符串，或 loc 元组
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :return: 元素对象
        """
        tab = tab or self.latest_tab

        return tab.ele(selector, index=index, timeout=timeout)

    def _verify_after_action(
        self,
        tab: Union[ChromiumTab, MixTab],
        verify_selector_appear: Optional[Union[str, Tuple[str]]] = None,
        verify_selector_disappear: Optional[Union[str, Tuple[str]]] = None,
        verify_text_appear: Optional[str] = None,
        verify_text_disappear: Optional[str] = None,
        verify_url_changed: bool = False,
        verify_url: Optional[str] = None,
        old_url: Optional[str] = None,
        verify_timeout: float = 5.0,
    ) -> bool:
        """
        通用点击后验证逻辑，返回True/False
        https://drissionpage.cn/browser_control/get_elements/find_in_object/#-ele

        :param tab: 标签页对象，类型为 ChromiumTab
        :param verify_selector_appear: 验证点击后页面上出现的元素定位
        :param verify_selector_disappear: 验证点击后页面上消失的元素定位
        :param verify_text_appear: 验证点击后页面上出现的文本
        :param verify_text_disappear: 验证点击后页面上消失的文本
        :param verify_url_changed: 验证点击后页面 url 是否发生变化
        :param verify_url: 验证点击后页面 url 是否为指定值
        :param old_url: 点击前的 url
        :param verify_timeout: 验证等待超时时间（秒）
        :return: 验证是否通过
        """
        start_time = time.time()
        while time.time() - start_time < verify_timeout:
            if verify_selector_appear:
                found = tab.ele(verify_selector_appear)
                if found:
                    return True
            if verify_selector_disappear:
                if not tab.ele(verify_selector_disappear):
                    return True
            if verify_text_appear:
                if verify_text_appear in tab.html:
                    return True
            if verify_text_disappear:
                if verify_text_disappear not in tab.html:
                    return True
            if verify_url_changed and old_url and tab.url != old_url:
                return True
            if verify_url and tab.url == verify_url:
                return True
            time.sleep(0.3)
        return False

    def click_ele(
        self,
        sel_or_ele: Union[str, Tuple[str], ChromiumElement],
        tab: Optional[ChromiumTab] = None,
        index: Optional[int] = 1,
        timeout: Optional[float] = None,
        by_js: Optional[bool] = None,
        c_timeout: float = 1.5,
        wait_stop: bool = True,
        expect_new_tab: bool = False,
        switch_to_new_tab: bool = True,
        verify_selector_appear: Optional[Union[str, Tuple[str]]] = None,
        verify_selector_disappear: Optional[Union[str, Tuple[str]]] = None,
        verify_text_appear: Optional[str] = None,
        verify_text_disappear: Optional[str] = None,
        verify_url_changed: bool = False,
        verify_url: Optional[str] = None,
        verify_timeout: float = 5.0,
        retry_times: int = 0,
    ) -> Optional[Tuple[Union[ChromiumTab, MixTab], ChromiumElement, bool]]:
        """
        点击元素，并可选验证点击生效或跳转新页面
        https://drissionpage.cn/browser_control/ele_operation/#-clickfor_new_tab

        :param sel_or_ele: 元素的定位信息。可以是查询字符串，loc 元组，或一个 ChromiumElement 对象
        :param tab: 标签页对象，如果为 None，则使用 self.latest_tab
        :param index: 获取第几个匹配的元素，从 1 开始，可输入负数表示从后面开始数，默认为 1
        :param timeout: 等待元素出现的超时时间（秒），默认为: None 使用页面对象设置
        :param by_js: 指定点击行为方式。为 None 时自动判断，为 True 用 JS 方式点击，为 False 用模拟点击。
        :param c_timeout: 模拟点击的超时时间（秒），等待元素可见、可用、进入视口，默认为 1.5 秒
        :param wait_stop: 点击前是否等待元素停止运动，默认为 True
        :param expect_new_tab: 是否预期点击后会打开新标签页（推荐用于 a 标签或 target=_blank 等情况）
        :param switch_to_new_tab: 是否自动切换到新标签页（仅当 expect_new_tab=True 时有效）
        :param verify_selector_appear: 验证点击后页面上出现的元素定位（可选）
        :param verify_selector_disappear: 验证点击后页面上消失的元素定位（可选）
        :param verify_text_appear: 验证点击后页面上出现的文本（可选）
        :param verify_text_disappear: 验证点击后页面上消失的文本（可选）
        :param verify_url_changed: 验证点击后页面 url 是否发生变化（可选）
        :param verify_url: 验证点击后页面 url 是否为指定值（可选）
        :param verify_timeout: 验证等待超时时间（秒），默认 5 秒
        :param retry_times: 点击失败时重试的次数，默认为 0：不重试
        :return:
            - 若 expect_new_tab=True，返回 [新标签页对象, 元素对象, True/False(验证结果)]，未检测到新标签页则返回 [当前tab, 元素对象, False]；
            - 若有验证条件，返回 [当前tab, 元素对象, True/False(验证结果)]；
            - 否则返回 [当前tab, 元素对象, 点击结果]；
            - 未找到元素时返回 None
        """
        for attempt in range(retry_times + 1):
            if isinstance(sel_or_ele, ChromiumElement):
                ele = sel_or_ele
            else:
                ele = self.ele_for_action(sel_or_ele, tab, index, timeout)
            if not ele:
                self.log.error(f"❌ 未找到元素: {sel_or_ele}")
                if attempt < retry_times:
                    self.log.info(f"🔁 重试点击元素: {sel_or_ele}，第{attempt+1}次")
                    continue
                return None

            tab = tab or self.latest_tab

            need_verify = any(
                [
                    verify_selector_appear,
                    verify_selector_disappear,
                    verify_text_appear,
                    verify_text_disappear,
                    verify_url_changed,
                    verify_url,
                ]
            )

            try:
                if expect_new_tab:
                    new_tab = ele.click.for_new_tab(
                        by_js=by_js, timeout=c_timeout, wait_stop=wait_stop
                    )
                    if new_tab:
                        if switch_to_new_tab:
                            self.latest_tab = new_tab

                        if not need_verify:
                            return [new_tab, ele, True]

                        old_url = (
                            new_tab.url if (verify_url_changed or verify_url) else None
                        )
                        result = self._verify_after_action(
                            new_tab,
                            verify_selector_appear,
                            verify_selector_disappear,
                            verify_text_appear,
                            verify_text_disappear,
                            verify_url_changed,
                            verify_url,
                            old_url,
                            verify_timeout,
                        )
                        return [new_tab, ele, result]
                    self.log.warning("⚠️ 未检测到新标签页打开")
                    if attempt < retry_times:
                        self.log.info(f"🔁 重试点击元素: {sel_or_ele}，第{attempt+1}次")
                        continue
                    return [tab, ele, False]

                click_result = ele.click(
                    by_js=by_js, timeout=c_timeout, wait_stop=wait_stop
                )
                # click_result 不是bool，期望返回True/False，判断是否点击成功
                is_success = bool(click_result)
                if not need_verify:
                    return [tab, ele, is_success]

                old_url = tab.url if (verify_url_changed or verify_url) else None
                result = self._verify_after_action(
                    tab,
                    verify_selector_appear,
                    verify_selector_disappear,
                    verify_text_appear,
                    verify_text_disappear,
                    verify_url_changed,
                    verify_url,
                    old_url,
                    verify_timeout,
                )
                return [tab, ele, result]
            except Exception as e:
                self.log.error(f"❌ 点击元素异常: {e}")
                if attempt < retry_times:
                    self.log.info(f"🔁 重试点击元素: {sel_or_ele}，第{attempt+1}次")
                    continue
                return None

    def click_xpath(
        self,
        xpath: Union[str, Tuple[str]],
        tab: Optional[ChromiumTab] = None,
        index: Optional[int] = 1,
        timeout: Optional[float] = None,
        by_js: Optional[bool] = None,
        c_timeout: float = 1.5,
        wait_stop: bool = True,
        expect_new_tab: bool = False,
        switch_to_new_tab: bool = True,
        verify_selector_appear: Optional[Union[str, Tuple[str]]] = None,
        verify_selector_disappear: Optional[Union[str, Tuple[str]]] = None,
        verify_text_appear: Optional[str] = None,
        verify_text_disappear: Optional[str] = None,
        verify_url_changed: bool = False,
        verify_url: Optional[str] = None,
        verify_timeout: float = 5.0,
        retry_times: int = 0,
    ) -> Optional[Tuple[Union[ChromiumTab, MixTab], ChromiumElement, bool]]:
        """
        点击通过 Xpath 定位的元素，并可选验证点击效果或是否跳转新页面。
        https://drissionpage.cn/browser_control/ele_operation/#-clickfor_new_tab

        :param xpath: Xpath 表达式，用于定位要点击的元素
        :param tab: 操作的标签页对象，默认使用当前标签页
        :param index: 匹配的第几个元素，从 1 开始，负数表示从后往前
        :param timeout: 等待元素出现的超时时间（秒）
        :param by_js: 是否使用 JS 方式点击，None 时自动判断
        :param c_timeout: 模拟点击的超时时间（秒），等待元素可见、可用、进入视口
        :param wait_stop: 点击前是否等待元素停止运动
        :param expect_new_tab: 是否预期点击后会打开新标签页（如 a 标签或 target=_blank）
        :param switch_to_new_tab: 是否自动切换到新标签页（仅 expect_new_tab 为 True 时有效）
        :param verify_selector_appear: 验证点击后页面上出现的元素定位
        :param verify_selector_disappear: 验证点击后页面上消失的元素定位
        :param verify_text_appear: 验证点击后页面上出现的文本
        :param verify_text_disappear: 验证点击后页面上消失的文本
        :param verify_url_changed: 验证点击后页面 url 是否发生变化
        :param verify_url: 验证点击后页面 url 是否为指定值
        :param verify_timeout: 验证等待超时时间（秒）
        :param retry_times: 点击失败时重试的次数，默认为 0：不重试
        :return:
            - 若 expect_new_tab=True，返回 [新标签页对象, 元素对象, True/False(验证结果)]，未检测到新标签页则返回 [当前tab, 元素对象, False]；
            - 若有验证条件，返回 [当前tab, 元素对象, True/False(验证结果)]；
            - 否则返回 [当前tab, 元素对象, 点击结果]；
            - 未找到元素时返回 None
        """
        for attempt in range(retry_times + 1):
            ele = self.xpath_for_action(xpath, tab, index, timeout)
            if not ele:
                self.log.error(f"❌ 未找到元素: {xpath}")
                if attempt < retry_times:
                    self.log.info(f"🔁 重试点击元素: {xpath}，第{attempt+1}次")
                    continue
                return None

            tab = tab or self.latest_tab

            need_verify = any(
                [
                    verify_selector_appear,
                    verify_selector_disappear,
                    verify_text_appear,
                    verify_text_disappear,
                    verify_url_changed,
                    verify_url,
                ]
            )

            try:
                if expect_new_tab:
                    new_tab = ele.click.for_new_tab(
                        by_js=by_js, timeout=c_timeout, wait_stop=wait_stop
                    )
                    if new_tab:
                        if switch_to_new_tab:
                            self.latest_tab = new_tab

                        if not need_verify:
                            return [new_tab, ele, True]

                        old_url = (
                            new_tab.url if (verify_url_changed or verify_url) else None
                        )
                        result = self._verify_after_action(
                            new_tab,
                            verify_selector_appear,
                            verify_selector_disappear,
                            verify_text_appear,
                            verify_text_disappear,
                            verify_url_changed,
                            verify_url,
                            old_url,
                            verify_timeout,
                        )
                        return [new_tab, ele, result]
                    self.log.warning("⚠️ 未检测到新标签页打开")
                    if attempt < retry_times:
                        self.log.info(f"🔁 重试点击元素: {xpath}，第{attempt+1}次")
                        continue
                    return [tab, ele, False]

                click_result = ele.click(
                    by_js=by_js, timeout=c_timeout, wait_stop=wait_stop
                )
                # click_result 不是bool，期望返回True/False，判断是否点击成功
                is_success = bool(click_result)
                if not need_verify:
                    return [tab, ele, is_success]

                old_url = tab.url if (verify_url_changed or verify_url) else None
                result = self._verify_after_action(
                    tab,
                    verify_selector_appear,
                    verify_selector_disappear,
                    verify_text_appear,
                    verify_text_disappear,
                    verify_url_changed,
                    verify_url,
                    old_url,
                    verify_timeout,
                )
                return [tab, ele, result]
            except Exception as e:
                self.log.error(f"❌ 点击元素异常: {e}")
                if attempt < retry_times:
                    self.log.info(f"🔁 重试点击元素: {xpath}，第{attempt+1}次")
                    continue
                return None

    def auto_find_next_selector(
        self, tab: Union[ChromiumTab, MixTab, None] = None, timeout: float = 5.0
    ) -> ChromiumElement:
        """
        查找文本为 “下一页” 的 button 或 a标签的元素
        https://drissionpage.cn/browser_control/get_elements/syntax#-xpath-%E5%8C%B9%E9%85%8D%E7%AC%A6-xpath

        :param tab: 标签页对象
        :param timeout: 查找超时时间（秒）
        :return: 下一页按钮的元素对象
        """
        tab = tab or self.latest_tab
        # 查找文本为 “下一页” 的 button 或 a 标签元素，normalize-space 用于去除文本两端的空格；not(@disabled) 用于排除已禁用的按钮
        sel = 'xpath://button[normalize-space(text())="下一页" and not(@disabled)] | //a[normalize-space(text())="下一页"]'
        return self.ele_for_action(sel, tab=tab, timeout=timeout)

    def _run_callback(
        self,
        page_callback: Callable,
        *args,
        tab: Union[ChromiumTab, MixTab, None] = None,
        refresh_on_None: bool = False,
        ignore_cache: bool = False,
        retry_times: int = 0,
        **kwargs,
    ) -> any:
        """
        运行回调函数，并处理异常和重试逻辑。

        :param page_callback: 页面回调函数
        :param args: 位置参数
        :param kwargs: 关键字参数
        :param tab: 标签页对象，默认为 None
        :param refresh_on_None: 回调函数返回 None 或异常时是否刷新页面
        :param ignore_cache: 刷新页面时是否忽略缓存
        :param retry_times: 重试次数
        :return: 回调函数的返回结果，全部失败时返回 None
        """
        current_tab = tab or self.latest_tab
        for attempt in range(retry_times + 1):
            try:
                result = page_callback(*args, **kwargs)
                if result is not None:
                    return result
            except Exception as e:
                self.log.error(f"❌ page_callback 执行异常: {e}")

            if refresh_on_None and attempt < retry_times:
                self.log.info(
                    f"🔄 回调返回 None 或异常，刷新页面进行第 {attempt + 1} 次重试..."
                )
                try:
                    current_tab.refresh(ignore_cache=ignore_cache)
                except Exception as e:
                    self.log.error(f"❌ 刷新页面异常: {e}")

            time.sleep(0.5)
        return None

    def next_page(
        self,
        page_callback: Callable[[Union[ChromiumTab, MixTab], int], any],
        parse_current_page: bool = True,
        callback_retry_times: int = 0,
        page_fail_stop: bool = False,
        expect_new_tab: bool = False,
        next_selector: Optional[Union[str, Tuple[str]]] = None,
        tab: Union[ChromiumTab, MixTab, None] = None,
        max_pages: Optional[int] = None,
        verify_selector: Optional[Union[str, Tuple[str]]] = None,
        verify_text: Optional[str] = None,
        verify_timeout: float = 5.0,
        timeout: float = 5.0,
        retry_times: int = 0,
        wait_time: float = 0.3,
    ) -> list:
        """
        通用翻页函数，自动点击“下一页”按钮，支持自定义查找和翻页逻辑。

        :param page_callback: 每次翻页后执行的回调函数，参数为(tab, page_index)，返回 None 表示处理失败，配合 callback_retry_times 参数程序会重试该页。非 None 时正常。
        :param parse_current_page: 是否解析当前页数据，默认为 True。
        :param callback_retry_times: page_callback 返回 None时重试的次数
        :param page_fail_stop: 如果 page_callback 返回 None，是否停止翻页。默认为 False，继续翻页。
        :param expect_new_tab: 点击下一页会有新标签页打开，默认为 False。
        :param next_selector: 下一页按钮的定位信息。为 None 时自动查找常见“下一页”按钮或a标签。
        :param tab: 标签页对象，默认为：self.latest_tab
        :param max_pages: 最大页数（默认起始页是第 1 页），None 表示自动翻页直到没有“下一页”
        :param verify_selector: 翻页后用于验证的元素定位
        :param verify_text: 翻页后用于验证的文本
        :param verify_timeout: 验证等待超时时间
        :param timeout: 查找“下一页”按钮的超时时间（秒）
        :param retry_times: 点击 下一页 失败时重试的次数
        :param wait_time: 每次翻页后的等待时间（秒）
        :return: parse_result，包含每一页 page_callback 的返回结果
        """
        tab = tab or self.latest_tab
        page_index = 1  # 页码索引，默认起始页是 1
        parse_result = []

        # 先处理当前页（如果需要）
        if parse_current_page:
            self.log.info("📄 处理起始页数据...")
            cb_result = self._run_callback(
                page_callback, tab, page_index, retry_times=callback_retry_times
            )
            parse_result.append(cb_result)
            if cb_result is None and page_fail_stop:
                self.log.error("❌ page_callback 处理起始页时返回 None，停止翻页")
                return parse_result

        while True:
            # 翻页前判断是否达到最大页数
            if max_pages is not None:
                if page_index >= max_pages:
                    self.log.info(f"⏭️ 已达到最大页数：{max_pages}，停止翻页")
                    break

            self.log.info(f"➡️ 开始翻页，当前页数: {page_index}")

            # 查找“下一页”按钮元素
            if next_selector is None:
                next_ele = self.auto_find_next_selector(tab, timeout=timeout)
            else:
                next_ele = self.ele_for_action(next_selector, tab=tab, timeout=timeout)

            if not next_ele:
                self.log.info("⛔ 未找到“下一页”按钮，停止翻页")
                break

            click_result = self.click_ele(
                next_ele,
                tab=tab,
                expect_new_tab=expect_new_tab,
                verify_selector_appear=verify_selector,
                verify_text_appear=verify_text,
                verify_timeout=verify_timeout,
                retry_times=retry_times,
            )

            if click_result is None:
                self.log.info("❌ 点击“下一页”按钮失败，停止翻页")
                break

            tab, _, is_success = click_result

            if not is_success:
                self.log.info("⚠️ 点击“下一页”按钮未通过验证，停止翻页")
                break

            page_index += 1
            self.log.info(f"📄 使用 page_callback 处理第 {page_index} 页...")

            cb_result = self._run_callback(
                page_callback, tab, page_index, retry_times=callback_retry_times
            )
            parse_result.append(cb_result)
            if cb_result is None and page_fail_stop:
                self.log.error(
                    f"❌ page_callback 处理第 {page_index} 页时返回 None，停止翻页！"
                )
                break

            time.sleep(wait_time)

        return parse_result

    def listen_network(
        self,
        targets: Union[str, List[str], Literal[True]] = True,
        tab: Union[ChromiumTab, MixTab, None] = None,
        tab_url: Optional[str] = None,
        timeout: Optional[float] = 10,
        count: int = 1,
        is_regex: bool = False,
        methods: Union[str, List[str]] = ("GET", "POST"),
        res_type: Union[str, List[str], Literal[True]] = True,
        stop_loading: bool = False,
        raise_err: bool = True,
        fit_count: bool = True,
        retry_times: int = 0,
        return_res: bool = True,
    ) -> Union[
        List[DataPacket],
        DataPacket,
        List[Union[dict, bytes, str, None]],
        Union[dict, bytes, str, None],
        None,
    ]:
        """
        监听网页中的网络请求，并返回捕获到的数据包。
        https://drissionpage.cn/browser_control/listener
        https://drissionpage.cn/browser_control/visit/#-none%E6%A8%A1%E5%BC%8F%E6%8A%80%E5%B7%A7
        https://drissionpage.cn/browser_control/listener/#%EF%B8%8F-datapacket%E5%AF%B9%E8%B1%A1

        :param targets: 要匹配的数据包 url 特征，可用列表指定多个，默认为：True 获取所有数据包
        :param tab: 要监听的浏览器标签页，默认为：None，使用 self.latest_tab
        :param tab_url: 要监听的标签页 URL，默认为：None，自动刷新当前 tab
        :param timeout: 等待数据包的最大时间（秒），默认 10 秒，为 None 表示无限等待
        :param count: 要捕获的数据包数量，默认 1 个
        :param is_regex: 是否将 targets 作为正则表达式处理，默认：False
        :param methods: 要监听的请求方法，如 'GET'、'POST'，可传入字符串或列表
        :param res_type: 要监听的资源类型，如 'xhr'、'fetch'、'png'，默认：True 监听所有类型
        :param stop_loading: 是否在捕获数据包后停止页面加载，默认为 False
        :param raise_err: 超时是否抛出异常，默认抛出，设置为 False：超时会返回 False
        :param fit_count: 是否必须捕获到 count 个数据包才返回，默认 True：超时会返回 False，设置为 False：超时会返回已捕捉到的数据包
        :param retry_times: 捕获失败时重试的次数，默认为 0 表示不重试
        :param return_res: 是否返回数据包的 response 的 body 数据，默认为：True：如果是 json 格式，转换为 dict；如果是 base64 格式，转换为 bytes，其它格式直接返回文本
        :return: 捕获到的数据包列表或单个数据包，超时或未捕获到数据包时返回 None；return_res=True 时返回 response 的 body 数据
        """
        tab = tab or self.latest_tab

        for attempt in range(retry_times + 1):
            self.log.info("📡 开始监听网络请求...")

            try:
                tab.listen.start(
                    targets=targets,
                    is_regex=is_regex,
                    method=methods,
                    res_type=res_type,
                )
            except Exception as e:
                self.log.error(f"❌ 启动监听器失败: {e}")
                return None

            try:
                if tab_url:
                    self.log.info(f"🔄 访问：{tab_url} 以开始捕获数据包...")
                    tab.get(tab_url)
                else:
                    self.log.info("🔄 刷新页面以开始捕获数据包...")
                    tab.refresh(ignore_cache=True)
            except Exception as e:
                self.log.error(f"❌ 页面刷新或访问失败: {e}")
                tab.listen.stop()
                return None

            self.log.info(
                f"✅ 监听目标：{targets}（正则模式：{is_regex}），"
                f"方法：{methods}，"
                f"资源类型：{'所有类型' if res_type is True else res_type}，"
                f"目标数量：{count}{'（超时会返回 None）' if fit_count else '超时会返回已捕捉到的数据包'}，"
                f"返回 response 数据：{return_res}，"
                f"超时时间：{timeout} 秒。"
            )
            # https://drissionpage.cn/browser_control/listener/#-listenwait
            try:
                result = tab.listen.wait(
                    count=count,
                    timeout=timeout,
                    fit_count=fit_count,
                    raise_err=raise_err,
                )
            except Exception as e:
                self.log.warning(f"⚠️ 捕获数据包时发生异常: {e}")
                result = None

            tab.listen.stop()
            self.log.info("🛑 监听结束，监听器已关闭。")

            if stop_loading:
                self.log.info("🛑 停止页面加载...")
                tab.stop_loading()

            if not result:
                self.log.warning("⚠️ 未能在规定时间内捕获到满足条件的数据包！")
                if attempt < retry_times:
                    self.log.info(f"🔁 即将进行第 {attempt + 1} 次重试 ...")
                    continue
                return None

            if isinstance(result, list):
                self.log.info(f"📦 已捕获 {len(result)} 个数据包。")
            else:
                self.log.info("📦 已捕获 1 个数据包。")

            # https://drissionpage.cn/browser_control/listener/#-response%E5%AF%B9%E8%B1%A1
            if return_res:

                def get_body(pkt):
                    try:
                        return pkt.response.body
                    except Exception as e:
                        self.log.warning(f"⚠️ 获取 response 数据失败: {e}")
                        return None

                if isinstance(result, list):
                    return [get_body(pkt) for pkt in result]
                else:
                    return get_body(result)

            return result

        return None
