from common import DBBuilder
from shell import WorkShell

#Init and do not launch shell
builder=DBBuilder('project').init_from_excel('yourexcel.xlsx')
#Init and launch shell
WorkShell(builder=DBBuilder('project').init_from_excel('yourexcel.xlsx')).cmdloop()

#Reload
#Approach 1
WorkShell(builder=DBBuilder('project').init_from_json()).cmdloop()
#Approach 2
WorkShell(project_name='project').cmdloop()

