# scraper-TW-hotels (台灣旅宿爬蟲)

## 簡介
為協助女友解決工作需要抓取台灣所有合法的旅宿資訊，因此找到「台灣旅宿網」此網站並爬取旅館、民宿的基本資訊，並保存到 Excel 檔案中。該程式透過 `Python 2.7`、`requests`、`beautifuloup4` 和 `xlsxwriter` 開發並於 2017/08/05 完成，後因該網站改版更新，已有提供 CSV 資料匯出所以不需要此功能，維護更新只單純練習與更新版本為主。

目前版本更新至 `Python 3.7` 並改用 `pipenv` 安裝套件。因鮮版的網站撈取資料方式不同，採用 `seleniunm` 模擬點擊縣市取得各縣市的市區鄉鎮資料後，再透過 `aiohttp` 改成非同步請求網頁 HTML，並使用 `lxml` 以 XPath 抓取資料，再搭配少量 `beautifuloup4` HTML 解析，抓取下來後ㄧ樣使用 `xlsxwriter` 寫入 Excel。
過程中使用 `fake-useragent` 模擬 Header，另外因為網站多次請求會導致異常頁面，所以採用支持非同步的 Retry 函式庫 `tenacity` ，於偵測回應網址為異常網頁後，延遲依定秒數重新重試以確保資料撈取。

## 開發環境
- 程式語言：Python 3.7
- 使用套件：aiohttp, beautifuloup4, lxml, xlsxwriter, fake-useragent, seleniunm, tenacity

<br/>

## 啟動執行

```bash
$> pipenv install # 安裝 Pipfile 套件
$> pipenv shell # 進入 Pipenv 環境
$> python main.py # 執行
```


## 執行過程

**<p align="center">「台灣旅宿網」截圖</p>**
<p align="center">
  <img src="../master/Images/TWHotels-MainPage.png?raw=true">
</p>

**<p align="center">「台灣旅宿網」旅館列表截圖</p>**
<p align="center">
  <img src="../master/Images/TWHotels-MultiHotelsOfPage.png?raw=true">
</p>

**<p align="center">「台灣旅宿網」資訊頁面截圖</p>**
<p align="center">
  <img src="../master/Images/TWHotels-SingleHotelInfo.png?raw=true">
</p>

<br/>

<br/>

**<p align="center">指令輸入</p>**
<p align="center">
  <img src="../master/Images/Run.png?raw=true">
</p>

**<p align="center">執行過程</p>**

<p align="center">
  <img src="../master/Images/Parsing.png?raw=true">
</p>

**<p align="center">Excel 資料 - 金門縣</p>**

<p align="center">
  <img src="../master/Images/SaveExcel.png?raw=true">
</p>
