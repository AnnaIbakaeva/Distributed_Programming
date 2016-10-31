__author__ = 'Anna'
import rpyc
import time
import threading


class Client(object):
    def __init__(self):
        self.conn = None
        self.others = [19912]
        self.my_port = 19913
        self.isStart = False
        self.iterationsCount = 0

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
            self.conn.root.login(self)
            print("I login")
        except ValueError:
            print("")
            print("EXCEPTION self.conn.root.login!!!")
            print("")
            self.conn.close()
            self.conn = None

    def user_input(self):
        self.iterationsCount = int(input("Please, type the iterations count: "))
        self.send_iterations_count()
        print("I am worked")

    def cycle(self):
        while self.iterationsCount == 0:
            # print("self.iterationsCount = ", self.iterationsCount)
            time.sleep(1)
        print("Cycle end!")

    def send_iterations_count(self):
        for client in self.others:
            try:
                conn = rpyc.connect("localhost", client)
                conn.root.change_iterations_count(self.iterationsCount)
            except Exception:
                print("")
                print("Host unavailable ", client)
                print("")
                return
            # try:
            #     conn.root.change_iterations_count(self.iterationsCount)
            # except Exception:
            #     print("")
            #     print("Exception change_iterations_count ", self.iterationsCount)
            #     print("")

    def start(self):
        if self.isStart:
            return
        self.isStart = True

        print("I am start!")

if __name__ == "__main__":
    cc = Client()