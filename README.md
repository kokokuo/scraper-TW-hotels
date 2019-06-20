# scraper-TW-hotels (台灣旅宿網爬蟲程式)

## 簡介
為協助女友解決工作需要抓取台灣所有合法的旅宿資訊，因此找到「台灣旅宿網」此網站並爬取旅館、民宿的基本資訊，並保存到 Excel 檔案中。該程式於 2017/08/05 完成，透過 `Python 2.7`、`requests`、`beautifuloup4` 實作，後因該網站改版更新，已有提供 CSV 資料匯出所以不需要此功能，維護更新只單純練習與更新版本為主。


**<p align="center">「台灣旅宿網」首頁截圖</p>**
<p align="center">
  <img src="../master/Images/TWHotels-MainPage.png?raw=true" width="640px">
</p>

**<p align="center">「台灣旅宿網」旅館列表截圖</p>**
<p align="center">
  <img src="../master/Images/TWHotels-MultiHotelsOfPage.png?raw=true" width="640px">
</p>

**<p align="center">「台灣旅宿網」資訊頁面截圖</p>**
<p align="center">
  <img src="../master/Images/TWHotels-SingleHotelInfo.png?raw=true" width="640px">
</p>


目前版本更新至 `Python 3.7` 並改用 `pipenv` 安裝套件，並且新增了儲存到 json 檔案格式中，用戶可以在一開始決定要儲存至 Excel 或是儲存到 json 檔案。

爬蟲方面因和原先舊版的網站撈取資料方式不同，採用 `seleniunm` 模擬點擊縣市取得各縣市的市區鄉鎮資料後，再透過 `aiohttp` 改成非同步請求網頁 HTML，並使用 `lxml` 以 XPath 抓取資料，再搭配少量 `beautifuloup4` HTML 解析，抓取下來依照原先選擇的儲存方式。

最後依照一開始選擇保存方式，若為到 Excel 則使用 `xlsxwriter` 寫入到 Excel 檔案中；選擇 json 則透過 `aiofiles` 非同步儲存到 json 格式的檔案內。


**<p align="center">儲存至 Excel - 金門縣</p>**

<p align="center">
  <img src="../master/Images/SaveExcel.png?raw=true" width="640px">
</p>


**<p align="center">儲存至 Json 資料 - 台北市</p>**

<p align="center">
  <img src="../master/Images/SaveJson.png?raw=true" width="640px">
</p>


過程中使用 `fake-useragent` 模擬 Header，另外因為網站多次請求會導致異常頁面，所以採用支持非同步的 Retry 函式庫 `tenacity` ，於偵測回應網址為異常網頁後，延遲依定秒數重新重試以確保資料撈取。

## 架構設計
由於該程式應用單純，不含業務場景，於是原先採用輕量的 [Transaction Script](https://martinfowler.com/eaaCatalog/transactionScript.html) 流程。而後為了達到整潔、職責分離，嘗試以 [DDD](https://en.wikipedia.org/wiki/Domain-driven_design) 的思維導入，透過 [Domain Model](https://martinfowler.com/eaaCatalog/domainModel.html) 去劃分，不過因為此爬蟲程式的 Scope 較小，業務場景難以捕捉，所以基本上以 [Domain Service](http://zhangyi.xyz/how-to-identify-application-service/) 搭配 [Value Object](https://martinfowler.com/bliki/ValueObject.html) 為主，或許未來可以嘗試再做調整。

```
--- apps # 應用服務模組
|  |
|   -- assembler # 組裝器，負責從不同的 Domain 的資料組裝成需要的資料集並轉換成 DTO 回傳
|  |
|   -- dto # 資料傳輸物件：展示層或 View 層需要的資料
|  |
|   -- services # 應用服務層：承接來自 Controller 的資料並作為處理業務需求相關的服務動作之第一層介面，類似 Facade，包裝業務場景的功能細節，會去調用 Domain 層的 Models 處理邏輯，以及儲存至資料庫等動作，或是做 Trasacntion 的檢查、日誌紀錄等。
|
--- domain # 領域模組：負責業務場景的細節
|   |
|    -- models # 領域模型
|
--- infra # infrastructure 基礎建設模組：放置領域模型或應用服務會使用的基礎工具或服務或實現領域會調用的底層細節
|   | 
|   -- asynchttp
|   |
|   -- excepts
|   |
|   -- logging
|
---- settings # 存放設定檔

```


## 開發環境
- 程式語言：Python 3.7
- 使用套件：`aiohttp`, `beautifuloup4`, `lxml`, `xlsxwriter`, `fake-useragent`, `seleniunm`, `tenacity`, `aiofiles`

<br/>

## 啟動執行

```bash
$> pipenv install # 安裝 Pipfile 套件
$> pipenv shell # 進入 Pipenv 環境
$> python scraping.py # 執行
```

## 執行過程

**<p align="center">指令輸入</p>**

<p align="center">
  <img src="../master/Images/Run.png?raw=true" width="640px">
</p>

**<p align="center">抓取過程</p>**
<p align="center">
  <img src="../master/Images/Parsing.png?raw=true" width="640px">
</p>
