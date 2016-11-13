# coding: utf8
import rpyc
from random import random
from math import sqrt, ceil
import threading
import time


class Client(object):
    def __init__(self):
        self.current_my_value = 0
        self.my_data = []
        self.received_data = []
        self.iteration_size = 0
        self.iterations_count = 0
        self.name = "Bob"
        self.other = None
        self.conn = None
        self.wait_me = False
        self.alreadyCalc = 0

        self.on_connect()
        self.calculate(100000000 / 4, 10)

    def calculate(self, count, iterations):
        iterCount = iterations
        iterSize = int(count / iterCount)
        print("Общее количество итераций = ", iterCount * 4)
        print("Количество итераций в одном шаге = ", iterSize)

        self.update_data(iterCount, iterSize)

        self.mass_start()

    def mass_start(self):
        t1 = threading.Thread(target=self.main)
        t1.start()
        t1.join()
        # self.main()

    def main(self):
        time.clock()
        result = self.get_result()
        print("\nРезультат = ", result)
        print("Время счета ", time.clock())

    def get_result(self):
        iterationsCount = self.iterations_count * 4 # сколько всего вычислений
        self.alreadyCalc = self.is_all_over() # сколько уже сделано

        while self.alreadyCalc < iterationsCount:
            w = self.other.get_wait_me_clients_count()
            # print("\nWait me = ", w)
            doing = self.alreadyCalc + w# сколько сделано на данный момент задач + сколько делаются в данный момент
            print("\nВ работе ", doing)
            if doing < iterationsCount: #// ??? // Если ктото упал  // и при этом есть свободные итерации
                self.next_step()  # берем итерацию и делаем
            else:
                print("\nЯ закончил счет")
                break
            self.alreadyCalc = self.is_all_over() # обновляем общее значение сделанных итераций
            print("Посчитано ", self.alreadyCalc)

        while self.other.get_wait_me_clients_count() > 0:
            time.sleep(0.5)

        count = len(self.my_data)
        print("Я посчитал ", count)
        result = 0
        for value in self.my_data:
            result += value

        for rec_result in self.received_data:
            result += rec_result

        count += len(self.received_data)

        print("\nОбщее количество = ", count)
        # print("Pre-result = ", result)
        return float((result * 4) / count)

    def is_all_over(self):
        dataCount = len(self.my_data)
        # print("My data count = ", dataCount)
        dataCount += self.get_received_data_count()
        # print("Sum data count = ", dataCount)
        return dataCount

    def get_received_data_count(self):
        # print("len(self.received_data) ", len(self.received_data))
        return len(self.received_data)

    def next_step(self):
        # Сообщаем каждому, с кем есть связь, что мы считаем
        self.other.wait_me(True)

        self.make_iteration() #// Считаем один блок

        self.alreadyCalc = self.is_all_over()
        if self.alreadyCalc < self.iterations_count * 4:
            # рассылаем всем посчитаный блок
            self.other.update_information(self.my_data[len(self.my_data) - 1])
        else:
            print("\nI not send the data!\n")
            self.my_data.pop()
        self.other.wait_me(False)

    def get_wait(self):
        return self.wait_me

    def make_iteration(self):
        self.current_my_value = 0
        for i in range(0, int(self.iteration_size)):
            self.current_my_value += self.is_enter()
        data = float(self.current_my_value/self.iteration_size)
        # print("data = ", data)
        self.my_data.append(data)

    def is_enter(self):
        """// Берет произвольную точку в квадрате с ребром 1 и считает её удаленность от левого нижнего угла
        // Возвращает 1, если точка находится в окружности
        // Возвращает 0, если точка за пределами окружности"""
        x = random()
        y = random()
        z = sqrt(x*x + y*y)

        if z <= 1:
            return 1
        return 0

    def update_data(self, count, size):
        # print("\nupdate_data ", count, size)
        self.my_data = []
        self.iterations_count = count
        self.iteration_size = size
        self.received_data = []

    def update_information(self, name, value):
        if name == self.name:
            return
        # print("\nUpdate information ", value)
        self.received_data.append(value)
        self.alreadyCalc = self.is_all_over()

    def disconnect(self):
        if self.conn:
            try:
                self.other.logout()
            except:
                print("Logout except")
            self.conn.close()
            self.other = None
            self.conn = None

    def on_close(self):
        print("I closed!")
        self.disconnect()

    def on_connect(self):
        try:
            self.conn = rpyc.connect("localhost", 19913)
        except Exception:
            print("\nEXCEPTION!!!\n")
            self.conn = None
            return
        try:
            self.other = self.conn.root.login(self.name, self.update_data, self.mass_start,
											  self.get_wait, self.update_information, self.get_received_data_count)
        except ValueError:
            self.conn.close()
            self.conn = None

if __name__ == "__main__":
    cc = Client()