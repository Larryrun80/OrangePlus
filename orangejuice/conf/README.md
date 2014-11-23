### Something about Config files

You should create your config file in this folder
Whitch named
With following format:

```
[DB_ORANGEJUICE]    
//Only support MySQL DB Now
Host = #your host# 
User = #your username#
Password = #your password#
Database = #your database# 

[MAIL_INFO]
SMTP = #your SMTP Server# 
User = #your username# 
Password = #your password# 

[LOG_FILE_SETTINGS]
Type = (Dynamic|Static) 
Dir = #your dir to create log files, '/' presents project root#
DynamicPart = %%Y%%m%%d # format of time string, to create Dynamic path
Format = %%(asctime)s : %%(levelname)s : %%(message)s
```
