# rpa_scrap_etf.py
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
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
                "holding_percentage": match[2],
                "holding_amount": match[3].replace(",", ""),  
                "unit": match[4]
            })
        return result
    
    # Read csv-file for trading days 
    def get_trade_days_list(self):        
        file_path = os.path.join(self.pwd, self.folder_in, self.file_in_trade_day)
        df = pd.read_csv(file_path)
        df.trade_day = df.trade_day.apply(lambda x: x.replace("-","/"))
        trade_days = list(df.trade_day)
        return trade_days
    
    # Check if data updates
    def chk_ds_update_(self, variables):                
        date_list = []
        output_path = os.path.join(self.pwd, self.folder_out, self.file_out_etfs)      
        if os.path.isfile(output_path):        
            with open(output_path, mode='r') as f:
                data = json.load(f)
                date_list = list(data.keys())

        if self.today not in date_list:        
            r.init(headless_mode=True)  
            r.url(variables['pocket_url'])
            r.wait(1)    
            etfs_num = len(self.etfs) 
            update_num = 0   
            for etf in self.etfs:                                            
                r.type(variables['type_code'], etf)
                r.click(variables['click_code'])
                r.wait(0.5)
                r.click(variables['click_option'])
                r.wait(1)
                r.click(variables['click_holding'])
                r.wait(1)    
                holding_date = r.dom(variables['dom_date']).strip()[5:]                               
                print("--->", etf, "(web_update_date: " + holding_date + ")")
                if holding_date == self.today:                    
                    # print("--->", etf, "(" + holding_date + ")")
                    update_num = update_num + 1                    
                r.wait(random.randint(2,6))  
            r.close()    
            if update_num == etfs_num:
                return "All updated"
            else:
                return "Not updated"
        else:
            return "Done today"   
    
    # Operate website and get data         
    def get_ds_from_url(self, variables): 
        # r.init()  
        r.init(headless_mode=True)    
        r.url(variables['pocket_url'])
        r.wait(1)
        ds_list = []    
        for etf in self.etfs:         
            daily_ds = dict()                              
            r.type(variables['type_code'], etf)
            r.click(variables['click_code'])
            r.wait(0.5)
            r.click(variables['click_option'])
            r.wait(1)
            r.click(variables['click_holding'])
            r.wait(3)   
            etf_name = r.dom(variables['dom_etf_name']).replace("\n", "") 
            etf_name = etf_name[0:etf_name.find("<span>")].strip()                           
            print("--->", etf, etf_name, "(parsing html...)")      
            holding_date = r.dom(variables['dom_date']).strip()[5:]
            r.wait(1)
            t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')    
            html_str = r.dom(variables['dom_tb'])
            r.wait(1)        
            parsed_data = self.parse_html_tb(html_str) 

            # Prevent from getting uncompleted data
            if parsed_data==[] or len(parsed_data)<25:                
                r.click(variables['click_holding'])
                r.wait() 
                parsed_data = self.parse_html_tb(html_str)

            daily_ds['etf_code'] = etf        
            daily_ds['etf_name'] = etf_name        
            daily_ds['scraping_time'] = t 
            daily_ds['etf_holding'] = parsed_data
            ds_list.append(daily_ds)
            r.wait(random.randint(2,6))     

        r.close()    
        return [holding_date, ds_list]
    
    # Workflow with conditions
    def processes(self):
        trade_list = self.get_trade_days_list()
        if self.today in trade_list:            
            file_path = os.path.join(self.pwd, self.folder_in, self.file_in_parameters)
            variables = self.read_json_to_dict(file_path) 
            flag = self.chk_ds_update_(variables)              
            if flag in ['All updated']: 
                t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')
                print("Start job...({})".format(t))    
                res = self.get_ds_from_url(variables)
                daily_ds = dict()  
                daily_ds[res[0]] = res[1]                
                output_path = os.path.join(self.pwd, self.folder_out, self.file_out_etfs)                
                if os.path.isfile(output_path):        
                    with open(output_path, mode='r') as f:
                        data = json.load(f)        
                    data.update(daily_ds)
                    with open(output_path, 'w', encoding='utf-8') as fp:
                        json.dump(data, fp, ensure_ascii=False, indent=4)
                else:        
                    with open(output_path, 'w', encoding='utf-8') as fp:
                        json.dump(daily_ds, fp, ensure_ascii=False, indent=4)  
            elif flag in ["Done today"]:
                t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')
                print("It's already done, please check...({})".format(t))              
            else:
                t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')
                print("Not updated, please wait...({})".format(t))
        else:
             t = dt.datetime.strftime(dt.datetime.now(),'%Y-%m-%d %H:%M:%S')
             print("Today is not trading day...({})".format(t))       


# Schedule job
def main(): 
    sched = BlockingScheduler() 
    scrapingetfs = ScrapingEtf()
    sched.add_job(func=scrapingetfs.processes,
                  trigger=CronTrigger.from_crontab('0/10 18-20 * * *'),
                  next_run_time=dt.datetime.now())       
    try:
        sched.start()    
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()
        sys.exit(0)
    except Exception as e:
        print(e)
    

    
if __name__ == "__main__":    
    main()         


# clear & python rpa_scrap_etf.py