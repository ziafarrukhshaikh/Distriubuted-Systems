#Zia Farrukh Shaikh
import sys
print("Standard Input:")

try:
    while True:
       string = input()
       print(string)
except EOFError:      
    pass

print("Command Line Arguments:")
options = ""
values = []
argc = len(sys.argv)

for i in range(1,argc):

    if sys.argv[i] == "-o":
        options = "options 1: "
        i = i + 1
        values.insert(2,options + sys.argv[i])
        continue
    if sys.argv[i] == "-t":
        options = "options 2: "
        i = i + 1
        values.insert(1,options + sys.argv[i])
        continue
    if sys.argv[i] == "-h":
        options = "options 3: "
        i = i + 1
        values.insert(0,options)
        continue

for i in reversed(values):
    print(i)