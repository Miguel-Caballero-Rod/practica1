from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint

NPROD = 5
N = 10

def delay(factor = 3):
    sleep(random()/factor)

def produce_num(val):
    val.value+=randint(1,5)   # SUMA UN NÚMERO DEL 1 AL 4
    
def producer(sem, val, full):   # sem cap 1 y full cap NPROD
    for i in range(N):
        produce_num(val)
        sem.acquire()
        full.release()

def obtener_minimo(array):  #tener en uenta el >0 y que coja luego el menor
    pos,val=-1,-1
    for i in range(len(array)):
        if array[i].value>val:
            val=array[i].value
            pos=i
    return pos,val

def main():
    storage = Array('i', NPROD)
    index = Value('i', 0)
    for i in range(NPROD):
        storage[i] = -1
    print ("almacen inicial", storage[:], "indice", index.value)

    non_empty = Semaphore(0)
    empty = BoundedSemaphore(NPROD)
    mutex = Lock()

    prodlst = [ Process(target=producer,
                        name=f'prod_{i}',
                        args=(storage, index, empty, non_empty, mutex))
                for i in range(NPROD) ]

    for p in prodlst:
        p.start()

    for p in prodlst:
        p.join()


if __name__ == '__main__':
    main()