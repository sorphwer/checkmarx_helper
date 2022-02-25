from pyparsing import countedArray
from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback  
import time
import openpyxl
from common import cprint , init_dic_from_json,save_dic_as_json
class CheckmarxDriver():
    workqueue = []
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
        self.wait = WebDriverWait(self.driver, 15)
        if mode == 'Full-Screen':
            self.driver.maximize_window()

    def set_workqueue_cache_path(self,path='Checkmarx_web_workqueue.json'):
        self.cache_path = path
        return self

    def init_workqueue_from_excel(self,
                                    PATH,
                                    url_index = 'AC',
                                    comment_index = 'AF',
                                    status_index = 'AB',
                                    id_index = 'B',
                                    result_state = 'Z',
                                    sheet_name ='checkmarx'):
        wb_obj = openpyxl.load_workbook(PATH)
        sheet = wb_obj[sheet_name]
        counter = 0
        for i in range(2,len(sheet['A'])):
            if sheet[result_state+str(i)].value == 'To Verify':
                self.workqueue.append({'index':counter,
                                        'id':sheet[id_index+str(i)].value,
                                        'url':sheet[url_index+str(i)].value,
                                        'status':sheet[status_index+str(i)].value,
                                        'comment':sheet[comment_index+str(i)].value,
                                        'isSet':False,
                                        'isCommentSet':False})
                counter += 1
        save_dic_as_json(self.workqueue,self.cache_path)

    def load_workqueue_from_json(self):
        self.workqueue = init_dic_from_json(self.cache_path)

    def sso_login(self,target_url):
        try:
            self.driver.get(target_url)

            sso_login_btn = self.wait.until(EC.element_to_be_clickable((By.NAME,'providerid')))
            self.driver.execute_script("document.body.style.zoom='1'") #Adjust zoom into 100% or click() won't work

            sso_login_btn.click()

            iframe = self.wait.until(EC.presence_of_element_located((By.ID,"codeFrame")))
            if iframe:
                cprint('Login successfully','WEB')
                return True
            else:
                return False
        except:
            traceback.print_exc()
            cprint('Login failed','WEB')
            return False
    def exec_get_code_html(self,url):
        try:
            if self.sso_login(url):
                iframe = self.wait.until(EC.presence_of_element_located((By.ID,"codeFrame")))
                self.driver.switch_to.frame(iframe)

                code_div = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.CodeMirror-lines > div >div.CodeMirror-code')))

                return code_div

        except:
            traceback.print_exc()

    def set_status(self,workqueue_unit):
        cprint('Executing:','WEB')
        print(workqueue_unit)
        if not workqueue_unit['comment']:
            return False
        else:
            self.driver.get(workqueue_unit['url'])
            time.sleep(2)
            try:
                iframe = self.wait.until(EC.presence_of_element_located((By.ID,"gridFrame")))
                self.driver.execute_script("document.body.style.zoom='1'") #Adjust zoom into 100% or click() won't work
                self.driver.switch_to.frame(iframe)

                # checkbox = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'tr.rgSelectedRow > td:first-child > span > input')))
                # checkbox.click()
                # time.sleep(1)
                # menu = self.driver.find_element_by_css_selector('a.rtbExpandDown')
                # menu.click()
                # time.sleep(1)
                # if workqueue_unit['status'] == 'False Positive':
                #     cprint('Set as Not exploitable','WEB')
                #     not_exploitable_item = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'ul.rtbActive > li:nth-child(2) > a')))
                #     not_exploitable_item.click()
                #     print(not_exploitable_item.get_attribute('innerHTML'))
                # elif workqueue_unit['status'] == 'Open':
                    
                #     confirmed_item = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'ul.rtbActive > li:nth-child(3) > a')))
                #     confirmed_item.click()
                #     print(confirmed_item.get_attribute('innerHTML'))
                #     cprint('Set as Confirmed done','WEB')
                # elif  workqueue_unit['status'] == 'Pending Further Information':
                #     pass
                # else:
                #     cprint('Unknown status, must be "False Positive","Open" or "Pending')
                #     raise
                # time.sleep(4)



                img = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'tr.rgSelectedRow > td:last-child > div > img')))
                img.click()
                comment = workqueue_unit['comment'].replace('"',"'")
                js = 'let ta = document.getElementById("wndCmmt_C_txtCmmt");ta.value = "'+comment +'"'
                time.sleep(3)
                self.driver.execute_script(js)
                time.sleep(2)
                btn = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'span#wndCmmt_C_btnSave')))
                btn[0].click()
                time.sleep(1)
                return True

            except:
                traceback.print_exc()
                cprint(f'Operation failed','WEB')
                return False

            
    #New Method
    def exec_workqueue(self):
        try:
            if self.sso_login(self.workqueue[0]['url']):
                for i in range(0,len(self.workqueue)):
                    if not self.workqueue[i]['isCommentSet']:
                        print('Checking ',i+1 ,'/', len(self.workqueue))
                        if self.set_status(self.workqueue[i]):
                            self.workqueue[i]['isCommentSet'] = True
                            save_dic_as_json(self.workqueue,self.cache_path)
            else:
                self.driver.quit()

        except:
            traceback.print_exc()
            self.driver.quit()
            # self.exec_workqueue(change_to)
    def print_workqueue(self):
        try:
            print(self.workqueue)
            return True
        except:
            return False

    def logout(self):
        self.driver.close()
    def __del__(self):
        self.driver.quit()