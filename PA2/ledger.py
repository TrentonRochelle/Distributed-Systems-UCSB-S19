import os
if os.path.exists("ledger1.txt"):
  os.remove("ledger1.txt")
if os.path.exists("ledger1.txt"):
  os.remove("ledger2.txt")
if os.path.exists("ledger1.txt"):
  os.remove("ledger2.txt")
f = open('ledger1.txt','w')
g = open('ledger2.txt','w')
h = open('ledger3.txt','w')
a = "Alice:100\n"
b = "Bob:100\n"
c = "Carol:100\n"
f.write(a)
f.write(b)
f.write(c)
g.write(a)
g.write(b)
g.write(c)
h.write(a)
h.write(b)
h.write(c)


f.close()
g.close()
h.close()