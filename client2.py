import rpyc
import time
from copy import deepcopy
import threading


class Client(object):

    def __init__(self):
        # init values
        self.conn = None
        self.user = None
        self.name = "Ann"
        self.iterationsCount = 0
        self.iterations_size = 10
        self.active_clients_count = 0
        self.isStart = False

        self.my_pi = []

        self.received_pi = []
        self.result_pi = 0
        self.messages_counter = 0

        self.current_iteration = 0

        self.on_connect()

        self.t1 = threading.Thread(target=self.user_input)
        self.t1.start()

        if (self.iterationsCount > 0):
            self.t1.join()

        self.t2 = threading.Thread(target=self.cycle)
        self.t2.start()

        self.t2.join()

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
            self.user = self.conn.root.login(self.name, self.on_received, self.update_data, self.kill_user_input)
        except ValueError:
            self.conn.close()
            self.conn = None
            return

    def user_input(self):
        self.iterationsCount = int(input("Please, type the iterations count: "))
        self.user.kill_other_user_input()
        print("I am worked")

    def cycle(self):
        while self.iterationsCount == 0:
            print("self.iterationsCount = ", self.iterationsCount)
            time.sleep(1)
        print("Cycle end!")

    def start(self):
        if self.isStart:
            return
        self.isStart = True

        print("I am start!")

        while deepcopy(self.iterationsCount) > 0:
            self.calculate_pi()
            self.update_iterations(deepcopy(self.iterationsCount) - self.iterations_size)
            self.on_send()
        self.end()

    def end(self):
        for pi in self.my_pi:
            self.result_pi += pi
        print("My pi = ", self.result_pi)

        received_pi = 0
        for pi in self.received_pi:
            received_pi += pi
        print("Received pi = ", received_pi)

        self.result_pi += received_pi
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
        text = self.my_pi[len(self.my_pi)-1]
        print("Send ", text)
        self.user.send_pi(text)

    def on_received(self, text):
        mes = text.split(' ')
        name = "[" + self.name + "]"
        if mes[0] == name:
            return
        self.received_pi.append(float(mes[1]))

    def update_iterations(self, unsolved):
        if unsolved < 0:
            self.iterationsCount = 0
            self.user.update_data(self.iterationsCount, self.iterations_size, self.current_iteration)
            return

        print("")
        print("Unsolved = ", unsolved)

        last_active_clients_count = self.user.get_active_clients_count()

        if not (self.active_clients_count == last_active_clients_count):
            self.active_clients_count = last_active_clients_count
            delta_iteration = int (unsolved / self.active_clients_count)
            self.iterationsCount = delta_iteration
            print("Iterations count = ", self.iterationsCount)
        else:
            self.iterationsCount = unsolved

        self.user.update_data(self.iterationsCount, self.iterations_size, self.current_iteration)

        self.size = last_active_clients_count
        self.rank = self.user.get_rank()

    def update_data(self, iterCount, iterSize, currentIteration):
        if self.t1.isAlive:
            self.t1.join()

        print("")
        print("I update my data ", iterCount, iterSize, currentIteration)

        self.iterationsCount = iterCount
        self.iterations_size = iterSize
        self.current_iteration = currentIteration

        self.size = self.user.get_clients_count()
        self.rank = self.user.get_rank()

        self.start()

    def kill_user_input(self):
        if self.t1.isAlive:
            print("I kill t1")
            self.t1.join()

if __name__ == "__main__":
    cc = Client()







