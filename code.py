from random import randint
from queue import Queue
import os


PROC_COUNT = 20 # количество процессов
NUM_OF_TICKS = 2 # количество тиков


if not os.path.isfile("input.txt"):
    with open ("input.txt", "w") as f:
        for i in range(1, PROC_COUNT + 1):
            n, t1, t2, p = i, randint(0, 100), randint(1, 10), randint(0, 1)
            f.write(f"{n} {t1} {t2} {p}\n")


class Process:

    def __init__(self, number, readinessTime, requiredAmount, priority):
        self.number = number
        self.readinessTime = readinessTime
        self.requiredAmount = requiredAmount
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority if self.readinessTime == other.readinessTime else self.readinessTime < other.readinessTime



processes = []
processes_fifo = []
with open ("input.txt", "r") as f:
    for line in f.readlines ():
        n, t1, t2, p = map(int, line.split())
        processes.append(Process(n, t1, t2, p))
        processes_fifo.append(Process(n, t1, t2, p))


q = Queue()
for process in sorted(processes):
    q.put(process) 



class ProcessorState:
    tick = 0
    tick_fifo = 0
    last = None



last_trace_msg = None
def trace(msg, alg=False):
    global last_trace_msg
    if last_trace_msg == msg:
        return
    last_trace_msg = msg
    tick = ProcessorState.tick_fifo if alg == 'fifo' else ProcessorState.tick
    print(f'{tick}: {msg}')



print('=============== RR ===============')

while not q.empty():
    process, next_process = q.get(), q.queue[0] if q.qsize() else process

    if process.readinessTime > ProcessorState.tick and process == ProcessorState.last:
        diff = max(process.readinessTime - ProcessorState.tick, 0)
        trace(f'Пропущено тиков: {diff}')
        ProcessorState.tick = process.readinessTime
    elif process.readinessTime > ProcessorState.tick and not ProcessorState.last:
        q.put(process)
        ProcessorState.last = process
        continue
    elif process.readinessTime > ProcessorState.tick and ProcessorState.last:
        q.put(process)
        continue

    trace(f'Процесс {process.number} исполняется на процессоре')

    process.requiredAmount -= min(NUM_OF_TICKS, process.requiredAmount)
    ProcessorState.tick += min(NUM_OF_TICKS, process.requiredAmount)
    ProcessorState.last = None

    if process.requiredAmount > 0:
        q.put(process)
    else:
        trace(f'Процесс {process.number} завершил исполнение')



# FIFO
print('\n\n=============== FIFO ===============')

for process in sorted(processes_fifo):
    diff = max(process.readinessTime - ProcessorState.tick_fifo, 0)
    if diff:
        trace(f'Пропущено тиков: {diff}', 'fifo')
        ProcessorState.tick_fifo = process.readinessTime

    trace(f'Процесс {process.number} начал исполнение на процессоре', 'fifo')

    ProcessorState.tick_fifo += process.requiredAmount

    trace(f'Процесс {process.number} завершил исполнение', 'fifo')


print('\n\n==============================================================')
print('============Статистические результаты моделирования===========')
print('==============================================================')
print('\nСуммарное кол-во затраченных тактов процессора для RR:', f'{ProcessorState.tick}' )
print('Суммарное кол-во затраченных тактов процессора для FIFO:', f'{ProcessorState.tick_fifo}' )
