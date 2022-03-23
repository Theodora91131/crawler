import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
import time

import multiprocessing
from multiprocessing import Pool
cpu = multiprocessing.cpu_count()

######################################
# 主程式-- 從Google學術取得所需論文    #
######################################
def main():
    print('\n===============程式開始======================\n')
    keyword=input('請輸入欲查詢的關鍵字... ：')
    url='https://scholar.google.com/scholar?&hl=zh-TW&q='+keyword
    
    #取得初始結果頁面，以獲得搜尋出的總論文數
    soup = Get_PageContent(url)
    tot_articles_str = soup.select('div#gs_ab_md > div.gs_ab_mdw')[0].text.replace(',', '')
    tot_articles = [int(s) for s in tot_articles_str.split() if s.isdigit()][0]
    
    #一頁有10篇論文，計算頁數
    total_page_num = int(int(tot_articles)/10)+1
    print('\n查詢結果約有 {} 頁相關論文。'.format(total_page_num))
    page_want_to_crawl = input('一頁有10篇論文，請問你要爬取多少頁? ')

    if page_want_to_crawl == '' or not page_want_to_crawl.isdigit() or int(page_want_to_crawl) <= 0:
        print('\n所欲爬取的頁數輸入錯誤，離開程式。。。。。。')
        print('\n===============程式結束======================\n')        
    else:
        page_want_to_crawl = min(int(page_want_to_crawl), total_page_num)

        #取得各分頁之連結的url
        pages_link = Get_pages_link(url, page_want_to_crawl)

        print('\n計算中，請稍候。。。。。')
        start = time.time()

        #取得所有的論文資料
        articles = Get_Articles(pages_link)
        print('\n已取得所需論文，執行時間共 {} 秒。'.format(time.time()-start))
        
        Save2Excel(articles)
        print('\n====資料已順利取得，並已存入articles.xlsx中====\n')


#############################################
# 向伺服器發出請求，取得指定url的HTML原始碼    #
#############################################
def Get_PageContent(url):
    header_dict={'Host': 'scholar.google.com',
             'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Mobile Safari/537.36',
             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
             'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
             'Referer': 'https://scholar.google.com.tw/',
             'Connection': 'keep-alive',
             'cookie': 'SID=VgZ9mxS8mAzSWCseNui6lGEcUwqlt0xYfgxVfUOligzjl9p3ziRg1nVhQNeRxQ-MqahAWA.'}
    res = requests.get(
        url=url,
        headers=header_dict
        )
    content = BeautifulSoup(res.text, 'lxml')

    return content


##########################################################
# 取得各分頁的連結                                           #
##########################################################
def Get_pages_link(url, page_want_to_crawl):
    #取得各分頁的連結網址，並存入pages_link串列中
    pages_link = list()
    for i in range(0, int(page_want_to_crawl)*10, 10):
        link = url + '&start=' + str(i)
        pages_link.append(link)
    
    return pages_link


#############################
# 取得各分頁中的論文          #
#############################
def Parse_Get_MetaData(page_link):
    #取得各分頁的HTML原始碼
    soup = Get_PageContent(page_link)
    
    #取得本分頁的論文資料，並存入articles串列中
    page_articles = list()
    for item in soup.select('div.gs_or'):
        
        #取得論文下載的資源與下載連結
        if item.select('div.gs_or_ggsm > a'):
            source_type = item.select('div.gs_or_ggsm > a')[0].text
            download_link = item.select('div.gs_or_ggsm > a')[0].get('href')
        else:
            source_type ='No PDF OR HTML'
            download_link ='NO LINK'
    
        #取得每篇論文的所屬期刊與年份
        journal_year = item.select('div.gs_a')[0].text
        shift_1 = '-'
        shift_2 = ','
        journal_year = journal_year[journal_year.find(shift_1)+2:]
        journal = journal_year[:journal_year.find(shift_2)]
        year = [int(s) for s in journal_year.split() if s.isdigit()][0]

        #論文資料存入articles串列中
        page_articles.append({
                '標題':item.select('h3.gs_rt')[0].text,
                '期刊':journal,
                '年份':year,
                '簡介':item.select('div.gs_rs')[0].text if item.select('div.gs_rs') else '',
                '網址':item.select('h3.gs_rt > a')[0].get('href') if item.select('h3.gs_rt > a') else '',
                '下載檔案類型':source_type,
                '下載之連結':download_link
                })
        
    return page_articles


##########################################################
# 取得所有的論文                  #
##########################################################
def Get_Articles(pages_link):
    #取得各分頁中的論文，並存入 pages_article_list串列中
    with Pool(cpu) as p:
        pages_articles_list = p.map(Parse_Get_MetaData, pages_link)
    
    #將各分頁中的論文，統整存入 all_articles_list串列中
    all_articles_list = list()
    for each_page in pages_articles_list:
        for each_article in each_page:
            all_articles_list.append(each_article)
    
    return all_articles_list


###################################
# 將論文資料存入articles.xlsx 中   #
###################################
def Save2Excel(articles):
    titles = [entry['標題'] for entry in articles]
    journals = [entry['期刊'] for entry in articles]
    years = [entry['年份'] for entry in articles]
    details = [entry['簡介'] for entry in articles]
    links = [entry['網址'] for entry in articles]
    types = [entry['下載檔案類型'] for entry in articles]
    dlinks = [entry['下載之連結'] for entry in articles]

    df = DataFrame({
        '標題':titles,
        '期刊':journals,
        '年份':years,
        '簡介':details,
        '網址':links,
        '下載檔案類型':types,
        '下載之連結':dlinks
        })
    df.to_excel('articles.xlsx', sheet_name='sheet1', columns=['標題', '期刊', '年份', '簡介', '網址', '下載檔案類型', '下載之連結'])   


if __name__ == '__main__':
    main()