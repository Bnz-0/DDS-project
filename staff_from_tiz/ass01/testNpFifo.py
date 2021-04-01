from NpFifo import Fifo
import random


f = Fifo()
print(f.size())

f.append(1)
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size)
f.append(2)
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size)
f.append(3)
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size)
f.append(4)
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size)
f.append(5)
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size)
f.append(6)
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size)
f.append(7)
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size)
f.append(8)
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size)
f.append(9)
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size)
f.append(10)
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size)
f.append(11)
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size)
f.append(12)
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size)

print("len: ", len(f))
print("f[0] = ", f[0])

print(f.popleft(), f[0])
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size, "len: ", len(f))
print(f.popleft(), f[0])
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size, "len: ", len(f))
print(f.popleft(), f[0])
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size, "len: ", len(f))
print(f.popleft(), f[0])
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size, "len: ", len(f))
print(f.popleft(), f[0])
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size, "len: ", len(f))
print(f.popleft(), f[0])
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size, "len: ", len(f))
print(f.popleft(), f[0])
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size, "len: ", len(f))
print(f.popleft(), f[0])
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size, "len: ", len(f))
print(f.popleft(), f[0])
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size, "len: ", len(f))
print(f.popleft(), f[0])
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size, "len: ", len(f))
print(f.popleft(), f[0])
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size, "len: ", len(f))
print(f.popleft(), f[0])
print ("i_pop: ", f.i_pop, ", i_push: ", f.i_push, ", _size: ", f._size, "len: ", len(f))



f = Fifo()
l = []
i = 0
for z in range(10000000):
  # 0 pop, 1 insert random
  if random.randint(0,1) == 1:
    r = random.randint(0,10000)
    l.append(r)
    f.append(r)
  else:
    e = f.popleft()
    if i>=len(l):
      assert e == None
    else:
      assert e == l[i]
      i += 1
      
