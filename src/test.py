import multiprocessing
import os
import queue

q = queue.Queue()
def run_proc(name):
    print('Child process {0} {1} Running '.format(name, os.getpid()))

def insert():
    for i in range(10):
       # print(i)
        q.put(i)
        print(q.qsize())

if __name__ == '__main__':
    print('Parent process {0} is Running'.format(os.getpid()))
    p = multiprocessing.Process(target=insert, args=())
    print('process start')
    p.start()
    p.join()
    print('Process close')