
import traceback
import cmd
import json
import os
from IPython import get_ipython
from common import DBBuilder,cprint,cstr
import openpyxl

'''
Usage 1: WorkShell(db:dictionary,PATH:string)
Usage 2: WorkShell(builder:DBBuilder)
'''
class WorkShell(cmd.Cmd):
    # db -> node - > chunks -> <list>
    # db = { SrcFile: node }
    # node =  { chunks }
    # chunks = { DestFile : <list> }
    # <list> = [row]
    _current_node_index = 0
    _current_chunk_index = 0
    
    db = {}
    db_index_list = []
    CACHE_PATH = ''
    is_notebook = False
    

    def __init__(self, project_name:str=None,builder:DBBuilder=None):
        super(WorkShell, self).__init__()
        if project_name:
            self.init_from_project_name(project_name)
        if builder:
            self.init_from_builder(builder)
    def init_from_project_name(self,project_name:str):
        self.CACHE_PATH = project_name+'.json'
        try:
            with open(self.CACHE_PATH,'r') as r:
                self.db = json.load(r)
            self.db_index_list = list(self.db.keys())
            self.is_notebook = self.is_notebook()
            if self.is_notebook:
                cprint('Welcome to Shell, you are using Jupyter notebook','SHELL')
            else:
                cprint('Welcome to Shell, you are using None Jupyter notebook','SHELL')
        except:
            cprint('Load project json file failed','SHELL',project_name)
    def init_from_builder(self,builder:DBBuilder):
        self.CACHE_PATH = builder.get_project_name()+'.json'
        self.db = builder.get_db()
        self.db_index_list = list(self.db.keys())
        self.is_notebook = self.is_notebook()
        if self.is_notebook:
            cprint('Welcome to Shell, you are using Jupyter notebook','SHELL')
        else:
            cprint('Welcome to Shell, you are using None Jupyter notebook','SHELL')

    def is_notebook(self):
        try:
            shell = get_ipython().__class__.__name__
            if shell == 'ZMQInteractiveShell':
                return True   # Jupyter notebook or qtconsole
            elif shell == 'TerminalInteractiveShell':
                return False  # Terminal running IPython
            else:
                return False  # Other type (?)
        except NameError:
            return False      # Probably standard Python interpreter

    def check_str(s):
        if s == None:
            return ""
    
    def _clear_console(self):
        if self.is_notebook:
            from IPython.display import clear_output
            clear_output()#for ipynb
        else:
            os.system('cls')#for windows console

    def _get_code_line(self,id,N):
        current_chunk = self._get_current_chunk()
        try:
            for i in current_chunk:
                if i['#'] == id:
                    path = i['SrcFilePath']
                    with open(path,mode='r',encoding='UTF-8') as f:
                        head = [next(f) for x in range(i['Line']+N)]
                    for i in range(i['Line'],i['Line']+N):
                        print(head[i].strip().replace('\n',''))
            return 0
        except:
            print('Out of file length')
            traceback.print_exc()
            return 1
                              

    def _get_current_node(self):
        return self.db[self.db_index_list[self._current_node_index]]
    def _get_current_chunk(self):
        return self._get_current_node()[list(self._get_current_node().keys())[self._current_chunk_index]]
        
    def _set_current_node(self,node):
        self.db[self.db_index_list[self._current_node_index]] = node
        return self._get_current_node()

    def _set_reference(self,id,target_id):
        if id == target_id:
            print("Cannot set self reference")
            return False
        current_chunk = self._get_current_chunk()
        comment = ""
        status = ""
        for i in current_chunk:
            if i['#'] == target_id:
                comment = i['Comment']
                status = i['Status']
        for i in current_chunk:
            if i['#'] == id:
                i['Comment'] = comment
                i['Status'] = status
                i['reference'] = int(target_id)
        return True
                
    def _detach_reference(self,id):
        current_chunk = self._get_current_chunk()
        for i in current_chunk:
            if i['#'] == id:
                i['Comment'] = None
                i['Status'] = None
                del i['reference']

    def _set_open_comment(self,id,comment):
        current_chunk = self._get_current_chunk()
        for i in current_chunk:
            if i['#'] == id:
                i['Comment'] = comment
                i['Status'] = 'Open'
                
    def _set_fp_comment(self,id,comment):
        current_chunk = self._get_current_chunk()
        for i in current_chunk:
            if i['#'] == id:
                i['Comment'] = comment
                i['Status'] = 'False Positive'
                
                
    def _set_pending_comment(self,id,comment):
        current_chunk = self._get_current_chunk()
        for i in current_chunk:
            if i['#'] == id:
                i['Comment'] = comment
                i['Status'] = 'Pending'
    def _add_comment(self,id,comment):
        current_chunk = self._get_current_chunk()
        for i in current_chunk:
            if i['#'] == id:
                i['Comment'] += comment
                
    def _remove_comment(self,id):
        current_chunk = self._get_current_chunk()
        for i in current_chunk:
            if i['#'] == id:
                i['Comment'] = ''
                i['Status'] = ''


    def _set_comment_template(self,id,type,filename = 'Src', line = None):
        current_chunk = self._get_current_chunk()
        for i in current_chunk:
            if i['#'] == id:
                if filename == 'Dest':
                    filename = i['DestFileName']
                else:
                    filename = i['SrcFileName']
                if not line:
                    line = i['Line']
         
            
        if type.lower() == 'fp5':
            for i in current_chunk:
                if i['#'] == id:
                    i['Comment'] = 'There is no logical relationship between the data flow provided by Checkmarx.'
                    i['Status'] = 'False Positive'
        elif type.lower() == 'fp1':
            for i in current_chunk:
                if i['#'] == id:
                    i['Comment'] = f'The global filterring method has been used , or there are other filtering methods, but it is not recognized by checkmarx'
                    i['Status'] = 'False Positive'
        elif type.lower() == 'fp2':
            for i in current_chunk:
                if i['#'] == id:
                    i['Comment'] = 'The input has been restricted on characters, such as length, character type, etc., but it is not recognized by checkmarx.'
                    i['Status'] = 'False Positive'
        elif type.lower() == 'fp3':
            for i in current_chunk:
                if i['#'] == id:
                    i['Comment'] = 'The input comes from a trusted source, such as constants or variables that are not input by the user, but it is not recognized by checkmarx.'
                    i['Status'] = 'False Positive'
        elif type.lower() == 'fp4':
            for i in current_chunk:
                if i['#'] == id:
                    i['Comment'] = 'The output will not cause vulnerabilities, but the tool misreports the vulnerabilities.'
                    i['Status'] = 'False Positive'
        elif type.lower() == 'fp6':
            for i in current_chunk:
                if i['#'] == id:
                    i['Comment'] = 'The judgment of other tools is wrong.'
                    i['Status'] = 'False Positive'

        elif type.lower() =='sqlformat':
            for i in current_chunk:
                if i['#'] == id:
#                     i['Comment'] = f"The application uses 'String.format' to embed untrusted params and construct sql queries, and executes queries in the function '{ExecuteScalar}' at line {508} of {Unisoft.Library/Unisoft.Net.Common/Helper/SQLHelper.cs}, which may cause sql injection attacks. Moreover, we observed that each time before executing queries, '{ExecuteScalar}' will call the function '{PrepareCommand}' at line 842 of Unisoft.Library/Unisoft.Net.Common/Helper/SQLHelper.cs to prepare sql query strings. We recommend to add sql injection prevention methods into the function '{PrepareCommand}' such as Prepared Statement, Input Validation Check, Sanitization, instead of string concatenation. "
                    i['Status'] = 'Open'
                    i['Comment'] = f"The application uses 'String.format' to embed untrusted params and construct sql queries at line {line} of {filename}, which may cause sql injection attacks."
        elif type.lower() == "sql+":
            for i in current_chunk:
                if i['#'] == id:
                    i['Status'] = 'Open'
                    i['Comment'] = f"The application uses string concatenation to embed untrusted params and construct sql queries at line {line} of {filename}, which may cause sql injection attacks."
        elif type.lower() == "pending":
            for i in current_chunk:
                if i['#'] == id:
                    i['Status'] = 'Pending Further Information'
                    i['Comment'] = f"Through the code snippet provided by Checkmarx, we know that the application deserializes  an object which is a FileStream read from a file at line {line} of {filename}. However, we are not aware that whether the file is user controlled, thus we could not consider the status of the vulnerability to be Open."
                    
        
    #edit interface
    def _edit_current_chunk(self):
        cprint('Node ' +str(self._current_node_index+1) +'/'+str(len(self.db)),'SHELL')
        cprint('Chunk '+str(self._current_chunk_index+1)+'/'+str(len(self.db[self.db_index_list[ self._current_node_index]])),'SHELL')
        current_chunk = self._get_current_chunk()
        #Print basic info of this chunk
        print(current_chunk[0]["SrcFileName"],'--->',current_chunk[0]["DestFileName"])
        #interface_dic : {key:[linked_key,code],key:[linked_key,code]}
        interface_dic = {}
#         print(current_chunk)
        for i in current_chunk:
            if 'reference' in i:
                interface_dic[int(i['reference'])][0] += ( '-' + cstr(i['#']))
            else:
                interface_dic[int(i['#'])] = [cstr(i['#']),"["+cstr(i['Line'])+"]"+cstr(i['SrcCode'][1]), "["+cstr(i['DestLine'])+"]"+cstr(i['DestCode'][1])]

                
#         for key in interface_dic.keys():
        for i in current_chunk:
            if 'reference' in i:
                pass
            else:
                if not i['Comment']:
                    i['Comment'] = ''
                if i['Status'] == 'Open':
                    print("\033[32;1m [Open]",end='')
                    print('\033[1;32;43m'+interface_dic[i['#']][0]+'\033[0m',end='')
                    print("\033[32;1m"+i['Comment']+'\033[0m')
            
                    print(interface_dic[i['#']][1])
                    print(interface_dic[i['#']][2])
                elif i['Status'] == 'False Positive':
                    print("\033[33;1m [FP]",end='')
                    print('\033[1;32;43m'+interface_dic[i['#']][0]+'\033[0m',end='')
                    print("\033[33;1m"+i['Comment']+'\033[0m')
                    print(interface_dic[i['#']][1])
                    print(interface_dic[i['#']][2])
                elif i['Status'] == 'Pending Further Information':
                    print("\033[33;1m [Pending]",end='')
                    print('\033[1;32;43m'+interface_dic[i['#']][0]+'\033[0m',end='')
                    print("\033[33;1m"+i['Comment']+'\033[0m')
                    print(interface_dic[i['#']][1])
                    print(interface_dic[i['#']][2])
                else:
                    print("\033[31;1m [UnChecked]",end='')
                    print('\033[1;32;43m'+interface_dic[i['#']][0]+'\033[0m')
                    print(interface_dic[i['#']][1])
                    print(interface_dic[i['#']][2])
                          

    #Shell Commands

    def do_EOF(self, line):
        with open(self.CACHE_PATH,'w') as w:
            w.write(json.dumps(self.db,indent=4,default=str))
        print('json file is saved.')
        return True
    
    def do_duo(self,line):
        print(line.split(' '))
    
    def do_edit(self,line=None):
        if not line:
            self._clear_console()
            self._edit_current_chunk()
        else:
            try:
                args = line.split(' ')
                node_index = int(args[0]) - 1
                chunk_index = int(args[1]) - 1
                if node_index >= len(self.db) or node_index<0:
                    print('[edit] invaild node index')
                elif chunk_index >= len(self._get_current_node()) or chunk_index < 0:
                    print('[edit] invaild chunk index')
                else:
                    self._current_node_index = node_index
                    self._current_chunk_index = chunk_index
                    self._clear_console()
                    self._edit_current_chunk()
            except Exception as e:
                print('[edit] unacceptable args, usage: edit <node_index> <chunk_index>')
                traceback.print_exc()

        
    def do_nextchunk(self,line):
        self._clear_console()
        if self._current_chunk_index + 1 ==len(self._get_current_node()):
            print('This is the last chunk.')
        else:
            self._current_chunk_index +=1
            self.do_edit(None)
        
    def do_lastchunk(self,line):
        self._clear_console()
        if self._current_chunk_index == 0:
            print('This is the first chunk.')
        else:
            self._current_chunk_index -= 1
            self.do_edit(None)
        
    def do_nextnode(self,line):
        self._clear_console()
        if self._current_node_index + 1 ==len(self.db):
            print('This is the last node')
        else:
            self._current_node_index += 1
#             self._current_chunk_index = 0 #first chunk of next node
            self.do_edit(None)
            
    def do_lastnode(self,line):
        self._clear_console()
        if self._current_node_index == 0:
            print('This is the first node')
        else:
            self._current_node_index -= 1
            self.do_edit(None)
            
    def do_search(self,id):
        node_num = 0
        
        for node_key in self.db.keys():
            chunk_num = 0
            for chunk_key in self.db[node_key].keys():
                sublist = self.db[node_key][chunk_key]
                for i in sublist:
                    if i['#'] == id:
                        self.do_edit(str(node_num)+' '+str(chunk_num))
                chunk_num+=1
            node_num+=1
        
            
    def do_comment(self,line):
        if not line:
            print('[comment]: comment <id> -m <message>/ -r / -t <template>')
            print('Example: c 123 -t sqlformat -l 300 -df')
        else:
            try:
                args = line.split(' ')
                if '-m' in args:#add custom comment, set as Open
                    self._set_open_comment(int(args[0]),' '.join(args[args.index('-m')+1:]))
                    self.do_edit(None)
                elif '-fp' in args:#add custom comment, set as FP
                    self._set_fp_comment(int(args[0]),' '.join(args[args.index('-fp')+1:]))
                    self.do_edit(None)
                elif '-pending' in args:#add template comment, set as Pending
                    self._set_pending_comment(int(args[0]),' '.join(args[args.index('-pending')+1:]))
                    self.do_edit(None)
                    
                elif '-r' in args:#Remove comment, set as None
                    self._remove_comment(int(args[0]))
                    self.do_edit(None)
                elif '-t' in args:#add template comment, set corresponding status
                    mode = 'Src'
                    line = None
                    if '-df' in args:
                        mode = 'Dest'
                    if '-sf' in args:
                        mode = 'Src'
                    if '-l' in args:
                        line = args[args.index('-l')+1]
                    self._set_comment_template(int(args[0]),args[args.index('-t')+1],mode,line)
                    self.do_edit(None)
                    
                    
                elif '-a' in args:#append custom comment, keep status
                    self._add_comment(int(args[0]),' '.join(args[args.index('-a')+1:]))
                    self.do_edit(None)
                elif '-ref' in args:#add reference comment
                    self._set_reference(int(args[0]),args[args.index('-ref')+1])
                    self.do_edit(None)
                elif '-deref' in args:#delete reference comment
                    self._detach_reference(int(args[0]))
                    self.do_edit(None)
                    
            except:
                print('[comment]: Unvalid args')
                print('[comment]: comment <id> -m <message>/-fp <message>  /-r / -t <template> <fp/sqlformat/sql+/pending> / -ref <target_id> / -deref')
                traceback.print_exc()
    def do_info(self,line):
        try:
            if not line:
                print('[comment]: info <id> <number of lines>')
            else:
                args = line.split(' ')
                self._get_code_line(int(args[0]),int(args[-1]))
        except:
            print('[info]: Unvalid args')
            traceback.print_exc()
    def do_c(self,line): self.do_comment(line)
    def do_lc(self,line): self.do_lastchunk(line)
    def do_nc(self,line): self.do_nextchunk(line)
    def do_ln(self,line): self.do_lastnode(line)
    def do_nn(self,line): self.do_nextnode(line)
    def do_e(self,line): self.do_edit(line)

        
    def do_merge(self,line):
        current_chunk = self._get_current_chunk()
        temp = {} #{line:id}
        for i in current_chunk:
            if not i['Line'] in temp:
                temp[i['Line']] = i['#']
            else:
                self._set_reference(i['#'],temp[i['Line']])
        self.do_edit(None)
        
    def do_save(self,line):
        with open(self.CACHE_PATH,'w') as w:
            w.write(json.dumps(self.db,indent=4,default=str))
        cprint('json file is saved.','SHELL',self.CACHE_PATH)

        
    def __del__(self):
        with open(self.CACHE_PATH,'w') as w:
            w.write(json.dumps(self.db,indent=4,default=str))
        cprint('json file is saved.','SHELL',self.CACHE_PATH)


    def do_export(self,line):
        if not line:
            REPORT_EXCEL_PATH = self.CACHE_PATH.split('.')[0]+'.xlsx'
        else:
            if '.xlsx' in line:
                REPORT_EXCEL_PATH = line
            else:
                REPORT_EXCEL_PATH = line + '.xlsx'
        wb_obj = openpyxl.load_workbook(REPORT_EXCEL_PATH)
        sheet = wb_obj['checkmarx']
        for node_key in self.db.keys():
            for chunk_key in self.db[node_key].keys():
                sublist = self.db[node_key][chunk_key]
                for i in sublist:
                    sheet['AF'+str(i['#']+1)].value = i['Comment']
                    if not 'reference' in i:
                        sheet['AB'+str(i['#']+1)].value = i['Status']

        for node_key in self.db.keys():
            for chunk_key in self.db[node_key].keys():
                sublist = self.db[node_key][chunk_key]

                for i in sublist:
                    if  'reference' in i:
                        #sync status
                        sheet['AB'+str(i['#']+1)].value = sheet['AB'+str(i['reference']+1)].value
                        #sync comment
                        # sheet['AF'+str(i['#']+1)].value = sheet['AF'+str(i['reference']+1)].value
                        #override comments col to fix bug
                        reference = str(i['reference'])
                        sheet['AF'+str(i['#']+1)].value = f'As the code triggers this issue and the remediation is the same, please refer to #{reference}'   
        wb_obj.save(REPORT_EXCEL_PATH)
        cprint('DB saved into'+REPORT_EXCEL_PATH,'SHELL')