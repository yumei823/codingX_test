import requests
from bs4 import BeautifulSoup
import os
import time
from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np

class DrawChart():
    def __init__(self, datasize):
        self.datasize = datasize

    # 圓餅圖
    def DrawPie(self, font, labels_list, percent_list, title):		#labels_list: 圓餅圖的字   #percent_list: 圓餅圖各項的比例
        labels, sizes = [], []											
        plt.title(title, fontproperties = font)
        for i in range(self.datasize):
            labels.append(str(labels_list[i]))
            sizes.append(str(percent_list[i]))
        colors = cm.rainbow(np.arange(len(sizes))/len(sizes))
        pictures,category_text,percent_text = plt.pie(sizes, labels=labels, colors=colors, autopct='%1.2f%%', shadow=True, startangle=140)
        for i in category_text:
            i.set_fontproperties(font)
        plt.axis('equal')

    # 直方圖	
    def DrawBar(self, font, sem_list, bar_list, title):				#sem_list: 直方圖的每條上的字   #bar_list: 直方圖的長度
        plt.title(title, fontproperties = font)
        y_pos = np.arange(1)                                                            #y_pos產生y軸座標序列
        plt.xticks(y_pos + .3/2, (''), fontproperties = font)                           #xticks設定x軸刻度標籤
        for i in range(len(sem_list)):
            plt.bar(y_pos + 0.25*i , bar_list[i], 0.2, alpha=.5, label = sem_list[i])
        plt.legend(loc = "upper right", prop = font)

    # 輸出圖表與結果
    def chart_output(self, sum_all, semantic_list, sum_sem_list, percent_list):
        # 1準備繪圖
        pnb_list = []
        for sum_in_bar in range(self.datasize):
            bar_pnb = (sum_sem_list[sum_in_bar])
            pnb_list.append(bar_pnb)

        print('\r\r')
        print("總搜尋字彙出現個數為 : ", sum_all)
        for i in range(self.datasize):
            print(semantic_list[i],"出現個數為:",sum_sem_list[i],"百分比為",percent_list[i],"%")

        # 2將結果繪圖
        myfont = FontProperties(fname=r'./GenYoGothicTW-Regular.ttf')							#字型檔，r'裡面放你的字型檔案路徑'
        # 圓餅圖
        title1 = '關鍵字出現比例'
        plt.subplot(2,2,1)											#將圖表分割為2行2列，目前繪製的是第一格
        DrawChart.DrawPie(myfont, semantic_list, percent_list, title1)
        # 長條圖
        title2 = '關鍵字出現總數'
        plt.subplot(2,2,2)											#將圖表分割為2行2列，目前繪製的是第二格
        DrawChart.DrawBar(myfont, semantic_list, pnb_list, title2)

        plt.show()

class PTTcrawler():
    def __init__(self, board, datasize, semantic_list):
        self.page_num = 10
        self.board = board
        self.datasize = datasize
        self.semantic_list = semantic_list
        self.PTT_URL = 'https://www.ptt.cc/bbs/'
        self.sum_sem_list = []
        self.percent_list = []

    # 讀取PTT網頁
    def get_web_page(self, url):
        time.sleep(0.1)
        response = requests.get(url)    
        if response.status_code != 200:
            print('Invalid url:', response.url)
            return None
        else:
            return response.text

    # 對PTT網頁進行資料擷取
    def get_data(self, text):   #搜索節點
        soup = BeautifulSoup(text , 'html.parser')
        article = soup.find(id='main-content')
        return article

    # 讀取文章網址
    def get_article_url(self, text):
        url = []
        soup = BeautifulSoup(text, 'html.parser')
        get_divs = soup.find_all("div", "r-ent")   #把divs改成get_divs
        for div in get_divs:
            try:
                href = div.find('a')['href']
                url.append('https://www.ptt.cc' + href)
            except:
                pass
        return url

    # 爬蟲
    def crawler(self):
        articles = []		                              #那頁之中的所有文章，一個元素就是一篇文章跟所有留言的text們(字串)
        for page in range(self.page_num):	              #取得PTT頁面資訊
            # 1-10頁的網址
            for seman in range(self.semantic_list):
                url = self.PTT_URL + self.board + '/search?page=' + str(page+1) + '&q=' + self.semantic_list(seman)
                response = requests.get(url)              # get此頁資訊
                # 此頁抓到的text丟到get_article_url函式，去抓取每個有關鍵字的網址，做成list(urls)
                urls = self.get_article_url(response.text)
                # 進去每一個有關鍵字文章的網址
                for url in urls:
                    print(url)                            #印出網址
                    text = self.get_web_page(url)         #抓取有關鍵字文章網址中，所有text
                    arti = self.get_data(text)            #arti = article   #抓取所有text中的文章部分
                    articles.append(arti)                 #丟到articles list
                    ##所以 articles list 中的元素 arti 為PTT一頁之中，所有文章的網址中的文章text
                # 計算關鍵字出現次數，以及關鍵字出現的文章
                for sum_critic in range(self.datasize):        #for迴圈來一個一個計算關鍵字在第page頁的數量
                    sem_count = 0                              #關鍵字有幾個
                    for arti in articles:                      #在每一頁中，把每一篇文章頁面都拿來算裡面的關鍵字數量
                        #文章網址中的所有文字，包含的關鍵字數量的加總
                        sem_count += str(arti).count(semantic_list[sum_critic])    
                    sum_sem_list.append(sem_count)             #把每一篇文章有這個關鍵字的數量放進list中

    # 計算百分比，回傳關鍵字數量    
    def calculate_percent(self):
        sum_all = sum(self.sum_sem_list)                            #將所有找尋到的字彙個數相加，計算總合
        # 計算單一詞彙佔全部字彙的百分比
        for i in range(self.datasize):
            if sum_all != 0:
                self.percent_list.append(round((self.sum_sem_list[i]*100)/sum_all,2))
            else:
                self.percent_list.append(0)
        return sum_all

if __name__ == '__main__':
    print('''省錢: Lifeismoney/CPBL: Elephants/籃球: NBA,
            遊戲: LOL/Hate: HatePolitics/婚姻: marriage,
            車車: car/資訊: MobileComm/工作: Tech_Job,
            聊天: WomenTalk/心情: Boy-Girl/家庭: BabyMother,
            硬體: PC_Shopping/娛樂: joke/主機: PlayStation,
            韓國: KoreaStar/聯誼: AllTogether/理財: creditcard,
            高雄: Kaohsiung/台南: Tainan/CPBL: Lions,
            主機: NSwitch/CPBL:  Guardians/韓劇: KoreaDrama,
            綜藝: KR_Entertain/手遊: PCReDive/資訊: CVS,
            台中: TaichungBun/系統: iOS/美容: MakeUp''')
    board = str(input("請輸入想要搜尋的版(Ex:creditcard)  :  "))
    datasize = eval(input("請輸入欲分析的詞彙個數  :  "))
    semantic_list = []                                                     #存放輸入的關鍵字
    for num_word in range(datasize):
        semantic_in = input("請輸入第"+str(num_word+1)+"個關鍵字  :  ")     #想要找的關鍵字
        semantic_list.append(semantic_in)
    
    bug = PTTcrawler(board, datasize, semantic_list)
    bug.crawler()
    main_sum_all = calculate_percent()
    picture = DrawChart(datasize)
    picture.chart_output(main_sum_all, semantic_list, bug.sum_sem_list, bug.percent_list)