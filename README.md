#### __Read this in other languages:__ [[Chinese(中文)]](README_CHT.md)<br><br>

# **tagui_demo_02**

## **RPA: Creating a schedule to periodically perform web scraping with "RPA for Python"**

### **Ⅰ. Purpose** 
TagUI is an open-source RPA tool. The package "RPA for Python" is based on TagUI. The content of this project is a demo to build an example of periodically performing web scraping with "RPA for Python".<br><br>

### **Ⅱ. Tools**
RPA for Python、APScheduler (Advanced Python Schedule)、MongoDB<br><br>

### **Ⅲ. Statement**

__1. The data of web scraping__ <br>

The targeted data is the holding details, like stocks, bonds and so on, of exchange-traded fund (ETF) in Taiwan. The ETFs are selected according to the standard that they primarily invest in stocks and their asset value is more than one hundred billion (TWD). Therefore, 8 ETFs are selected in this project. (Please refer to the list "etfs" in python script)<br>
In addition, the information about ETF ranking by asset value, trading volume and so on, in Taiwan can be read on the website, Yahoo Finance (Taiwan). (Please refer to [details](<https://tw.stock.yahoo.com/tw-etf/total-assets>))。<br>
<br> 

__2. Data source__ <br>

Thanks for the website, "https://www.pocket.tw/etf/", provided by Pocket Securities. This company, one of the best Online Brokers in Taiwan, delivers high-quality services to customers, and its website makes it easier for investors to obtain financial data and useful information. <br>
<br>

__3. How programming works__ <br>

Advanced Python Scheduler (APScheduler) is a Python library that lets you schedule your Python code to be executed later, either just once or periodically. The operation on website is implemented by "RPA for Python", and then APScheduler arranges this operation to execute periodically.
As you can see from the python script ("[rpa_scrap_etf.py](./rpa_scrap_etf.py)"), this operation will be executed every 10 minutes from 18:00 to 20:00 every day.<br>
<br>

__4. Results__ <br>

In python script, the content of html will be pared, processed, and then saved into a JSON file with the method modifying the existing records. (Please refer to "[etfs_holding.json](./outputs/etfs_holding.json)") <br>
Besides, the data after processing also will be updated into MongoDB. Checking whether the data exists in database can execute the python script (Please refer to "[save_db.py](./save_db.py)"), and then the result will be shown in the terminal as below. <br>

![avatar](./README_png/terminal_result.png)
<br><br>

__The above offers an example of periodically performing web scraping with RPA for Python.__ <br>

(Similar projects, please refer to: [tagui_demo_01](<https://github.com/qinglian1105/tagui_demo_01>) , [uipath_demo_01](<https://github.com/qinglian1105/uipath_demo_01>) , [power_automate_demo_01](<https://github.com/qinglian1105/power_automate_demo_01>) )
<br><br>

---

### **Ⅳ. References**

[1] [TagUI](<https://tagui.readthedocs.io/en/latest/index.html>)

[2] [RPA for Python: tebelorg/RPA-Python](<https://github.com/tebelorg/RPA-Python>)

[3] [Yahoo Finance(Taiwan) - ETF asset ranking](<https://tw.stock.yahoo.com/tw-etf/total-assets>)

[4] [Advanced Python Scheduler (APScheduler)](<https://apscheduler.readthedocs.io/en/3.x/>)

[5] [Pocket Securities - ETF](<https://www.pocket.tw/etf/>)