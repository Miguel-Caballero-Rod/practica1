from multiprocessing import Process
from multiprocessing import Semaphore
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint

NPROD = 5   
N = 10

def delay(factor = 10):
    sleep(random()/factor)

def produce_num(val):
    val.value+=randint(1,10)   # SUMA UN NÚMERO DEL 1 AL 9

def producer(sem, val, full):   # sem cap 1 y full cap NPROD
    for i in range(N):
        produce_num(val)
        print (f"{current_process().name} produciendo...")
        sem.release()
        full.acquire()  # espera a que el consumidor le diga de volver a producir
        delay()
    val.value=-1    # Ha terminado
    sem.release()
    print(f"{current_process().name} terminado")

def obtener_minimo(lista_numeros):  #devuelve el minimo valor mayor que 0 y su posicion
    pos,val=-1,-1
    i=0
    terminado=True
    while i<len(lista_numeros) and terminado:
        if lista_numeros[i].value<0:
            i+=1
        else:
            terminado=False
    if not terminado:
        pos=i
        val=lista_numeros[i].value
        for j in range(i+1,len(lista_numeros)):
            if lista_numeros[j].value>=0 and lista_numeros[j].value<val:
                pos=j
                val=lista_numeros[j].value
    return pos,val,terminado

def consumidor(semaforos_vac, semaforos_llen, lista_numeros, array_salida):
    terminado = False
    k=0
    for s in semaforos_vac:  #Espera a que todos los productores hayan producido el primer numero
        s.acquire()
    while not terminado:
        pos, val, terminado=obtener_minimo(lista_numeros)
        if not terminado:
            array_salida[k]=val
            print ("ordenando...")
            k+=1
            semaforos_llen[pos].release()
            semaforos_vac[pos].acquire()
            delay()

def main():
    storage = [Value('i', 0) for i in range(NPROD)]
    print ("almacen inicial", [v.value for v in storage])

    semaforos_vac = [Semaphore(0) for i in range(NPROD)]

    semaforos_llen = [Semaphore(0) for i in range(NPROD)]

    prodlst = [ Process(target=producer,
                        name=f'productor_{i}',
                        args=(semaforos_vac[i], storage[i], semaforos_llen[i]))
                for i in range(NPROD) ]

    salida = Array('i', N*NPROD)

    proc_cons = Process(target=consumidor,
                        name='consumidor',
                        args=(semaforos_vac, semaforos_llen, storage, salida))
    
    print('inicializando productores...')
    
    for p in prodlst:
        p.start()
    
    print('inicializando consumidor...')
    
    proc_cons.start()

    for p in prodlst:
        p.join()

    proc_cons.join()

    print('\nLISTA FINAL ORDENADA:\n')

    print(list(salida))

if __name__ == '__main__':
    main()