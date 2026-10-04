# ==============================
# @File    : zs.py
# @Time    : 2026/10/04
# @Author  : 
# @Version : Python3 + Selenium+time+random+mongodb
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
    终端执行：scrapy crawl zs

4、输出内容：
    小说标题、作者、章节链接、正文内容、来源网址结构化数据
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

