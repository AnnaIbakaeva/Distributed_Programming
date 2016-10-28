import rpyc
import time

class Information(object):
    def __init__(self):
        self.received_data = []
        self.client = None


class Client(object):
    def __init__(self):
        # init values
        self.conn = None
        self.user = None
        self.name = "Kate"
        self.iterationsCount = 10000
        self.iterations_size = 10

        self.my_pi = []

        self.pi = 0
        self.received_pi = 0
        self.result_pi = 0
        self.messages_counter = 0

        self.on_connect()

        self.size = self.user.get_clients_count()
        self.rank = self.user.get_rank()

        for i in range(0, self.iterationsCount):
            self.calculate_pi()

        # for i in range(self.rank, self.iterationsCount, self.size):
        #     print("")
        #     print("My pi = ",self.pi)
        #     self.pi += pow(-1, i) / (2 * i + 1)
        #     self.on_send()

        self.result_pi = self.pi + self.received_pi
        print("Result pi = ", self.result_pi * 4)

        count = self.iterationsCount / self.size
        while self.messages_counter < count:
            time.sleep(10)

        print(self.messages_counter, " = ", count)
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
            self.user = self.conn.root.login(self.name, self.on_received)
        except ValueError:
            self.conn.close()
            self.conn = None
            return

    def calculate_pi(self):
        pi = 0
        for i in range(0, self.iterations_size):
            pi += pow(-1, i) / (2 * i + 1)
        self.my_pi.append(pi)
        # self.on_send()

    def on_send(self):
        text = self.pi
        print("")
        print("Send ", text)
        self.user.say(text)

    def on_received(self, text):
        mes = text.split(' ')
        name = "[" + self.name + "]"
        if mes[0] == name:
            return
        print("")
        print ("Received: ", text)
        # print("My received pi = ", self.received_pi)
        self.received_pi = float(mes[1])
        # print("I summed receiving pi ", self.received_pi)
        self.result_pi = self.pi + self.received_pi
        # print("Result pi after receiving = ", self.result_pi * 4)
        self.messages_counter += 1
        print("Messages counter = ", self.messages_counter)

    def update_iterations(self, unsolved):
        activeClientsCount = self.user.get_active_clients_count()
        deltaIteration = unsolved / activeClientsCount
        self.iterationsCount += deltaIteration


if __name__ == "__main__":
    cc = Client()







