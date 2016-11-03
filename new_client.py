__author__ = 'Anna'
import rpyc
import time
import threading


class Client(object):
    def __init__(self):
        self.name = "Ann"
        self.conn = None
        self.others = [19913]
        self.my_port = 19912
        self.isStart = False
        self.iterations_count = 0
        self.iterations_size = 10
        self.current_iteration = 0
        self.received_pi = []

        self.server = None

        self.on_connect()

        self.t1 = threading.Thread(target=self.user_input)
        self.t1.start()

        self.t2 = threading.Thread(target=self.cycle)
        self.t2.start()

        self.t2.join()

        print("After join")


    def on_connect(self):
        try:
            self.conn = rpyc.connect("localhost", self.my_port)
        except Exception:
            print("")
            print("EXCEPTION!!!")
            print("")
            self.conn = None
            return
        try:
            self.server = self.conn.root.login(self.name, self.on_received, self.update_data)
            print("I login")
        except ValueError:
            print("")
            print("EXCEPTION self.conn.root.login!!!")
            print("")
            self.conn.close()
            self.conn = None

    def user_input(self):
        self.iterations_count = int(input("Please, type the iterations count: "))
        self.send_iterations_count()
        print("I am worked")

    def cycle(self):
        while self.iterations_count == 0:
            time.sleep(1)
        print("Cycle end!")

    def send_iterations_count(self):
        for client in self.others:
            try:
                conn = rpyc.connect("localhost", client)
                # conn.root.change_iterations_count(self.iterationsCount)
            except Exception:
                print("")
                print("Host unavailable ", client)
                print("")
                return
            try:
                conn.root.update_data(self.iterations_count, self.iterations_size, self.current_iteration)
            except Exception:
                print("")
                print("Exception change_iterations_count ", self.iterations_count)
                print("")

    def update_data(self, iterCount, iterSize, currentIteration):
        print("Update")
        if self.t1.isAlive:
            self.t1.join()

        print("")
        print("I update my data ", iterCount, iterSize, currentIteration)

        self.iterations_count = iterCount
        self.iterations_size = iterSize
        self.current_iteration = currentIteration

        # self.size = self.server.get_clients_count()
        # self.rank = self.server.get_rank()

        self.start()

    def start(self):
        if self.isStart:
            return
        self.isStart = True
        print("I am start!")

    def on_received(self, text):
        mes = text.split(' ')
        name = "[" + self.name + "]"
        if mes[0] == name:
            return
        self.received_pi.append(float(mes[1]))

if __name__ == "__main__":
    cc = Client()