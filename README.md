# checkmarx_workspace
A toolkit for code audit in checkmarx platform, including web app simulation, work shell and much more.

There are three modules in this toolkit:

## Quick Start

### 0x00 Download checkmarx csv report and merge it into  a `xlsx` file 

Here is the sample format of xlsx report:

| Projects  Name | #    | Query | QueryPath | SrcFileName | Line | Column | NodeId | Name | DestFileName | DestLine | DestColumn | DestNodeId | DestName | Result State | Result Severity | Status | Link | Result Status | Detection Date | Comment | Manul  Verification | Fix Evidence |
| -------------- | ---- | ----- | --------- | ----------- | ---- | ------ | ------ | ---- | ------------ | -------- | ---------- | ---------- | -------- | ------------ | --------------- | ------ | ---- | ------------- | -------------- | ------- | ------------------- | ------------ |
|                |      |       |           |             |      |        |        |      |              |          |            |            |          |              |                 |        |      |               |                |         |                     |              |

Notes: leave **#** column blank, the program will automatically set index from 1 in this column.

### 0x01 Boost Shell

For the first time, using `init_from_excel` method to load xlsx file. This operation will generate a json file whose name is the project name for saving, and if everything is right, a cmd shell will be open. Please avoid using Visual Studio Code since `cmd` module will not displayed in the console.

```python
from common import DBBuilder
from shell import WorkShell

project_name = 'your-project-name'
xlsx_path = 'your-xlsx-path'

#Init from xlsx, and boost shell
WorkShell(builder=DBBuilder(project_name).init_from_excel(xlsx_name)).cmdloop()
```

If you already have the json file, use the command below to load the json file and boost shell, all changes in json file will be loaded.

```python
WorkShell(project_name='supply-ors-pu').cmdloop()
```

### 0x02 Using Shell

| Command                      | Arguments               | Discription                                                  | Example            |
| ---------------------------- | ----------------------- | ------------------------------------------------------------ | ------------------ |
| e/edit  `Node id` `Chunk id` |                         | Jump to target node and target chunk                         | e 1 1              |
| nc/nextchunk                 |                         | jump to next chunk                                           | nc                 |
| lc/lastchunk                 |                         | jump to last chunk                                           | lc                 |
| nn/nextnode                  |                         | jump to next node                                            | nn                 |
| ln/lastnode                  |                         | jump to last node                                            | ln                 |
| c/comment `record id`        | -m `message`            | Manually add comments, and set status as **Open**            | c 12 -m comments   |
|                              | -fp `message`           | Manually add comments, and set status as **False Positive**  | c 12 -fp comments  |
|                              | -t `template`           | See appendix below                                           | c 12 -t sql+       |
|                              | -a                      | Add extra comments.                                          | c 12 -a comments   |
|                              | -ref `target record id` | Add comments: `As the code triggers this issue and the remediation is the same, please refer to #<target record id>`, and link this reocrd to target record. | c 12 -ref 13       |
|                              | -deref                  | cancle the operation of `-ref`                               | c 12 -deref        |
| merge                        |                         | automatically use `-ref` for every record in this node, checking the `line` attribution. | merge              |
| export `xlsx path`           |                         | Transmit all changes in json file into xlsx report. This operation effects **AB** and **AF** columns, which is **Status** and **Comments** | export report.xlsx |

When using `-t` commands:

- `-t sqlformat` :Add comments nd set Status as **Open**, where line is the `line` attribution and filename is `SrcFileName` attribution.

  ```python
  The application uses 'String.format' to embed untrusted params and construct sql queries at line {line} of {filename}, which may cause sql injection attacks.
  ```

- `-t sql+` : Add comments and set Status as **Open**, where line is the `line` attribution and filename is `SrcFileName` attribution.

  ```python
  The application uses string concatenation to embed untrusted params and construct sql queries at line {line} of {filename}, which may cause sql injection attacks.
  ```

- Use `-l line` to modify line value above, and use `-df` to change filename as `DestFileName`

- `-t pending` : Add comments, and set Status as **pending**

  ```
  The application uses string concatenation to embed untrusted params and construct sql queries at line {line} of {filename}, which may cause sql injection attacks.
  ```

- `-t fp1` : Add comments, and set Status as **False Positive**

  ```
  The global filterring method has been used , or there are other filtering methods, but it is not recognized by checkmarx
  ```

  

- `-t fp2` : Add comments, and set Status as **False Positive**

  ```
  The input has been restricted on characters, such as length, character type, etc., but it is not recognized by checkmarx.
  ```

  

- `-t fp3` : Add comments, and set Status as **False Positive**

  ```
  The input comes from a trusted source, such as constants or variables that are not input by the user, but it is not recognized by checkmarx.
  ```

  

- `-t fp4` : Add comments, and set Status as **False Positive**

  ```
  The output will not cause vulnerabilities, but the tool misreports the vulnerabilities.
  ```

  

- `-t fp5` : Add comments, and set Status as **False Positive**

  ```
  There is no logical relationship between the data flow provided by Checkmarx.
  ```

### 0x03 Using Web

  Currently you can use codes below to **automatically load all 'False Positive' records in your xlsx file and set them as 'Not Exploitable' or any other status in Checkmarx.** 

```python
from web import CheckmarxDriver


your_system_user_name = 'yourname'

json_file_to_save_the_work_queue = 'url-list.json'

your_completed_xlsx_path = 'report.xlsx'

status_col_index_in_xlsx = 'AB'

link_col_index_in_xlsx = 'AC'

status_you_want_to_load_into_workqueue = 'False Positive'

status_you_want_to_set_as = 'Not Exploitable' #must be one of checkmarx status

#Init a driver, and name a json file path where you want to save your work queue.
driver = CheckmarxDriver(your_system_user_name).set_workqueue_cache_path(json_file_to_save_the_work_queue)
driver.init_workqueue_from_excel(your_completed_xlsx_path,link_col_index_in_xlsx,status_col_index_in_xlsx,status_you_want_to_load_into_workqueue)
#If you quit the program, you can load the workqueue from json file directly using the method below: 
# driver.load_workqueue_from_json()

#After init/load workqueue, you can use `exec_workqueue` to run the work queue. 


driver.exec_workqueue(change_to=status_you_want_to_set_as)
```



Notes: This operation will load your **chrome** user data in your computer. Make sure you can access checkmarx in chrome via Domain authentication. Make sure the chrome is closed when running the script.

---

## Known issues 

Here are known  issues we will fix in later update.

1. Sometimes an error ''append' method can not be implemented in dic format will raise. Try restart your jupyter, delete any json file created.
2. Chrome might not be able to continue loading pages due to memory issue. Try restart script.
3. When using `e` the chunk index will not be reset as `1` ,  which will raise out of range issue. 
4. Make sure you have correct zoom in chrome using script, or the login may fail.

## Roadmaps

1. More browser support.
2. Prefetch checkmarx data.
3. Web GUI/ Better console UI using `rich` 
