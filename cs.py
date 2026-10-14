# ==============================
# @File    : cs.py
# @Time    : 2026/10/04
# @Author  : https://www.bqg371.cc/#/book/32181/,https://www.bqg371.cc/
# @Version : Python3 + Scrapy/Selenium
# @Desc    : 小说网站全站章节、标题、作者、链接爬取
# @FileType: 动态网页爬虫采集脚本
# @Update  : 首次编写，支持Edge无头渲染
# ==============================

"""
文件说明：
1、文件功能：
    针对小说静态+动态混合页面进行数据爬取，自动渲染JS页面，解析书籍列表与章节链接，
    实现自动化采集、去重、持久化存储。

2、技术栈：
    Scrapy2.17 + Selenium Edge无头模式 + BS4解析
    管道支持 MongoDB数据库存储 + Excel本地备份双方案

3、运行方式：
    终端执行：scrapy crawl novel_spider

4、输出内容：
    小说标题、作者、章节链接、正文内容、来源网址结构化数据
5.步骤
    导入库，打开浏览器，输入URL，进入网站，搜索内容，进入书籍，进入章节，保存本地，保存数据库保存EXCEL

"""
#1


import os
import random
import time
from openpyxl import Workbook, load_workbook
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def save_to_excel(file_name: str, sheet_name: str, data_list: list):
    """
    :param file_name: excel文件名
    :param sheet_name: 工作表名称
    :param data_list: 待写入多行数据，格式 [[列1,列2,列3], [列1,列2,列3], ...]
    """
    # 判断文件是否存在
    if os.path.exists(file_name):
        wb = load_workbook(file_name)
    else:
        from openpyxl import Workbook
        wb = Workbook()

    # 获取工作表，不存在则新建
    if sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
    else:
        ws = wb.active
        ws.title = sheet_name
        # 写入表头
        ws.append(["书名", "链接", "作者"])

    # 批量追加多行
    for row_data in data_list:
        ws.append(row_data)

    # 实时保存
    wb.save(file_name)
    wb.close()
    print(f"已保存 {len(data_list)} 条数据到Excel")


def init_edge_driver():
    """初始化Edge浏览器driver"""
    edge_options = Options()
    edge_options.add_argument('--start-maximized')
    edge_options.add_argument('--disable-gpu')
    driver = webdriver.Edge(options=edge_options)
    return driver


def search_book_list(driver, base_url: str, author_keyword: str):
    """
    根据作者搜索，返回小说详情页链接列表
    """
    driver.get(base_url)
    time.sleep(random.uniform(3.4, 5.215))

    search = driver.find_element(By.XPATH, '//*[@id="read"]/div[2]/div[1]/div[2]/form/input[1]')
    search.clear()
    search.send_keys(author_keyword)
    search.send_keys(Keys.ENTER)
    time.sleep(random.uniform(3.31, 5.155))

    wait = WebDriverWait(driver, 5.26)
    parent_box = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.hot.hothtml')))
    item_list = parent_box.find_elements(By.CSS_SELECTOR, 'div.item')
    total = len(item_list)
    print("搜索到的数量：", total)

    url_result = []
    for idx, item in enumerate(item_list):
        try:
            a_tag = item.find_element(By.TAG_NAME, "a")
            link = a_tag.get_attribute("href")
            url_result.append(link)
            print(f"第{idx+1}条链接：{link}")
        except Exception as e:
            print(f"第{idx+1}个item没有a标签链接，跳过")
            continue
    print("\n全部url列表：")
    print(url_result)
    return url_result


def crawl_book_detail(driver, book_url):
    """进入小说主页，获取书名、作者、章节链接列表"""
    driver.get(book_url)
    time.sleep(random.uniform(3.4, 5.215))
    source = driver.page_source
    soup = BeautifulSoup(source, "html.parser")
    name = soup.find(id="title").text.strip()
    author_name = soup.find(id="author").text.strip()
    author = author_name.replace("作者：", "")

    # 章节链接
    list_url = soup.find('div', id="list").find_all('a', href=True)
    all_url = []
    head_url = "https://www.bqg880.xyz"
    for a in list_url:
        home_url = head_url + a.get("href").replace("/#", "")
        all_url.append(home_url)
    return name, author, all_url


def download_chapter(driver, chapter_url, save_dir):
    """下载单章节，保存txt"""
    driver.get(chapter_url)
    time.sleep(random.uniform(4.4, 8.215))
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    title = soup.find(id="title").text.strip()
    content_div = soup.find("div", id="chaptercontent")
    if content_div:
        content = content_div.get_text(strip=False)
    else:
        print("无文本")
        return
    file_path = os.path.join(save_dir, f"{title}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"已经保存了{title}")
    return title


def main():
    """主入口函数"""
    # mongo连接
    client = MongoClient("mongodb://127.0.0.1:27017/")
    db = client["xs_ad"]
    coll = db["jiejie"]

    # 输入参数
    url = input("请输入网站：")
    author_key = input("请输入作者：")

    # 初始化浏览器
    driver = init_edge_driver()
    try:
        # 搜索获取小说列表
        book_url_list = search_book_list(driver, url, author_key)

        # 遍历每本小说
        for book_url in book_url_list:
            book_name, author_name, chapter_urls = crawl_book_detail(driver, book_url)
            print(f"当前小说：{book_name} 作者：{author_name}")

            # 创建小说文件夹
            book_dir = os.path.join(f"{author_name}的小说", book_name)
            os.makedirs(book_dir, exist_ok=True)

            # 循环下载章节
            for chap_url in chapter_urls:
                download_chapter(driver, chap_url, book_dir)
                # 写入excel
                three_rows = [
                    [book_name, chap_url, author_name],
                ]
                save_to_excel(f"{author_name}的.xlsx", "sheet1", three_rows)
    finally:
        # 无论是否报错，最后关闭浏览器
        driver.quit()


if __name__ == "__main__":
    main()


