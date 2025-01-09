# save_db.py
import pymongo
import time
import datetime as dt


class SaveMongo:
    
    # Variables for functions as below
    def __init__(self):                               
        self.host = 'your_host' 
        self.port = 'your_port'
        self.username= 'your_username'
        self.password= 'your_password'
        self.db_name = 'financedb'
        self.tb_name = 'top_etfs'
            
    # Get connection to mongodb
    def get_mongo_connection(self):
        try:
            m_client = pymongo.MongoClient(host = self.host,
                                           port = self.port,  
                                           username = self.username,
                                           password = self.password)
        except Exception as e:
            print(e)  
        return m_client

    # Insert data
    def insert_daily_efts(self, daily_etfs, holding_date):
        try:
            m_client = self.get_mongo_connection()
            m_db = m_client["financedb"]
            m_col = m_db["top_etfs"]
            if len(list(m_col.find({"holding_date": holding_date}))) !=0:
                m_col.delete_many({"holding_date": holding_date})
                time.sleep(1)
                m_col.insert_many([daily_etfs])                           
            else:
                m_col.insert_many([daily_etfs])            
            print("Successfully updated. Please check...")    
        except Exception as e:
            print(e)  

    # Query etf data with date   
    def show_eft_data_with_date(self, holding_date):
        try:
            m_client = self.get_mongo_connection()
            m_db = m_client["financedb"]
            m_col = m_db["top_etfs"]
            m_doc = m_col.find({"holding_date": holding_date})                        
            return m_doc
        except Exception as e:
            print(e) 


def main():
    try:
        savemongo = SaveMongo()
        now_date = dt.datetime.today().strftime('%Y/%m/%d')    
        etf_data = savemongo.show_eft_data_with_date(now_date)
        for doc in etf_data:
            print(doc)                                      
        print("Query 'holding_date':", now_date) 
    except Exception as e:
            print(e)    


    
if __name__ == "__main__":    
    main()                 
      