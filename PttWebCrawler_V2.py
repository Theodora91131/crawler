# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 04:38:03 2021

@author: actua
"""

from bs4 import BeautifulSoup
import requests

head1 = {'cookie':'over18=1'}

amount_list = []
title_list = []
author_list = []
date_list = []
for i in range(38914, 38910, -1):
    req = requests.get('https://www.ptt.cc/bbs/Gossiping/index' + str(i) + '.html', headers = head1)
    soup = BeautifulSoup(req.text, 'html.parser')
    
    amount_soup = soup.find_all('div', class_='nrec')
    title_soup = soup.find_all('div', class_='title')
    author_soup = soup.find_all('div', class_='author')
    date_soup = soup.find_all('div', class_='date')
    num = len(amount_soup)
    
    for i in range(num):
        if amount_soup[i].find('span') == None:
            amount_list.append(0)            
        elif  amount_soup[i].find('span').string.strip()=='爆':
            amount_list.append(100)
        elif amount_soup[i].find('span').string.strip()[0]=='X':
            amount_list.append(-1)
        else:
            amount_list.append(int(amount_soup[i].find('span').string.strip()))
        if title_soup[i].find('a') != None:
            title_list.append(title_soup[i].find('a').string.strip())
        else:
            title_list.append('')
        author_list.append(author_soup[i].string.strip())
        date_list.append(date_soup[i].string.strip())

import pandas as pd
df = pd.DataFrame({'amount':amount_list, 'title':title_list, 'author':author_list, 'date':date_list})
df.to_excel('ptt_article.xls', encoding='utf-8')