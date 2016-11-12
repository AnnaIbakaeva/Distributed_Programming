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
        print("iterCount, iterSize: ", iterCount, iterSize)

        self.update_data(iterCount, iterSize)

        self.mass_start()

    def mass_start(self):
        self.main()

    def main(self):
        result = self.get_result()
        print("\nResult pi = ", result)

    def get_result(self):
        iterationsCount = self.iterations_count * 4 # сколько всего вычислений
        self.alreadyCalc = self.is_all_over() # сколько уже сделано

        print("\nBefore while, iterationsCount = ", iterationsCount, " alreadyCalc = ", self.alreadyCalc)
        while self.alreadyCalc < iterationsCount:
            # aviable = self.other.get_active_clients_count() # сколько активных учатсникв
            # clients = self.other.get_clients_count() # сколько всего должно быть
            w = self.other.get_wait_me_clients_count()
            print("\nself.other.get_wait_me_clients_count() = ", w)
            doing = self.alreadyCalc + w# сколько сделано на данный момент задач + сколько делаются в данный момент
            print("doing ", doing)
            if doing < iterationsCount: #// ??? // Если ктото упал  // и при этом есть свободные итерации
                self.next_step()  # берем итерацию и делаем
            else:
                print("I end calculate")
                break
            self.alreadyCalc = self.is_all_over() # обновляем общее значение сделанных итераций
            print("alreadyCalc ", self.alreadyCalc)

        while self.other.get_wait_me_clients_count() > 0:
            time.sleep(0.5)

        count = len(self.my_data)
        result = 0
        for value in self.my_data:
            result += value

        for rec_result in self.received_data:
            result += rec_result

        count += len(self.received_data)

        print("\ncount = ", count)
        print("Pre-result = ", result)
        return float((result * 4) / count)

    def is_all_over(self):
        dataCount = len(self.my_data)
        print("My data count = ", dataCount)
        dataCount += self.get_received_data_count()
        print("Sum data count = ", dataCount)
        return dataCount

    def get_received_data_count(self):
        print("len(self.received_data) ", len(self.received_data))
        return len(self.received_data)

    def next_step(self):
        # Сообщаем каждому, с кем есть связь, что мы считаем
        self.wait_me = True

        self.make_iteration() #// Считаем один блок
        # рассылаем всем посчитаный блок
        print("self.other.update_information ", self.my_data[len(self.my_data) - 1])
        self.other.update_information(self.my_data[len(self.my_data) - 1])
        self.wait_me = False

    def get_wait(self):
        return self.wait_me

    def make_iteration(self):
        self.current_my_value = 0
        for i in range(0, int(self.iteration_size)):
            self.current_my_value += self.is_enter()
        data = float(self.current_my_value/self.iteration_size)
        print("data = ", data)
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
        print("\nupdate_data ", count, size)
        self.my_data = []
        self.iterations_count = count
        self.iteration_size = size
        self.received_data = []

    def update_information(self, name, value):
        if name == self.name:
            return
        print("Update inforemation ", value)
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
            self.conn = rpyc.connect("localhost", 19912)
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