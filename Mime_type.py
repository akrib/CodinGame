import sys
import math

listeMt=[]
listeExt=[]
n = int(input())
q = int(input())
for i in range(n):
    ext, mt = input().split()
    listeMt.append(mt)
    listeExt.append(ext.upper())
for i in range(q):
    fname = input()
    fname = fname.split(".")
    if len(fname) > 1:
        if fname[-1].upper() in listeExt:
            print(listeMt[listeExt.index(fname[-1].upper())])
        else:
            print("UNKNOWN")
    else:
         print("UNKNOWN") 
