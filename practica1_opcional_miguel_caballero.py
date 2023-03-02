from multiprocessing import Process
from multiprocessing import Semaphore
from multiprocessing import current_process
from multiprocessing import Value, Array, Manager
from time import sleep
from random import random, randint

NPROD = 5   
N = 10
k = 2

def delay(factor = 10):
    sleep(random()/factor)

def produce_num(storage, pos, sem):
    if pos == 0:
        num = randint(1,10)
    else:
        num = storage[(pos-1)%len(storage)]+randint(1,10)
    sem.acquire()
    storage[pos%len(storage)]=num

def producer(sem, storage, sem_cap):   # sem cap 1 y full cap NPROD
    for i in range(N):
        produce_num(storage, i, sem_cap)
        print (f"{current_process().name} produciendo...")
        sem.release()  #hace release tantas veces como numeros producidos, por lo que 
                        #el consumidor siempre puede acceder a la componente "#releases"
        delay()
    sem.release()
    print(f"{current_process().name} terminado")

def obtener_minimo(listas_numeros, listas_pos):
    lista_elementos_validos=[]
    for i, val in enumerate(listas_pos):
        if val.value < N:  # en otro caso ya se ha ordenado entero este array
            lista_elementos_validos.append((listas_numeros[i][val.value%len(listas_numeros[i])],i))
    if len(lista_elementos_validos)!=0:
        val,pos=min(lista_elementos_validos)
        terminado=False
    else:
        val,pos=-1,-1
        terminado=True
    return val,pos,terminado

def consumidor(semaforos_vac, listas_numeros, listas_pos, sem_cap, array_salida):
    terminado = False
    for s in semaforos_vac:
        s.acquire()
    while not terminado:
        val, pos, terminado=obtener_minimo(listas_numeros, listas_pos)
        if not terminado:
            listas_pos[pos].value += 1
            print ("ordenando...")
            array_salida.append(val)
            sem_cap[pos].release()
            semaforos_vac[pos].acquire()
            delay()

#no hay excxlusion mutua ya que acceden a componentes distintas de array storage

def main():
    lista_pos = [Value('i', 0) for i in range(NPROD)]

    semaforos_vac = [Semaphore(0) for i in range(NPROD)]
    
    storages = [Array('i', k) for i in range(NPROD)]
    
    capacidades = Array('i', NPROD)
    for i,a in enumerate(storages):
        capacidades[i] = len(a)

    sem_capacidad = [Semaphore(i) for i in capacidades]

    prodlst = [ Process(target=producer,
                        name=f'productor_{i}',
                        args=(semaforos_vac[i], storages[i], sem_capacidad[i]))
                for i in range(NPROD) ]

    salida = Manager().list()

    proc_cons = Process(target=consumidor,
                        name='consumidor',
                        args=(semaforos_vac, storages, lista_pos, sem_capacidad, salida))
    
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