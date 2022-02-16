from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
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
    # def init_workqueue_from_excel(self,
    #                             PATH,
    #                             url_index,
    #                             condition_index,
    #                             condition_value = 'False Positive',
    #                             sheet_name='checkmarx'):
    #     wb_obj = openpyxl.load_workbook(PATH)
    #     sheet = wb_obj[sheet_name]
    #     for i in range(2,len(sheet['A'])):
    #         if sheet[condition_index+str(i)].value == condition_value:
    #             self.workqueue.append({'id':i,'url':sheet[url_index+str(i)].value,'isSet':False})
    #     save_dic_as_json(self.workqueue,self.cache_path)
    #     return self
    
    #New Method
    def init_workqueue_from_excel(self,
                                    PATH,
                                    url_index,
                                    comment_index,
                                    status_index,
                                    sheet_name='checkmarx'):
        wb_obj = openpyxl.load_workbook(PATH)
        sheet = wb_obj[sheet_name]
        for i in range(2,len(sheet['A'])):
            self.workqueue.append({'id':i,
                                    'url':sheet[url_index+str(i)].value,
                                    'status':sheet[status_index+str(i)].value,
                                    'comment':sheet[comment_index+str(i)].value,
                                    'isSet':False})
        save_dic_as_json(self.workqueue,self.cache_path)

    def load_workqueue_from_json(self):
        self.workqueue = init_dic_from_json(self.cache_path)

    def sso_login(self,target_url):
        try:
            self.driver.get(target_url)
            # wait = WebDriverWait(self.driver, 10)
            # sso_login_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH,"//button[text()='Azure']")))
            
            sso_login_btn = self.wait.until(EC.element_to_be_clickable((By.NAME,'providerid')))
            self.driver.execute_script("document.body.style.zoom='1'") #Adjust zoom into 100% or click() won't work
            # print('Login button clicked',sso_login_btn.get_attribute("outerHTML"))
            sso_login_btn.click()
            
            # time.sleep(4)
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

    # def set_status(self,url,status):
    #     self.driver.get(url)
    #     time.sleep(5)
    #     try:
    #         iframe = self.wait.until(EC.presence_of_element_located((By.ID,"gridFrame")))
    #         self.driver.execute_script("document.body.style.zoom='1'") #Adjust zoom into 100% or click() won't work
    #         self.driver.switch_to.frame(iframe)
    #         checkbox = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'tr.rgSelectedRow > td:first-child > span > input')))
    #         checkbox.click()
    #         menu = self.driver.find_element_by_css_selector('a.rtbExpandDown')
    #         menu.click()
    #         not_exploitable_item = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'ul.rtbActive > li:nth-child(2) > a')))
    #         not_exploitable_item.click()
    #         time.sleep(4)
    #         cprint(f'Set as {status} successfully','WEB')
    #         return True
    #     except:
    #         traceback.print_exc()
    #         cprint(f'Set as {status} failed','WEB')
    #         return False

    #New Method
    def set_status(self,workqueue_unit):
        if not workqueue_unit.comment:
            return False
        else:
            self.driver.get(workqueue_unit.url)
            time.sleep(5)
            try:
                #Set as Not exploitable
                if workqueue_unit.status == 'False Positive':
                    iframe = self.wait.until(EC.presence_of_element_located((By.ID,"gridFrame")))
                    self.driver.execute_script("document.body.style.zoom='1'") #Adjust zoom into 100% or click() won't work
                    self.driver.switch_to.frame(iframe)
                    checkbox = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'tr.rgSelectedRow > td:first-child > span > input')))
                    checkbox.click()
                    menu = self.driver.find_element_by_css_selector('a.rtbExpandDown')
                    menu.click()
                    not_exploitable_item = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'ul.rtbActive > li:nth-child(2) > a')))
                    not_exploitable_item.click()
                    time.sleep(4)
                elif workqueue_unit.status == 'Open':
                    iframe = self.wait.until(EC.presence_of_element_located((By.ID,"gridFrame")))
                    self.driver.execute_script("document.body.style.zoom='1'") #Adjust zoom into 100% or click() won't work
                    self.driver.switch_to.frame(iframe)
                    checkbox = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'tr.rgSelectedRow > td:first-child > span > input')))
                    checkbox.click()
                    menu = self.driver.find_element_by_css_selector('a.rtbExpandDown')
                    menu.click()
                    not_exploitable_item = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'ul.rtbActive > li:nth-child(3) > a')))
                    not_exploitable_item.click()
                    time.sleep(4)
                elif  workqueue_unit.status == 'Pending':
                    pass
                else:
                    cprint('Unknown status, must be "False Positive","Open" or "Pending')
                    raise
                #Input comment into checkmarx
                iframe = self.wait.until(EC.presence_of_element_located((By.ID,"gridFrame")))
                self.driver.execute_script("document.body.style.zoom='1'") #Adjust zoom into 100% or click() won't work
                self.driver.switch_to.frame(iframe)
                img = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'tr.rgSelectedRow > td:last-child > div > img')))
                img.click()
                textarea = self.wait.until(EC.presence_of_element_located((By.NAME,'wndCmmt_C_txtCmmt')))
                textarea.sendKeys(workqueue_unit.comment)

                btn = self.wait.until(EC.presence_of_all_elements_located((By.ID,'wndCmmt_C_btnCancel_input')))
                # btn = self.wait.until(EC.presence_of_all_elements_located((By.ID,'wndCmmt_C_btnSave_input')))
                btn.click()
                time.sleep(1)
            except:
                traceback.print_exc()
                cprint(f'Set as {workqueue_unit.status} failed','WEB')
                return False

            
    #New Method
    def exec_workqueue(self,change_to='Not Exploitable'):
        try:
            if self.sso_login(self.workqueue[0]['url']):
                for i in range(0,len(self.workqueue)):
                    if not self.workqueue[i]['isSet']:
                        print('Checking ',i+1 ,'/', len(self.workqueue))
                        if self.set_status_and_comment(self.workqueue[i]):
                            self.workqueue[i]['isSet'] = True
                            save_dic_as_json(self.workqueue,self.cache_path)
            else:
                self.driver.quit()

        except:
            traceback.print_exc()
            self.driver.quit()
            # self.exec_workqueue(change_to)


    # def exec_full_workqueue(self):
    #     try:
    #         if self.sso_login(self.workqueue[0]['url']):
    #             for i in range(0,len(self.workqueue)):
    #                 if not self.workqueue[i]['isSet']:
    #                     print('Checking ',i+1 ,'/', len(self.workqueue))
    #                     if self.set_status(self.workqueue[i]['url'],change_to):
    #                         self.workqueue[i]['isSet'] = True
    #                         save_dic_as_json(self.workqueue,self.cache_path)
    #         else:
    #             self.driver.quit()

        except:
            traceback.print_exc()
            self.driver.quit()

    def logout(self):
        self.driver.close()
    def __del__(self):
        self.driver.quit()