from random import randint
from queue import Queue
import os


PROC_COUNT = 20 # количество процессов
NUM_OF_TICKS = 2 # количество тиков


if not os.path.isfile("input.txt"):
    with open ("input.txt", "w") as f:
        f.write(f"Номер | Время готовности | Время исполнения | Приоритет\n")
        for i in range(1, PROC_COUNT + 1):
            n, t1, t2, p = i, randint(0, 100), randint(1, 10), randint(0, 1)
            f.write(f"{n:^6} {t1:^18} {t2:^18} {p:^10}\n")



class Process:

    def __init__(self, number, readinessTime, requiredAmount, priority):
        self.number = number
        self.readinessTime = readinessTime
        self.origRequiredAmount = requiredAmount
        self.requiredAmount = requiredAmount
        self.priority = priority
        self.arrivalTime = None
        self.burstTime = None

    def __lt__(self, other):
        return self.priority < other.priority if self.readinessTime == other.readinessTime else self.readinessTime < other.readinessTime

    def execute_rr(self):

        tick = ProcessorState.tick
        print(f'{tick:3}: ', end=' ')
        print(f'{self.number:^4}| Готовы: ', end='')
        for i in q.queue:
            if i.readinessTime > tick:
                continue
            print(i.number, end=' ')
        print('| Блокированы: ', end=' ')
        for i in q.queue:
            if i.readinessTime <= tick:
                continue
            print(i.number, end=' ')
        print('')


        exec_ticks = min(NUM_OF_TICKS, self.requiredAmount)
        self.requiredAmount -= exec_ticks
        ProcessorState.tick += exec_ticks

        # если процесс еще не завершил свое исполнение, возвращаем True
        if self.requiredAmount > 0:
            return True

        # иначе запоминаем время, в которое этот процесс завершил свое исполнение
        # выводим в лог сообщений и возвращаем False
        self.burstTime = ProcessorState.tick

        # подсчитываем статистику
        ProcessorState.waiting_time_rr += self.burstTime - self.readinessTime - self.origRequiredAmount
        ProcessorState.execution_time_rr += self.burstTime - self.readinessTime

        trace(f'Процесс {self.number} завершил исполнение')
        return False



processes = []
processes_fifo = []
with open ("input.txt", "r") as f:
    f.readline()
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

    # RR
    waiting_time_rr = 0
    execution_time_rr = 0

    # FIFO
    waiting_time_fifo = 0
    execution_time_fifo = 0



last_trace_msg = None
def trace(msg, alg=False):
    global last_trace_msg
    if last_trace_msg == msg:
        return
    last_trace_msg = msg
    tick = ProcessorState.tick_fifo if alg == 'fifo' else ProcessorState.tick
    print(f'{tick:3}: {msg}')



print('=============== RR ===============')

while not q.empty():
    process = q.get()

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

    ProcessorState.last = None
    if process.execute_rr():
        q.put(process)


ProcessorState.waiting_time_rr /= PROC_COUNT
ProcessorState.execution_time_rr /= PROC_COUNT




# FIFO
print('\n\n=============== FIFO ===============')

for process in sorted(processes_fifo):
    diff = max(process.readinessTime - ProcessorState.tick_fifo, 0)
    if diff:
        trace(f'Пропущено тиков: {diff}', 'fifo')
        ProcessorState.tick_fifo = process.readinessTime

    trace(f'Процесс {process.number} начал исполнение на процессоре', 'fifo')

    ProcessorState.tick_fifo += process.requiredAmount
    ProcessorState.waiting_time_fifo += ProcessorState.tick_fifo - process.readinessTime - process.requiredAmount
    ProcessorState.execution_time_fifo += ProcessorState.tick_fifo - process.readinessTime

    trace(f'Процесс {process.number} завершил исполнение', 'fifo')



ProcessorState.waiting_time_fifo /= PROC_COUNT
ProcessorState.execution_time_fifo /= PROC_COUNT



print(f'''

==============================================================
============Статистические результаты моделирования===========
==============================================================

Суммарное кол-во затраченных тактов процессора для RR: {ProcessorState.tick}
Среднее время ожидания RR: {ProcessorState.waiting_time_rr}
Среднее время выполнения RR: {ProcessorState.execution_time_rr}

Суммарное кол-во затраченных тактов процессора для FIFO: {ProcessorState.tick_fifo}
Среднее время ожидания FIFO: {ProcessorState.waiting_time_fifo}
Среднее время выполнения FIFO: {ProcessorState.execution_time_fifo}
==============================================================
''')
