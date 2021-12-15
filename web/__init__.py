from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback  
import time
import openpyxl
from common import cprint , init_dic_from_json,save_dic_as_json
class CheckmarxDriver():
    workqueue = {}
    def __init__(self,
                system_user:str,
                chrome_driver_path:str = "chromedriver.exe",
                mode = 'Full-Screen'
                ):
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir=C:\\Users\\{system_user}\\AppData\\Local\\Google\\Chrome\\User Data")
        options.add_experimental_option("excludeSwitches",["ignore-certificate-errors"])
        if mode == 'headless':
            options.add_argument('--headless')

        self.driver = webdriver.Chrome(executable_path=chrome_driver_path,options=options)
        self.wait = WebDriverWait(self.driver, 10)
        if mode == 'Full-Screen':
            self.driver.maximize_window()
    def set_workqueue_cache_path(self,path='Checkmarx_web_workqueue.json'):
        self.cache_path = path
    def init_workqueue_from_excel(self,
                                PATH,
                                url_index,
                                condition_index,
                                condition_value = 'False Positive',
                                sheet_name='checkmarx'):
        wb_obj = openpyxl.load_workbook(PATH)
        sheet = wb_obj[sheet_name]
        self.workqueue = {}
        for i in range(2,len(sheet['A'])):
            if sheet[condition_index+str(i)].value == condition_value:
                self.workqueue.append({'id':i,'url':sheet[url_index+str(i)].value,'isSet':False})
        save_dic_as_json(self.workqueue,self.cache_path)

    def load_workqueue_from_json(self):
        self.workqueue = init_dic_from_json(self.cache_path)

    def sso_login(self,target_url):
        try:
            self.driver.get(target_url)
            wait = WebDriverWait(self.driver, 10)
            sso_login_btn = wait.until(EC.element_to_be_clickable((By.NAME,'providerid')))
            sso_login_btn.click()
            time.sleep(10)
            cprint('Login successfully','WEB')
            return True
        except:
            traceback.print_exc()
            cprint('Login failed','WEB')
            return False


    def set_status(self,status):
        try:
            iframe = self.wait.until(EC.presence_of_element_located((By.ID,"gridFrame")))
            
            self.driver.switch_to.frame(iframe)

            checkbox = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'tr.rgSelectedRow > td:first-child > span > input')))
            checkbox.click()
            time.sleep(1)

            menu = self.driver.find_element_by_css_selector('a.rtbExpandDown')
            menu.click()
            time.sleep(0.5)
            not_exploitable_item = self.driver.find_element_by_xpath(f"//span[text()='{status}']/..")
            not_exploitable_item.click()
            time.sleep(5)
            cprint(f'Set as {status} successfully','WEB')
            return True
        except:
            traceback.print_exc()
            cprint(f'Set as {status} failed','WEB')
            return False
    def exec_workqueue(self,change_to='Not Exploitable'):
        try:
            if self.sso_login(self.workqueue[0]['url']):
                for i in range(0,len(self.workqueue)):
                    if not self.workqueue[i]['isSet']:
                        print('Checking ',i ,'/', len(self.workqueue))
                        if self.set_status(self.workqueue[i]['url'],change_to):
                            self.workqueue[i]['isSet'] = True
                            save_dic_as_json(self.workqueue,self.cache_path)

        except:
            print(traceback)
            print('Got Error, it might be that the memory is running out')
            self.driver.close()
    def logout(self):
        self.driver.close()
    def __del__(self):
        self.driver.quit()