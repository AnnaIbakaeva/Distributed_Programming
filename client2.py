import rpyc
import time
from copy import deepcopy
import threading


class Client(object):

    def __init__(self):
        # init values
        self.conn = None
        self.user = None
        self.name = "Kate"
        self.iterationsCount = 10000
        self.iterations_size = 10
        self.active_clients_count = 0
        self.isStart = False

        self.my_pi = []

        self.received_pi = 0
        self.result_pi = 0
        self.messages_counter = 0

        self.current_iteration = 0

        self.on_connect()

        self.update_iterations(self.iterationsCount)
        self.current_iteration = self.rank

        self.start()

        self.on_close()

    def disconnect(self):
        if self.conn:
            try:
                self.user.logout()
            except:
                print("Logout except")
                pass
            self.conn.close()
            self.user = None
            self.conn = None

    def on_close(self):
        print("I closed!")
        self.disconnect()

    def on_connect(self):
        try:
            self.conn = rpyc.connect("localhost", 19912)
        except Exception:
            print("")
            print("EXCEPTION!!!")
            print("")
            self.conn = None
            return
        try:
            self.user = self.conn.root.login(self.name, self.on_received, self.update_data)
        except ValueError:
            self.conn.close()
            self.conn = None
            return

    def start(self):
        if self.isStart:
            return
        self.isStart = True

        print("I am start!")

        while deepcopy(self.iterationsCount) - deepcopy(self.current_iteration) > 0:
            self.calculate_pi()
            self.update_iterations(deepcopy(self.iterationsCount) - deepcopy(self.current_iteration))
            self.on_send()
        self.end()

    def end(self):
        for pi in self.my_pi:
            self.result_pi += pi
        print("My pi = ", self.result_pi)

        print("Received pi = ", self.received_pi)

        self.result_pi += self.received_pi
        print("Result pi = ", self.result_pi)
        print("Result 4*pi = ", self.result_pi*4)

    def calculate_pi(self):
        j = 0
        pi = 0
        for i in range(self.current_iteration, self.iterationsCount, self.size):
            print("i = ", i)
            pi += pow(-1, i) / (2 * i + 1)
            j += 1
            if j == self.iterations_size:
                break
        self.my_pi.append(pi)
        self.current_iteration += self.size * j

    def on_send(self):
        send_pi = 0
        for p in self.my_pi:
            send_pi += p
        # text = self.my_pi[len(self.my_pi)-1]
        print("Last temp pi = ", self.my_pi[len(self.my_pi)-1])
        print("Send ", send_pi)
        self.user.send_pi(send_pi)

    def on_received(self, text):
        mes = text.split(' ')
        name = "[" + self.name + "]"
        if mes[0] == name:
            return
        self.received_pi = float(mes[1])

    def update_iterations(self, unsolved):
        # if unsolved < 0:
            # self.iterationsCount = 0
            # self.user.update_data(self.iterationsCount, self.iterations_size, self.current_iteration)
            # return

        print("")
        print("Unsolved = ", unsolved)

        last_active_clients_count = self.user.get_active_clients_count()

        if not (self.active_clients_count == last_active_clients_count):
            self.active_clients_count = last_active_clients_count
            delta_iteration = int (unsolved / self.active_clients_count)
            # self.iterationsCount = delta_iteration + self.current_iteration
            print("Iterations count = ", self.iterationsCount)
            self.user.update_data(self.iterationsCount, self.iterations_size, self.current_iteration)
        # else:
        #     pass
            # self.iterationsCount = unsolved



        self.size = last_active_clients_count
        self.rank = self.user.get_rank()

    def update_data(self, name, iterCount, iterSize, currentIteration):
        if self.name == name:
            return

        if currentIteration < self.current_iteration:
            print(" I AM NOT WILL UPDATE MY DATA!!!!")
            return

        print("")
        print("I update my data ", iterCount, iterSize, currentIteration)

        self.iterationsCount = iterCount
        self.iterations_size = iterSize

        self.size = self.user.get_clients_count()
        self.rank = self.user.get_rank()

        print("Rank = ", self.rank)
        self.current_iteration = currentIteration + self.rank


        self.start()

if __name__ == "__main__":
    cc = Client()







