# ==============================
# @File    : novel_spider.py
# @Time    : 2026/10/04
# @Author  : 
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
5.错误内容
    在这里面的有一个问题，就是同一个作者的搜索会进行一个隐士判断，用来获得URL
"""

import os
import random
import time
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#2
url=input()
edge_options = Options()
edge_options.add_argument('--start-maximized')
edge_options.add_argument('--disable-gpu')
driver=webdriver.Edge(options=edge_options)
driver.get(url)

time.sleep(random.uniform(3.4,5.215))
#3
search=driver.find_element(By.XPATH,'//*[@id="read"]/div[2]/div[1]/div[2]/form/input[1]')
search.clear()
search.send_keys("阿刀")
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



