import rpyc
from copy import deepcopy


class Client(object):
    def __init__(self):
        self.conn = None
        self.user = None
        self.name = "Kate"
        self.iterationsCount = 10000
        self.iterations_size = 10
        self.active_clients_count = 0
        self.isStart = False
        self.calculated_iterations = []

        self.my_pi = []

        self.received_pi = 0
        self.current_iteration = 0

        self.on_connect()

        self.update_iterations(self.iterationsCount)
        if self.current_iteration == 0:
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
        result_pi = 0
        for pi in self.my_pi:
            result_pi += pi
        print("My pi = ", result_pi)

        print("Received pi = ", self.received_pi)

        result_pi += self.received_pi
        print("Result pi = ", result_pi)
        print("Result 4*pi = ", result_pi*4)

    def calculate_pi(self):
        j = 0
        pi = 0
        for i in range(self.current_iteration, self.iterationsCount, self.size):
            if i in self.calculated_iterations:
                continue
            print("i = ", i)
            pi += pow(-1, i) / (2 * i + 1)
            self.calculated_iterations.append(i)
            j += 1
            if j == self.iterations_size:
                break
        self.my_pi.append(pi)
        self.current_iteration += self.size * j

    def on_send(self):
        send_pi = 0
        for p in self.my_pi:
            send_pi += p
        print("Last temp pi = ", self.my_pi[len(self.my_pi)-1])
        print("Send ", send_pi)
        self.user.send_pi(send_pi, self.calculated_iterations)

    def on_received(self, text, calc_iters):
        mes = text.split(' ')
        name = "[" + self.name + "]"
        if mes[0] == name:
            return
        print("I received ", float(mes[1]), "; last received calc iters = ", calc_iters)
        self.received_pi = float(mes[1])
        self.calculated_iterations.extend(calc_iters)
        # print("")
        # print("self.calculated_iterations:")
        # for i in self.calculated_iterations:
        #     print(i, " ")
        # print("")

    def update_iterations(self, unsolved):
        print("")
        print("Unsolved = ", unsolved)

        last_active_clients_count = self.user.get_active_clients_count()

        if not (self.active_clients_count == last_active_clients_count):
            self.active_clients_count = last_active_clients_count
            print("Iterations count = ", self.iterationsCount)
            self.user.update_data(self.iterationsCount, self.iterations_size, self.current_iteration)

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

        self.size = self.user.get_active_clients_count()
        self.rank = self.user.get_rank()

        print("Rank = ", self.rank)
        self.current_iteration = currentIteration + self.rank

        self.start()

if __name__ == "__main__":
    cc = Client()







