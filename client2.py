import rpyc
import time

class ChatClient(object):
    def __init__(self):
        self.conn = None
        self.user = None
        self.name = "Ann"
        self.pi = 0
        self.received_pi = 0
        self.rank = 1
        self.n = 10000
        self.size = 2
        self.result_pi = 0
        self.messages_counter = 0

        self.on_connect()

        for i in range(self.rank, self.n, self.size):
            # print("")
            # print("My pi = ",self.pi)
            self.pi += pow(-1, i) / (2 * i + 1)
            self.on_send()

        self.result_pi = self.pi + self.received_pi
        print("Result pi = ", self.result_pi * 4)

        count = self.n / self.size

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
            self.user = self.conn.root.login(self.name, self.on_message)
        except ValueError:
            self.conn.close()
            self.conn = None
            return


    #
    # called by the reactor whenever the connection has something to say
    #
    def bg_server(self, source = None, cond = None):
        if self.conn:
            self.conn.poll_all()
            return True
        else:
            return False

    #
    # sends the current message
    #
    def on_send(self):
        text = self.pi
        print("")
        print("Send ", text)
        self.user.say(text)

    #
    # called by the server, with the text to append to the GUI
    def on_message(self, text):
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


if __name__ == "__main__":
    cc = ChatClient()






