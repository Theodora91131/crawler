from bs4 import BeautifulSoup
import requests

head1 = {'cookie':'over18=1'}
req = requests.get('https://www.ptt.cc/bbs/Gossiping/index.html', headers = head1)

soup = BeautifulSoup(req.text, 'html.parser')
#soup.prettify

title_soup = soup.find_all('div', class_='title')
num = len(title_soup)

author_soup = soup.find_all('div', class_='author')
#print(author_soup[0].string, end=' | ')

date_soup = soup.find_all('div', class_='date')
#print(date_soup[0].string)
title_list = []
author_list = []
date_list = []
for i in range(num):
#    print("%-30s%s%s" % (title_soup[i].find('a').string.strip(), author_soup[i].string.strip(), date_soup[i].string.strip()))
    title_list.append(title_soup[i].find('a').string.strip())
    author_list.append(author_soup[i].string.strip())
    date_list.append(date_soup[i].string.strip())

import pandas as pd
df = pd.DataFrame({'title':title_list, 'author':author_list, 'date':date_list})
df.to_excel('ptt_article.xls', encoding='utf-8')