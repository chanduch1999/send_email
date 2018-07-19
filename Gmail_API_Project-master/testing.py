# my_file = open("file.txt", "r")
# print my_file
# my_file.close()
from datetime import date
# today = str(date.today())
# print(today)

#from __future__ import print_function

today = str(date.today())
print("Today Date :" + today)

today = '[%s]' % date.today().strftime('%d-%m-%Y')

print (today)
