import json
import time
from collections import defaultdict
import openpyxl
import traceback
def init_dic_from_json(PATH):
    try:
        with open(PATH,'r') as r:
            dic = json.load(r)
        cprint('cache json file is loaded','COMMON',str(PATH))
        return dic
    except:
        traceback.print_exc()
        cprint('load file failed','COMMON',str(PATH))
        return False

def save_dic_as_json(dic,PATH,indent=4):
    try:
        with open(PATH,'w') as w:
            w.write(json.dumps(dic,indent=indent,default=str))
        cprint('cache json file is saved','JSON',str(PATH))
        return True
    except:
        traceback.print_exc()
        cprint('save file failed','JSON',str(PATH))
        return False

def cprint(content,module='DEBUG',*args):
    if args:
        print('\033[1;32;43m ['+module+'] \033[0m '+ content + '\033[1;35m' +str(args) +' \033[0m' + time.strftime(" |%Y-%m-%d %H:%M:%S|", time.localtime()) )
    else:
        print('\033[1;32;43m ['+module+'] \033[0m '+ content + time.strftime(" |%Y-%m-%d %H:%M:%S|", time.localtime()))

'''
INPUT:
    xxx.Web/xxx/xxx.Com/aaa.cs
OUTPUT:
    raw/aaa.cs
'''
def get_file_name(path):
    if path:
        return 'raw/'+str(path.split('/')[-1])
    else:
        raise ValueError('path is None')
        return -1

def get_file_name(path):
        if path:
            return 'raw/'+str(path.split('/')[-1])
        else:
            raise ValueError('path is None')
            return -1
class DBBuilder():

    db = defaultdict(dict)
    project_name = ''

    def __init__(self,project_name):
        self.project_name = project_name


    '''
    INPUT:
        {'#': 1, 
        'Query': 'Dynamic SQL Queries', 
        'SrcFileName': 'xxx.Web/xxx/pfc/PageBaseLanguage.cs', 
        'Line': 973, 
        'Column': 171, 
        'NodeId': 1, 
        'Name': 'BinaryExpr',
        'DestFileName': 'xxx.Web/xxx/pfc/Manage.cs', 
        'DestLine': 5845, 
        'DestColumn': 35, 
        'DestNodeId': 7, 
        'DestName': 'ExecuteScalar', 
        'Result State': 'To Verify', 
        'Result Severity': 'High', 
        'Status': None, 
        'Link': 'https://example.checkmarx.net/CxWebClient/ViewerMain.aspx?scanid=148&projectid=1&pathid=2', 
        'Result Status': 'Reoccured', 
        'Detection Date': None, 
        'Comment': None, 
        'Manul Verification': None, 
        'Fix Evidence': None,
        'SrcFilePath':'raw/PageBaseLanguage.cs',
        'DestFilePath':'raw/Manage.cs'}
    '''
    def _update_db(self,row):
        
        context = {
                **row,
                'SrcCode' : [row['Line'],self._get_code_line(row)],
                'DestCode': [row['DestLine'],self._get_code_line(row)]
        }
        if row['SrcFileName'] in self.db:
            self.db[row['SrcFileName']]['list'].append(context)
        else:
            self.db[row['SrcFileName']]['list'] = []
            self.db[row['SrcFileName']]['list'].append(context)
        return row
    
    '''
    Return n-th line of a file
    '''
    def _get_code_line(self,row):
        path = row['SrcFilePath']
        N = row['Line']
        try:
            with open(path,mode='r',encoding='UTF-8') as f:
                head = [next(f) for x in range(N)]
            return head[-1].strip().replace('\n','')
        except:
            return row['Link']

    def _split_chunks(self,db_key):
        def _init_link(L):
            #connect records with same code
            mapping = {} #mapping = {hash:[id]}
            for i in range(0,len(L)):
                try:
                    hash = str(L[i]['Line']) + str(L[i]['DestLine'])
                    id = L[i]['#']
                except:
                    print('KeyError in ',i)
                    print(L)
                if not hash in mapping:
                    mapping[hash] = [id]
                else:
                    L[i]['reference'] = mapping[hash][0]
                    L[i]['Comment'] = 'As the code triggers this issue and the remediation is the same, please refer to #'+str(id)
                    mapping[hash].append(id)
            return L
        chunks = defaultdict(dict)
        for i in self.db[db_key]['list']:
            if i['DestFileName'] in chunks:
                chunks[i['DestFileName']].append(i)
            else:
                chunks[i['DestFileName']] = []
                chunks[i['DestFileName']].append(i)
        for key in list(chunks.keys()):
            chunks[key] = _init_link(chunks[key])
        self.db[db_key] = chunks


    def init_from_json(self,PATH = ''):
        if PATH:
            self.db = init_dic_from_json(PATH)
        else:
            self.db = init_dic_from_json(self.project_name+'.json')
        return self
    
    def init_from_excel(self,
                        PATH,
                        sheet_name = 'checkmarx',
                        index_col = 'B',
                        col_list = ['B','C','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB','AC','AD','AE','AF','AG','AH']
                        ):
        wb_obj = openpyxl.load_workbook(PATH)
        sheet = wb_obj[sheet_name]
        #First init
        for i in range(2,len(sheet['A'])):
            #Init ID
            sheet[index_col+str(i)].value = i-1

            #init Row
            row = {}
            for header_index in col_list:
                row[sheet[header_index+'1'].value] = sheet[header_index+str(i)].value
            row['SrcFilePath'] = get_file_name(row['SrcFileName'])
            row['DestFilePath'] = get_file_name(row['DestFileName'])
            #first init
            self._update_db(row)
       
        #Second init
        for db_key in list(self.db.keys()):
            self._split_chunks(db_key)
        #Save excel
        wb_obj.save(PATH)
        #Save json
        save_dic_as_json(self.db,self.project_name+'.json')
        return self

    def get_db(self)->dict:
        if self.db:
            return self.db
        else:
            print("Please use 'init_from_excel' or 'init_from_json' to init db")
    def get_project_name(self)->str:
        return self.project_name
    def __del__(self):
        save_dic_as_json(self.db,self.project_name+'.json')