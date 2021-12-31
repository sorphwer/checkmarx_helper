from web import CheckmarxDriver

#Init a driver, and name a json file path where you want to save your work queue.
driver = CheckmarxDriver('riino').set_workqueue_cache_path('commercial-wccs-url-list.json')
# Assume you have an excel where col for urls is 'AC' and col for status is 'AB', you want to access url one by one, 
# and set the status in checkmarx into the status in col 'AB' where the status is 'False Positive' :
# driver.init_workqueue_from_excel('APAC-Commercial-WCCS#APAC-Commercial-WCCS-Web_v1.0_20211222.xlsx','AC','AB','False Positive')
#If you quit the program, you can load the workqueue from json file directly using the method below: 
driver.load_workqueue_from_json()

#After init/load workqueue, you can use `exec_workqueue` to run the work queue. 


driver.exec_workqueue(change_to='Not Exploitable')