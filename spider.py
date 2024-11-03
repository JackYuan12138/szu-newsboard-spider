# !/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import copy
import datetime
import logging
import smtplib
from config import *
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait


class Driver:
    class JSHandler:
        def __init__(self, js_path: str):
            self._js_path = js_path
            self.js_code = self.get_js()

        def get_js(self) -> str:
            with open(self._js_path, "r", encoding='UTF-8') as f:
                self.js_code = f.read()
            return self.js_code

        @staticmethod
        def refresh_window():
            return "window.location.reload()"

        @staticmethod
        def fill_login_form(id, password):
            return f"window.fill_login_form({id},{password})"

        @staticmethod
        def is_login():
            return "return window.is_login()"

        @staticmethod
        def do_login():
            return "window.do_login()"

    def __init__(self, url: str):
        self._URL = url
        self._driver = None
        self._is_init = False
        self._js_handler = self.JSHandler("web.js")
        self._get_driver()

    def _get_driver(self):
        # 浏览器设置
        browser_options = Options()
        browser_options.add_argument(
            'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/114.0.0.0"')
        browser_options.add_argument('--headless')
        browser_options.add_argument('--disable-gpu')
        browser_options.add_argument('window-size=1920x1080')

        self._driver = webdriver.Edge(options=browser_options)
        # 用于防止反爬
        self._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                            Object.defineProperty(navigator, 'webdriver', {
                              get: () => undefined
                            })
                          """
        })

        # 设置窗口大小
        self._driver.set_window_size(width=820, height=966)
        self._is_init = True

    def open_page(self):
        if not self._is_init:
            self._get_driver()
        else:
            # 打开网页，并等待网页加载完成
            self._driver.get(self._URL)
            WebDriverWait(self._driver, 120).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            self._driver.execute_script(self._js_handler.js_code)

    def refresh_window(self):
        self._driver.execute_script(self._js_handler.refresh_window())
        WebDriverWait(self._driver, 120).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        self._driver.execute_script(self._js_handler.js_code)

    def fill_login_form(self, id, password):
        self._driver.execute_script(self._js_handler.fill_login_form(id, password))

    def is_login(self):
        return self._driver.execute_script(self._js_handler.is_login())

    def do_login(self):
        self._driver.execute_script(self._js_handler.do_login())

    def get_page_source(self):
        return self._driver.page_source


def get_info_detail(info_element: Tag | NavigableString | None = None) -> dict[str:Tag | NavigableString | None] | None:
    """
    获取数据的详细信息,如类别，发文单位、标题、日期等
    :param info_element: html元素
    """
    valid_id = ['index', 'category', 'organization', 'title', 'date', 'link_img']
    try:
        index, category, organization, title, link_img, date = info_element.find_all('td')
        res = {
            'link_img': link_img,
            'index': index,
            'category': category,
            'organization': organization,
            'title': title,
            'date': date
        }
        for key in res:
            res[key]["detail_type"] = key
    except ValueError:
        try:
            res = {}
            _ = info_element.find_all('td')
            for el in _:
                if el.has_attr('detail_type') and el['detail_type'] in valid_id:
                    res[el['detail_type']] = el

            return res if len(res) > 0 else None

        except ValueError:
            res = None
    return res


def element_filter(title_element: Tag | NavigableString, info_elements: list[Tag | NavigableString]) -> tuple[Tag | NavigableString, list[Tag | NavigableString]]:
    """
    过滤数据，保留要展示的数据,并对数据的重要性进行标记
    :param title_element: 标题元素
    :param info_elements: 内容元素列表
    :return: 过滤后的数据
    """
    save_data = []
    display_tag = ['organization', 'title', 'link_img']

    # 如果是标题,保留要展示的标签
    if title_element:
        detail = get_info_detail(title_element)
        for key in detail:
            if key not in display_tag:
                detail[key].decompose()

    # 保存今天的数据
    for el in info_elements:
        detail = get_info_detail(el)
        if is_today(detail['date'].get_text()):
            # 删除不需要的标签
            for key in detail:
                if key not in display_tag:
                    detail[key].decompose()
            save_data.append(copy.copy(el))

    for index, el in enumerate(info_elements):
        if index < len(save_data):
            info_elements[index].replace_with(save_data[index])
        else:
            info_elements[index].decompose()

    return title_element, save_data


def sort_info(data: list[Tag | NavigableString | None] = None) -> list[Tag | NavigableString | None]:
    """
    对数据进行排序
    :param data: 对经过过滤的数据表格进行排序
    :return: 排序后的数据
    """
    sorted_data = [copy.copy(el) for el in data]

    def sort_key(el):
        return get_info_detail(el)['organization'].get_text()

    sorted_data.sort(key=sort_key)
    for index, el in enumerate(data):
        data[index].replace_with(sorted_data[index])
    return sorted_data


def beautify_html(table_title: Tag | NavigableString | None = None, info: list[Tag | NavigableString | None] | None = None):
    """
    美化html文本
    :param table_title: 表格标题的html元素
    :param notice: 表格内容的html元素
    """
    if table_title:
        table_title["class"] = "title_color"
        detail = get_info_detail(table_title)
        detail["organization"]["align"] = "center"
        detail["organization"]["width"] = "20%"

        # 设置标题列的样式
        detail['title']["align"] = "center"
        detail['title']["width"] = "80%"

    if info:
        for index, el in enumerate(info):
            if el.has_attr("bgcolor"):
                del el["bgcolor"]
            el["class"] = "info_color" + str(index % 2)
            detail = get_info_detail(el)
            detail["organization"]["align"] = "center"
            detail["organization"]["width"] = "20%"

            # 设置标题内容的样式
            detail['title']["align"] = "left"
            detail['title']["width"] = "80%"

            detail['title'].a["href"] = 'https://www1.szu.edu.cn/board//' + detail['title'].a["href"]
            detail['title'].a["class"] = "fontcolor_info_normal"
            detail['title'].a.string = detail['title'].a.get_text()

            # 设置附件图片链接
            if detail['link_img'].find('img'):
                detail['link_img'].find('img')['src'] = 'https://www1.szu.edu.cn/images/attach.gif'


def get_style_html() -> str:
    """
    获取html文本的样式,为邮件正文添加style样式
    :return: 样式html文本
    """
    with open('email.css', 'r') as f:
        css = f.read()
    return f'<style>{css}</style>'


def get_info_list(text: str) -> str:
    """
    从html文本中提取信息
    :param text: 来自公文通的原始html文本
    :return: 进行内容提取、排序以及美化后的html文本，作为邮件正文
    """
    soup = BeautifulSoup(text, 'html.parser')
    table = soup.find("table", attrs={"style": "border-collapse: collapse"})
    title, *info = table.find_all("tr")  # 提取标题和内容

    title, info = element_filter(title, info[1:])  # 过滤数据

    info = sort_info(info)  # 对数据进行排序

    beautify_html(title, info)  # 美化html文本

    style = get_style_html()
    print(style + table.prettify())
    return style + str(table)


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def get_email_content(data: str):
    send_str = '<p>以下是最新的公文通，请享用~</p>'
    send_str += data
    return send_str


def send_email(send_str, to_address, header='快来打开新鲜出炉的公文通叭~'):
    msg = MIMEText(send_str, 'html', 'utf-8')
    msg['From'] = _format_addr('公文通小助手 <%s>' % from_addr)
    msg['To'] = _format_addr('管理员 <%s>' % to_address)
    msg['Subject'] = Header(header, 'utf-8').encode()
    server = smtplib.SMTP(smtp_server, 25)
    # server.starttls()
    server.set_debuglevel(1)
    server.login(from_addr, password)

    count = 6
    while count:
        try:
            server.sendmail(from_addr, to_address, msg.as_string())
            break
        except Exception as e:
            logging.error(e)
            count -= 1

    server.quit()


def is_today(date_str: str) -> bool:
    """
    判断是否是今天
    :param date_str: 日期字符串
    :return: True 是今天，False 不是今天
    """
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return datetime.date.today() == date.date()


def get_current_hour():
    return str(datetime.datetime.now())[11: 13]


def get_pages(driver: Driver):
    driver.open_page()
    if not driver.is_login():
        driver.fill_login_form(board_id, board_password)
        driver.do_login()
    driver.open_page()
    while not driver.is_login():
        pass
    return driver.get_page_source()


if __name__ == "__main__":
    url = 'https://www1.szu.edu.cn/board/infolist.asp'
    driver = Driver(url)
    while True:
        if str(datetime.datetime.now())[14: 16] == '00' or str(datetime.datetime.now())[14: 16] == '30':
            print("公文通小助手已启动！", str(datetime.datetime.now()))
            break
    while True:
        if get_current_hour() == '12' or get_current_hour() == '21':
            pages = get_pages(driver)
            data = get_info_list(pages)
            msg = get_email_content(data)
            for addr in to_addr:
                send_email(msg, addr)
            logging.info('send successfully!')
        time.sleep(3600)
