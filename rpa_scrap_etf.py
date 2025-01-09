# rpa_scrap_etf.py
from apscheduler.schedulers.blocking import BlockingScheduler
from save_db import SaveMongo
import rpa as r
import datetime as dt
import pandas as pd
import os
import re
import json
import random
import sys



class ScrapingEtf:
    
    # Variables for functions as below
    def __init__(self):        
        self.today = dt.datetime.today().strftime('%Y/%m/%d')           
        self.pwd = os.getcwd()        
        self.folder_in = "inputs"
        self.folder_out = "outputs"
        self.file_in_trade_day = "twse_trade_days.csv"
        self.file_in_parameters = "parameters.json"
        self.file_out_etfs = "etfs_holding.json"
        self.etfs = ['0050','00878','0056','00919',
                     '00929','006208','00940','00713']
    
    # Read json file for parameter-variables        
    def read_json_to_dict(self, file_path):    
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                ds = json.load(file)
                return ds
        except FileNotFoundError:
            print(f"Not find: {file_path}")
        except json.JSONDecodeError as e:
            print(f"JSON coding error: {e}")
        except Exception as e:
            print(f"Unkown error: {e}")
        return None    
    
    # Parse html-table
    def parse_html_tb(self, html_string):    
        pattern = re.compile(r"""
            <tr>\s*            
            <td>(\d+)</td>\s*  
            <td>\s*<h2[^>]*title="([^"]+)"[^>]*>[^<]+</h2>\s*</td>\s* 
            <td>\s*<h2[^>]*title="([^"]+)"[^>]*>[^<]+</h2>\s*</td>\s* 
            <td>([\d,]+)</td>\s* 
            <td>([^<]+)</td>\s*   
            </tr>""", re.VERBOSE)    
        matches = pattern.findall(html_string)    
        result = []
        for match in matches:
            result.append({
                "s_code": match[0],
                "s_name": match[1],
                "holding_percentage": float(match[2]),
                "holding_amount": int(match[3].replace(",", "")),  
                "unit": match[4]
            })
        return result
    
    # Read csv-file for trading days 
    def get_trade_days_list(self): 
        try:       
            file_path = os.path.join(self.pwd, self.folder_in, self.file_in_trade_day)
            df = pd.read_csv(file_path)
            df.trade_day = df.trade_day.apply(lambda x: x.replace("-","/"))
            trade_days = list(df.trade_day)
        except Exception as e:
            print(e) 
        return trade_days
    
    # Check if data updates
    def chk_ds_update_(self, variables):                
        date_list = []
        output_path = os.path.join(self.pwd, self.folder_out, self.file_out_etfs)      
        if os.path.isfile(output_path):  
            try:      
                with open(output_path, mode='r') as f:
                    data = json.load(f)

                    date_list = []
                    for e in data:
                        date_list.append(e['holding_date'])
                    
            except Exception as e:
                print(e)     

        if self.today not in date_list:        
            r.init(headless_mode=True)  
            r.url(variables['pocket_url'])
            r.wait(1)

            t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')
            print("--->", f"Start to check 'holding_date' ({t})") 
            etfs_num = len(self.etfs) 
            update_num = 0   
            for etf in self.etfs:                                            
                r.type(variables['type_code'], etf)
                r.click(variables['click_code'])
                r.wait(0.5)
                r.click(variables['click_option'])
                r.wait(1)
                r.click(variables['click_holding'])
                r.wait(2.5)                    
                holding_date = r.dom(variables['dom_date']).strip()[5:]                               
                print("--->", etf, "(web_update_date: " + holding_date + ")")
                if holding_date == self.today:                                       
                    update_num = update_num + 1                    
                r.wait(random.randint(1,5))  

            r.close()  
              
            if update_num == etfs_num:
                return "All updated"
            else:
                return "Not updated"
        else:
            return "Done today"   
    
    # Operate website and get data         
    def get_ds_from_url(self, variables):         
        r.init(headless_mode=True)    
        r.url(variables['pocket_url'])
        r.wait(1)
        etf_list = []    
        for i, etf in enumerate(self.etfs): 
            etf_data = dict()                                               
            r.type(variables['type_code'], etf)
            r.click(variables['click_code'])
            r.wait(0.5)
            r.click(variables['click_option'])
            r.wait(1)
            r.click(variables['click_holding'])
            r.wait(2)   
            etf_name = r.dom(variables['dom_etf_name']).replace("\n", "") 
            etf_name = etf_name[0:etf_name.find("<span>")].strip()                           
            print("--->", etf, etf_name, "(parsing html...)")  
            if i < 1:
                holding_date = r.dom(variables['dom_date']).strip()[5:]
                r.wait(1)
            t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')    
            html_str = r.dom(variables['dom_tb'])
            r.wait(1)        
            parsed_data = self.parse_html_tb(html_str) 

            # Prevent from getting uncompleted data
            if parsed_data==[] or len(parsed_data)<20: 
                print("--->", etf, etf_name, "(re-parsing html...)") 
                r.type(variables['type_code'], etf)
                r.click(variables['click_code'])
                r.wait(0.5)
                r.click(variables['click_option'])
                r.wait(1)
                r.click(variables['click_holding'])                
                r.wait() 
                parsed_data = self.parse_html_tb(html_str)
                        
            etf_data['etf_code'] = etf        
            etf_data['etf_name'] = etf_name        
            etf_data['scraping_time'] = t 
            etf_data['etf_holding'] = parsed_data            
            etf_list.append(etf_data)            
            
            r.wait(random.randint(1,5))  

        daily_ds = dict() 
        daily_ds['holding_date'] = holding_date        
        daily_ds['etf_data'] = etf_list
             
        r.close()            
        return [holding_date, daily_ds]
    
    # Workflow with conditions
    def processes(self):        
        trade_list = self.get_trade_days_list()
        if self.today in trade_list:            
            file_path = os.path.join(self.pwd, self.folder_in, self.file_in_parameters)
            variables = self.read_json_to_dict(file_path) 
            
            flag = self.chk_ds_update_(variables)             
            if flag in ['All updated']: 
                t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')
                print(f"Start scraping job ({t})")    
                res = self.get_ds_from_url(variables)

                counts = 0
                for etf in res[1]['etf_data']:
                    securities = len(etf['etf_holding'])
                    counts = counts + securities
                                             
                output_path = os.path.join(self.pwd, self.folder_out, self.file_out_etfs)                
                if os.path.isfile(output_path): 
                    try:       
                        with open(output_path, mode='r') as f:
                            data = json.load(f)                               
                        data.append(res[1])                                 
                    except Exception as e:
                        print(e)                         
                    try:    
                        with open(output_path, 'w', encoding='utf-8') as fp:
                            json.dump(data, fp, ensure_ascii=False, indent=4)
                            t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')   
                            print(f"Completed: {counts:,} records are written into JSON file ({t})")    

                        savemongo = SaveMongo()
                        savemongo.insert_daily_efts(res[1], res[1]['holding_date'])
                        print(f"Updated: {counts:,} records are updated to MongoDB ({t})")   

                    except Exception as e:
                        print(e)     
                else:
                    try:                                
                        with open(output_path, 'w', encoding='utf-8') as fp:                            
                            json.dump(res[1], fp, ensure_ascii=False, indent=4) 
                            t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')
                            print(f"Completed: {counts:,} records are written into JSON file ({t})")  

                        savemongo = SaveMongo()
                        savemongo.insert_daily_efts(res[1], res[1]['holding_date'])
                        print(f"Updated: {counts:,} records are updated to MongoDB ({t})")   
                        
                    except Exception as e:
                        print(e)   

            elif flag in ["Done today"]:
                t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')
                print(f"Today's job has been completed, please check... ({t})")  

            else:
                t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')
                print(f"The data on the website has not been updated yet, please wait... ({t})")
                
        else:
             t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')
             print(f"Sorry, today is not trading day. ({t})")       


# Schedule job
def main():     
    sched = BlockingScheduler() 
    sched.configure(timezone="Asia/Taipei")
    scrapingetfs = ScrapingEtf()
    sched.add_job(scrapingetfs.processes, 'cron', minute='0/10',hour='18-20') 
     
    try:        
        sched.start()      
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()
        sys.exit(0)
    except Exception as e:
        print(e)
    

    
if __name__ == "__main__":    
    main()        