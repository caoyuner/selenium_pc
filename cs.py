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
from openpyxl import Workbook,load_workbook
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC









def end_excel(row_data:list,file_name="ad_jj.xlsx"):
    if os.path.exists(file_name):
        wb=load_workbook(file_name)
        ws=wb.active
    else:
        wb=Workbook()
        ws=wb.active
        ws.append(row_data)
        wb.save(file_name)
        wb.close()







#2
url=input("请输入网站")
edge_options = Options()
edge_options.add_argument('--start-maximized')
edge_options.add_argument('--disable-gpu')
driver=webdriver.Edge(options=edge_options)
driver.get(url)

time.sleep(random.uniform(3.4,5.215))
#3
search=driver.find_element(By.XPATH,'//*[@id="read"]/div[2]/div[1]/div[2]/form/input[1]')
search.clear()
search.send_keys(input("请输入作者"))
search.send_keys(Keys.ENTER)
time.sleep(random.uniform(3.31,5.155))


# 创建显式等待对象：最长等待5.26秒
wait = WebDriverWait(driver, 5.26)

# 等待页面出现 div.hot.hothtml 这个父容器，找到之后把这个元素赋值给parent_box
# EC.presence_of_element_located：只要DOM里存在这个元素就算成功，不用等完全可见
parent_box=wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.hot.hothtml')))

# 在上面这个父容器内部，查找所有 class="item" 的div，结果是元素列表
item_list=parent_box.find_elements(By.CSS_SELECTOR,'div.item')

# 获取列表长度，也就是item的总个数
total=len(item_list)
print("搜索到的",total)

# 定义空列表，用来存放提取出来的url链接




url_result = []

# 循环遍历每一个item，idx是下标（从0开始），item是当前遍历到的div.item元素
for idx, item in enumerate(item_list):
    try:
        # 在当前item内部找<a>超链接标签
        a_tag = item.find_element(By.TAG_NAME, "a")
        # 获取a标签的href属性，就是网页链接
        link = a_tag.get_attribute("href")
        # 把链接存入url_result列表
        url_result.append(link)
        # 打印当前这条链接，idx+1，序号从1开始展示
        print(f"第{idx+1}条链接：{link}")
    except Exception as e:
        # 如果上面代码报错（找不到a标签等），执行这里
        print(f"第{idx+1}个item没有a标签链接，跳过")
        continue # 跳出本次循环，直接进入下一个item

# 循环结束，打印全部收集到的链接
print("\n全部url列表：")
print(url_result)


client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["xs_ad"]
coll = db["jiejie"]


for url in url_result:
    driver.get(url)
    time.sleep(random.uniform(3.4,5.215))
    source=driver.page_source
    soup = BeautifulSoup(source, "html.parser")
    name=soup.find(id="title").text.strip()
    author_name=soup.find(id="author").text.strip()
    author=author_name.replace("作者：","")
    print(author)
    book_dir=os.path.join(f"{author}的小说",name)
    os.makedirs(book_dir, exist_ok=True)
    list_url=soup.find('div',id="list").find_all('a',href=True)
    all_url=[]
    for url in list_url:
        head_url = "https://www.bqg880.xyz"
        home_url = head_url + url.get("href").replace("/#", "")
        all_url.append(home_url)

    for url in all_url:
        driver.get(url)
        time.sleep(random.uniform(4.4,8.215))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        title = soup.find(id="title").text.strip()
        content_div = soup.find("div", id="chaptercontent")
        if content_div:
            content = content_div.get_text(strip=False)
        else:
            print("无文本")

        file_path = os.path.join(book_dir, f"{title}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            print(f"已经保存了{title}")
        doc = {
            "book_name": name,
            "author": author,
            "chapter_title": title,
            "chapter_url": url,
            "content": content,
            "crawl_time": datetime.now()
        }
        coll.insert_one(doc)
        data=[f"文章{title}",f"URL{url}",f"作者{author}",f"内容{content}"]
        end_excel(data)







