from django.shortcuts import render , redirect
from django.http import HttpResponse

from urllib.parse import quote
import re
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

#from tkinter import Tk
#from tkinter import messagebox

# Create your views here.

#グローバル変数を利用し、更新箇所以外は値を残す。（無駄な処理をしない）

######################################################################################
######################################################################################
#■関数宣言

#【概ね完了】
#入力したタイトルもどきを以下のサイトで検索したときのトップに出た本のタイトル・ISBN13と２、３…番目に出た本のタイトルを取得。
#http://www.books.or.jp/
#引数：入力したタイトルもどき　戻り値（辞書）：{真偽(正常取得できたか？)、（検索トップの）本のISBN13、タイトル、定価、２番目に出た本のタイトル、3番目に出た本のタイトル}　
def search_books_or_jp(given_title_tmp , given_writer_tmp , given_syuppansya_tmp , max_data_num = 20):
        
    #情報を1件で取得できたらTrueにする
    exist = False
    
    #検索結果をTOPから順に格納
    list_results = []
    
    #検索結果画面
    url_mae = 'http://www.books.or.jp/ResultList.aspx?scode=&searchtype=0'
    
    title_url_encoding = '&title=' + quote(given_title_tmp.encode('sjis'))
    writer_url_encoding = '&writer=' + quote(given_writer_tmp.encode('sjis'))
    syuppansya_url_encoding = '&syuppansya=' + quote(given_syuppansya_tmp.encode('sjis'))
    
    url_ato = '&showcount=' + str(max_data_num) + '&startindex=0'
    
    url_search_result = url_mae + title_url_encoding + writer_url_encoding + syuppansya_url_encoding + url_ato
    
    #検索トップの本のタイトル、isbn13、価格
    top_title = ''
    top_isbn = ''
    top_price = 0
    #２、３番目の本のタイトル
    top_2_title = ''
    top_3_title = ''
    
    res_info = requests.get(url_search_result)

    #正常に情報取得できた場合
    if str(res_info.status_code)[0] == '2':            
        #検索結果一覧（0件ならばNone）
        search_result_list_tmp = BeautifulSoup(res_info.text , 'html.parser').find('table' , id = 'htBookList')
        
        #結果0件でない場合
        if search_result_list_tmp != None:
            #検索結果一覧をリスト化
            search_result_list = search_result_list_tmp.find_all('tr')[1:]

            #画面で取得できるデータを1件ずつ取得
            for i in range(len(search_result_list)):

                book_info = search_result_list[i].find_all('td')

                #検索トップ
                #if (i + 1) == 1:


                #タイトル、価格
                top_title = book_info[0].text
                top_price = int(book_info[3].text.replace('\\' , '').replace(',' , ''))

                #isbn13を取得するため、リンク先へ飛ぶ
                top_info_link = 'http://www.books.or.jp/' + book_info[0].find_all('a')[0].get('href').replace('amp;' , '')
                res_top_info_link = requests.get(top_info_link)

                #正常に情報取得できた場合
                if str(res_top_info_link.status_code)[0] == '2':
                    detail_list = BeautifulSoup(res_top_info_link.text , 'html.parser').find_all('div')
                    
                    #対象情報が無い場合のため、初期化
                    sub_title = ""
                    contents_introduction = ""
                    c_code = ""

                    for i in range(len(detail_list)):
                        
                        #「著者名」の次が著者名
                        if detail_list[i].text.strip() == '著者名':
                            writer = detail_list[i + 1].text.strip()
                            continue
                        #「サブタイトル」の次がサブタイトル
                        elif detail_list[i].text.strip() == 'サブタイトル':
                            sub_title = detail_list[i + 1].text.strip()
                            continue
                        #「ISBN」の次がISBN番号
                        elif detail_list[i].text.replace('-' , '') == 'ISBN':
                            top_isbn = detail_list[i + 1].text.replace('-' , '')
                            continue
                        #「C-CODE」の次がC-CODE
                        elif detail_list[i].text.strip() == 'C-CODE':
                            c_code = detail_list[i + 1].text.strip()
                            continue
                        #「サイズ」の次がサイズ
                        elif detail_list[i].text.replace('-' , '') == 'サイズ':
                            size = detail_list[i + 1].text.strip()
                            continue
                        #「ページ数」の次がページ数
                        elif detail_list[i].text.replace('-' , '') == 'ページ数':
                            page_num = detail_list[i + 1].text.strip()
                            continue
                        #「発行年月」の次が発行年月
                        elif detail_list[i].text.replace('-' , '') == '発行年月':
                            date_of_publication = detail_list[i + 1].text.strip()
                            continue
                        #「出版社」の次が出版社
                        elif detail_list[i].text.replace('-' , '') == '出版社':
                            syuppansya = detail_list[i + 1].text.strip()
                            continue
                        #内容紹介（これが最後なのでbreak）
                        elif detail_list[i].get('id') == 'htrBookNaiyou':
                            contents_introduction = detail_list[i].text.replace('内容紹介' , '').strip()
                            break                            

                    #OrderedDictの引数用
                    entity_for_o_dict = (('title' , top_title)
                                            , ('writer' , writer)
                                            , ('sub_title' , sub_title)
                                            , ('price' , top_price)
                                            , ('size' , size)
                                            , ('page_num' , page_num)
                                            , ('date_of_publication' , date_of_publication)
                                            , ('syuppansya' , syuppansya)
                                            , ('contents_introduction' , contents_introduction)
                                            , ('link' , top_info_link)
                                            , ('c_code' , c_code)
                                            , ('isbn' , top_isbn))

                    entity_for_list_results = OrderedDict(entity_for_o_dict)

                    list_results.append(entity_for_list_results)

                    #情報を取得できたのでTrueにする
                    exist = True

    
    #取得データがある場合
    if exist :
        return {'exist':exist , 'list_results':list_results}
    else:
        return {'exist':exist}

#ISBN13をISBN10に変換(引数：isbn13(str) 戻り値：isbn10(str))
def isbn13_10(isbn13):
    #戻り値
    isbn10 = ''
    
    isbn10_tmp = ''
    
    #頭３文字と後ろ1文字を外す。
    isbn10_tmp = isbn13[3 : 12]
    
    #外した後のものにチェックデジットを算出し、後ろにつける
    checkdigit = ''
    checkdigit_tmp = 0
    
    for i in range(len(isbn10_tmp)):
        checkdigit_tmp += int(isbn10_tmp[i]) * (10 - i)
    else:
        checkdigit_tmp = 11 - (checkdigit_tmp % 11)
    
    if checkdigit_tmp == 11:
        checkdigit = '0'
    elif checkdigit_tmp == 10:
        checkdigit = 'X'
    else:
        checkdigit = str(checkdigit_tmp)
    
    isbn10 = isbn10_tmp + checkdigit
        
    return isbn10

#amazon検索結果（引数：isbn13　戻り値：{真偽(正常取得できたか？) , URL , 価格}）
def search_result_amazon(isbn13):
    #サイト名
    site_name = 'amazon'
    
    url_mae = 'https://www.amazon.co.jp/dp/'
    url_ato = ''
    
    url = url_mae + isbn13_10(isbn13) + url_ato
    
    res_info = requests.get(url)
    
    #正常に情報取得できた場合
    if str(res_info.status_code)[0] == '2':
        taisho_html_bs = BeautifulSoup(res_info.text , 'html.parser')
        
        #中古価格
        taisho_tag_info_old = taisho_html_bs.find('span' , class_ = 'olp-used olp-link')
        #新品価格
        taisho_tag_info_new = taisho_html_bs.find('span' , class_ = 'olp-new olp-link')
        
        #中古があれば中古情報を取得
        if taisho_tag_info_old != None:
            taisho_tag_info_tmp = taisho_tag_info_old
        elif taisho_tag_info_new != None:
            taisho_tag_info_tmp = taisho_tag_info_new
        else:
            return {site_name : OrderedDict((('success' , '成功')
                                    , ('price' , float('inf'))
                                    , ('url' , url)))}
            #return {'success':False , 'url':url}
            
        taisho_tag_info = taisho_tag_info_tmp.find_all('a')[0]

        #テキスト部分抽出(要加工)
        price_tmp_1 = taisho_tag_info.text

        #改行、空白削除（処理後（例）：￥1,268より7中古品の出品）
        price_tmp_2 = price_tmp_1.replace('\n' , '').replace(' ' , '')

        #「より」を境に分割し、価格のある方を取得（処理後（例）：￥1,268）
        pattern = '(.*)より(.*)'
        price_tmp_3 = re.search(pattern , price_tmp_2).group(1)

        #￥とカンマを削除し、数値化
        price = int(price_tmp_3.replace('￥' , '').replace(',' , ''))
        
        #テスト
        print('**' * 10)
        print('amazon' , 'OK')
        print('**' * 10)
        
        return {site_name : OrderedDict((('success' , '成功')
                                    , ('price' , price)
                                    , ('url' , url)))}
        #return {'success':True , 'url':url ,'price':price}
        
    else:
        
        return {site_name : OrderedDict((('success' , '失敗')
                                    , ('price' , float('inf'))
                                    , ('url' , url)))}
        #return {'success':False , 'url':url}

#楽天古本市場 検索結果（引数：isbn13　戻り値：{真偽(正常取得できたか？) , 価格}）
def search_result_rakutenhuruhon(isbn13):
    #サイト名
    site_name = '楽天'
    
    url_mae = 'https://search.rakuten.co.jp/search/event/'
    url_ato = '/200162/?ev=19&f=1&s=4&evsitem=%E3%80%90%E4%B8%AD%E5%8F%A4%E3%80%91'
    
    url = url_mae + isbn13 + url_ato

    res_info = requests.get(url)
    
    #正常に情報取得できた場合
    if str(res_info.status_code)[0] == '2':
        search_rusult_bs = BeautifulSoup(res_info.text , 'html.parser')
        
        detail_page_link_div = search_rusult_bs.find('div' , class_ = 'extra content').findNext('div' , class_ = 'extra content')
        
        if detail_page_link_div != None:
            detail_page_link = detail_page_link_div.find_all('a')[0].get('href')
            
            #変数urlを更新
            url = detail_page_link
            
            res_detail_info = requests.get(detail_page_link)
            detail_bs = BeautifulSoup(res_detail_info.text , 'html.parser')
            detail_info = detail_bs.find('div' , class_ = 'topProduct__otherShopInfo')
            
            #新品価格
            #new_price = detail_info.find_all('span')[0].find_all('span')[0].replace(',' , '').replace('円' , '').replace('～' , '')
            #中古価格
            #old_price = detail_info.find_all('span')[1].find_all('span')[0].replace(',' , '').replace('円' , '').replace('～' , '')
            
            price_info_list = detail_info.find_all('span')
            
            #新品価格用
            new_price = None
            #中古価格用
            old_price = None
            #戻り値用（中古があれば中古価格）
            price = None
            
            for i in range(len(price_info_list)):
                if price_info_list[i].find_all('a') != []:
                    #新品価格
                    if price_info_list[i].find_all('a')[0].text[:2] == '新品':
                        new_price = int(price_info_list[i].findNext('span').text.replace(',' , '').replace('円' , '').replace('～' , ''))
                    #中古価格
                    elif price_info_list[i].find_all('a')[0].text[:2] == '中古':                        
                        old_price = int(price_info_list[i].findNext('span').text.replace(',' , '').replace('円' , '').replace('～' , ''))
                    else:
                        continue
            
            if old_price != None:
                price = old_price
            elif new_price != None:
                price = new_price
            else:
                return {site_name : OrderedDict((('success' , '失敗')
                                    , ('price' , float('inf'))
                                    , ('url' , url)))}
                #return {'success':False , 'url':url}
                
                
            #テスト
            print('**' * 10)
            print('楽天' , 'OK')
            print('**' * 10)
            
            return {site_name : OrderedDict((('success' , '成功')
                                    , ('price' , price)
                                    , ('url' , url)))}
            #return {'success':True , 'url':url , 'price':price}
            
        else:
            return {site_name : OrderedDict((('success' , '失敗')
                                    , ('price' , float('inf'))
                                    , ('url' , url)))}
            #return {'success':False , 'url':url}
         
    else:
        return {site_name : OrderedDict((('success' , '失敗')
                                    , ('price' , float('inf'))
                                    , ('url' , url)))}
        #return {'success':False , 'url':url}
    
#駿河屋 検索結果（引数：isbn13　戻り値：{真偽(正常取得できたか？) , 価格}）
def search_result_surugaya(isbn13):
    #サイト名
    site_name = '駿河屋'
    
    url_mae = 'https://www.suruga-ya.jp/search?category=&search_word=&bottom_detail_search_bookmark=1&gtin=&id_s=&jan10='
    url_ato = '&mpn='
    
    url = url_mae + isbn13_10(isbn13) + url_ato
    
    res_info = requests.get(url)
    
    if str(res_info.status_code)[0] == '2':
        taisho_html_bs = BeautifulSoup(res_info.text , 'html.parser')
        
        taisho_old_price_tag = taisho_html_bs.find('p' , class_ = 'price')
        
        if taisho_old_price_tag != None:
            price = int(taisho_old_price_tag.text.replace('税込' , '').replace('￥' , '').replace(',' , '').replace(' ' , ''))
            
            print('**' * 10)
            print('駿河屋' , 'OK')
            print('**' * 10)
            
            return {site_name : OrderedDict((('success' , '成功')
                                    , ('price' , price)
                                    , ('url' , url)))}
        else:
            return {site_name : OrderedDict((('success' , '失敗')
                                    , ('price' , float('inf'))
                                    , ('url' , url)))}
        
    else:        
        return {site_name : OrderedDict((('success' , '失敗')
                                , ('price' , float('inf'))
                                , ('url' , url)))}

#ネットオフ検索結果（POSTリクエスト）（引数：isbn13　戻り値：{真偽(正常取得できたか？) , URL , 価格}）
def search_result_netoff(isbn13):
    #サイト名
    site_name = 'ネットオフ'
    
    url_mae = 'https://www.netoff.co.jp/cmdtyallsearch/hdnAllSearchFlg/1/Ctgry/*/LRack/*/SetFlg/'
    url_ato = ''
    
    url = url_mae + url_ato
    
    #POSTリクエストのため、ISBNを入力したHTTPデータを作成
    http_data = {'cartShopCodeTxt':''
                    ,'cartCmdtyCodeTxt':''
                    ,'cartStndrdCodeTxt1':''
                    ,'cartStndrdCodeTxt2':''
                    ,'cartElementCodeTxt1':''
                    ,'cartElementCodeTxt2':''
                    ,'rsrvShopCodeTxt':''
                    ,'rsrvCmdtyCodeTxt':''
                    ,'rsrvStndrdCodeTxt1':''
                    ,'rsrvStndrdCodeTxt2':''
                    ,'rsrvElementCodeTxt1':''
                    ,'rsrvElementCodeTxt2':''
                    ,'dispModeTxt':''
                    ,'cmdtyFlagTxt':'ad'
                    ,'pageNumberTxt':'1'
                    ,'actionNameTxt':''
                    ,'ctc':'/'
                    ,'cat':''
                    ,'word':isbn13
                    ,'stock':''}
    
    #POSTリクエスト
    res_info = requests.post(url , data = http_data)
    
    #正常に情報取得できた場合
    if str(res_info.status_code)[0] == '2':
        taisho_html_bs = BeautifulSoup(res_info.text , 'html.parser')
        
        results_bs = taisho_html_bs.find('div' , id='dataId1')
        
        #検索結果が存在
        if results_bs != None:
            price_tmp = results_bs.find('li' , class_='clearfix resultRow').find('li' , class_='price mat5').text
            price = int(price_tmp.replace('円' , '').replace(',' , '').strip())
            
            #商品の詳細画面
            url = results_bs.find('a' , class_='fw').get('href')
            
            print('**' * 10)
            print('ネットオフ' , 'OK')
            print('**' * 10)
            
            return {site_name : OrderedDict((('success' , '成功')
                                        , ('price' , price)
                                        , ('url' , url)))}
        else:
            return {site_name : OrderedDict((('success' , '失敗')
                                        , ('price' , float('inf'))
                                        , ('url' , url)))}
        
    else: 
        return {site_name : OrderedDict((('success' , '失敗')
                                    , ('price' , float('inf'))
                                    , ('url' , url)))}

#ブックオフオンライン（selenium使用）
def search_result_bookoff(isbn13):
    #サイト名
    site_name = 'ブックオフ'
    
    #トップ画面
    url_top = 'http://www.bookoffonline.co.jp/'
    
    #webdriverに設定用のオプション
    options = Options()
    
    #ヘッドレス設定（ブラウザを表示しない）
    options.add_argument('--headless')

    #phantomJS起動
    #browser = webdriver.PhantomJS(executable_path=r'C:\Users\Takayoshi_Hoshino\phantomjs\bin\phantomjs.exe')

    #Chrome起動（ヘッドレス）
    browser = webdriver.Chrome(executable_path=r'C:\Users\Takayoshi_Hoshino\Desktop\インストール用ファイル\chromedriver_selenium\chromedriver_win32\chromedriver.exe' 
                                   , chrome_options=options)
    
    #ネットオフのトップへアクセス
    browser.get(url_top)

    #メモ：カテゴリリストは使わない（漫画と書籍が別々なっているため）

    #isbnをキーワードとして入力
    browser.find_element_by_id("tField").send_keys(isbn13)

    #検索ボタンをクリック
    browser.find_element_by_class_name("button").click()

    #検索結果のURLを取得（対象商品が無い場合の戻り値「url」の値にする）※但し、アクセスしても検索文字列は残ってない
    url_search_result = browser.current_url

    #検索結果画面をbs化
    bs_search_result = BeautifulSoup(browser.page_source , 'html.parser')

    #phantomJS（のみ）を閉じる　※全てのウィンドウを閉じる場合は quit()
    browser.close()

    #検索トップの商品のaタグ情報取得（詳細URL取得のため）
    taisho_p_tag_included_a_tag = bs_search_result.find("p" , class_ = "itemttl")

    #検索対象商品がある場合（在庫有無は以降で判別）
    if taisho_p_tag_included_a_tag != None:
        
        taisho_a_tag = taisho_p_tag_included_a_tag.find("a")

        #詳細画面URl
        url = 'http://www.bookoffonline.co.jp/' + taisho_a_tag.get('href')

        #在庫有無の判定
        div_tag_about_stock = bs_search_result.find("div" , class_="nostockbtn")

        #在庫が無い場合
        if div_tag_about_stock != None and div_tag_about_stock.text == '在庫がありません':
            
            #在庫は無いが、詳細画面があるので、urlは変数「url」を指定
            return {site_name : OrderedDict((('success' , '失敗')
                                        , ('price' , float('inf'))
                                        , ('url' , url)))}
        
        #在庫が有る場合
        else:
        
            print('**' * 10)
            print('ブックオフ' , 'OK')
            print('**' * 10)
            
            #価格取得
            price_text = bs_search_result.find("td" , class_="mainprice").text
            price = int(re.search("(.*)（税込）(.*)" , price_text).group(1).replace('￥' , '').replace(',' , '').strip())

            return {site_name : OrderedDict((('success' , '成功')
                                            , ('price' , price)
                                            , ('url' , url)))}
    #検索対象商品が無い場合
    else:
        return {site_name : OrderedDict((('success' , '失敗')
                                        , ('price' , float('inf'))
                                        , ('url' , url_search_result)))}
    
def set_compare_results(isbn13 , list_sites_search_func):
    #検索結果が１件でもあれば、True（関数リストに要素があれば、Trueになるはず）
    exist = False
    
    list_func_results = []
    
    for func in list_sites_search_func:
        list_func_results.append(func(isbn13))
    
    if len(list_func_results) > 0 :
        exist = True
        
    #価格で昇順ソート
    
    sorted_list_func_results = sorted(list_func_results , key = lambda x : list(x.items())[0][1]['price'])
    
    #価格がinfのやつは「-」に変更
    list_compare_info = sorted_list_func_results
    
    for compare_info in list_compare_info:
        dic_info = list(compare_info.items())[0][1]
        dic_info['price'] = dic_info['price'] if dic_info['price'] != float('inf') else '-'
    
    return {'exist':exist , 'list_compare_info':list_compare_info}
######################################################################################
######################################################################################


#【検索候補】

exist_serach_results = False
list_book_info_dic = None

#entity_1 = (('title','tttt') , ('price',1000) , ('link','http://aaa') , ('isbn','1234'))

#a = OrderedDict(entity_1)

#a = {'title':'tttt' , 'price':1000 , 'link':'http://aaa' , 'isbn':'1234'}
#list_book_info_dic.append(a)
#list_book_info_dic.append(a)



#【価格比較】

#本情報
exist_selected_book = False
selected_book_info = None

#entity_2 = (('title','勉強本') , ('price',1000) , ('isbn','1234'))
#selected_book_info = OrderedDict(entity_2)

#比較
exist_compare_info = False
list_compare_info = None


#entity_3 = (('success','成功') , ('price',1000) , ('url','http://bbb'))
#amazon_info = OrderedDict(entity_3)

#【注意】要素が一つの場合、最後にカンマを付けないとエラー
#entity_4 = (('amazon',amazon_info) , )

#b = OrderedDict(entity_4)

#list_compare_info .append(b)

#各サイトの検索関数のリスト(set_compare_results の引数)
list_compare_result_func = []

#--駿河屋
list_compare_result_func.append(search_result_surugaya)

#--楽天古本市場
list_compare_result_func.append(search_result_rakutenhuruhon)

#--amazon
list_compare_result_func.append(search_result_amazon)

#--ネットオフ
list_compare_result_func.append(search_result_netoff)

#--ブックオフオンライン
list_compare_result_func.append(search_result_bookoff)

def search_result(request):
	
	global exist_serach_results
	global list_book_info_dic
	
	#enumerate化
	if list_book_info_dic != None:
		enum_list_book_info_dic = enumerate(list_book_info_dic)
	else:
		enum_list_book_info_dic = None
	
	global exist_selected_book
	global selected_book_info
	
	global exist_compare_info
	global list_compare_info
	
	global contents
	
	global list_compare_result_func
	
	#確認ボタン押下
	if request.method == 'POST':
		
		#書籍確認を押下
		if "check" in request.POST and (request.POST['title_or_isbn'] != '' or request.POST['writer'] != '' or request.POST['syuppansya'] != ''):
			given_title_tmp = request.POST['title_or_isbn']
			given_writer_tmp = request.POST['writer']
			given_syuppansya_tmp = request.POST['syuppansya']
			 
			max_data_num = int(request.POST['max_data_num'])
			
			search_results_book_or_jp = search_books_or_jp(given_title_tmp , given_writer_tmp , given_syuppansya_tmp , max_data_num)
			
			exist_serach_results = search_results_book_or_jp['exist']
			
			if exist_serach_results:
				list_book_info_dic = search_results_book_or_jp['list_results']
				
				enum_list_book_info_dic = enumerate(list_book_info_dic)
				
				#messagebox.showinfo("【検索候補】", "データ取得完了")
				
				return redirect('/')
				
		#価格比較を押下
		elif "compare" in request.POST and (request.POST['title_or_isbn'] != '' or request.POST['writer'] != '' or request.POST['syuppansya'] != ''):
			given_title_tmp = request.POST['title_or_isbn']
			given_writer_tmp = request.POST['writer']
			given_syuppansya_tmp = request.POST['syuppansya']
			
			max_data_num = int(request.POST['max_data_num'])
			
			search_results_book_or_jp = search_books_or_jp(given_title_tmp , given_writer_tmp , given_syuppansya_tmp , max_data_num)
			
			exist_serach_results = search_results_book_or_jp['exist']
			
			if exist_serach_results:
				list_book_info_dic = search_results_book_or_jp['list_results']
				
				enum_list_book_info_dic = enumerate(list_book_info_dic)
				
				#検索候補TOPを対象に価格比較
				click_search_result_flg = 1
				index_clicked_search_result = 0
				
				#--対象のlist_book_info_dic の 要素を取得
				book_info_clicked_search_result = list_book_info_dic[index_clicked_search_result]
				
				#--本の一般情報用テンプレート変数に格納
				exist_selected_book = True
				
				#----タイトル、定価、リンク
				selected_book_info_tmp = ((key , value) for key , value in book_info_clicked_search_result.items() if key in ('title' , 'price' , 'link'))
				selected_book_info = OrderedDict(selected_book_info_tmp)
				
				#--各通販サイトでの検索
				#----ISBN番号を取得
				isbn13_clicked_search_result = book_info_clicked_search_result['isbn']
				
				#----各通販サイトの検索結果
				dic_compare_results = set_compare_results(isbn13_clicked_search_result , list_compare_result_func)
				
				#----テンプレート用変数に格納
				exist_compare_info = dic_compare_results['exist']
				list_compare_info = dic_compare_results['list_compare_info']
				
				#messagebox.showinfo("【検索候補】,【価格比較】", "データ取得完了")
				
				return redirect('/')
		
		else:
			#検索候補の一つをクリックしたか判定用フラグ
			click_search_result_flg = 0
			
			for key in request.POST:
				#検索候補の一つをクリックした場合
				if "_in_search_results" in key:
					click_search_result_flg = 1
					
					#対象のlist_book_info_dicのインデックス取得
					index_clicked_search_result = int(key.replace('_in_search_results' , ''))
					break
					
			#検索候補の一つをクリックした場合
			if click_search_result_flg == 1:
				#対象のlist_book_info_dic の 要素を取得
				book_info_clicked_search_result = list_book_info_dic[index_clicked_search_result]
				
				#本の一般情報用テンプレート変数に格納
				exist_selected_book = True
				
				#--タイトル、定価、リンク
				selected_book_info_tmp = ((key , value) for key , value in book_info_clicked_search_result.items() if key in ('title' , 'price' , 'link'))
				selected_book_info = OrderedDict(selected_book_info_tmp)
				
				#各通販サイトでの検索
				#--ISBN番号を取得
				isbn13_clicked_search_result = book_info_clicked_search_result['isbn']
				
				#--各通販サイトの検索結果
				dic_compare_results = set_compare_results(isbn13_clicked_search_result , list_compare_result_func)
				
				#--テンプレート用変数に格納
				exist_compare_info = dic_compare_results['exist']
				list_compare_info = dic_compare_results['list_compare_info']
				
				#messagebox.showinfo("【価格比較】", "データ取得完了")
				
				return redirect('/')
				
	contents = {'exist_serach_results':exist_serach_results , 'enum_list_book_info_dic':enum_list_book_info_dic
					, 'exist_selected_book':exist_selected_book , 'selected_book_info':selected_book_info
					, 'exist_compare_info':exist_compare_info , 'list_compare_info':list_compare_info}

	return render(request , 'search/search_result.html' , contents)