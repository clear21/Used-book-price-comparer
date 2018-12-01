# Used-book-price-comparer

# Overview
<b>より楽に！より安く！</b>中古本を購入するためのアプリです。

# Description
通販サイトで中古本を購入する下記のフローで <b>[本の検索]</b>～<b>[購入画面へアクセス]</b> が楽に行えるWebアプリです。  
（<b>本の検索</b> → 本の特定 → サイト1で価格確認 → サイト2で… → … → 購入サイトの決定 → <b>購入画面へアクセス</b> → …）

# Folders and Files
┏ mysite … プロジェクト管理用フォルダ  
┃　┣ …  
┃  
┣ search … アプリケーション管理用フォルダ  
┃　┣ templates … フロントエンド用プログラム（HTML）格納フォルダ  
┃　┃　┗ search  
┃　┃　　 ┗ search_result.html … フロントエンド用プログラム（HTML）   
┃　┣ templatetags … 自作タグの格納フォルダ  
┃　┃　┗ for_temp_tags.py … 自作タグの定義用  
┃　┣ views.py … スクレイピング処理等のバックエンド用プログラム（最も時間を費やしたファイル）  
┃　┣ …  
┃  
┗ manage.py … プロジェクト管理用プログラム（アプリ起動の際に実行する）  
※DB機能は無し

# Capture
![used_book_price_comparer](https://user-images.githubusercontent.com/39453720/46608590-4c1b4080-cb40-11e8-97cd-67714db7d2b4.png)
