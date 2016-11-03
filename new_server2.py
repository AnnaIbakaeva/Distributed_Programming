from __future__ import with_statement
from rpyc import Service, async
from rpyc.utils.server import ThreadedServer
from threading import RLock

clients = set()


class ClientToken(object):
    def __init__(self, name, send_pi, update_data):
        self.name = name
        self.state = False
        self.callback_send_pi = send_pi
        self.callback_update_data = update_data
        print("* Hello %s *" % (self.name))
        self.count = 0
        clients.add(self)

        print("")
        print("All clients:")
        for c in clients:
            print(c.name)

    def exposed_send_pi(self, message):
        if self.state:
            raise ValueError("User token is stale")
        self.broadcast("[%s] %s" % (self.name, message))

    def exposed_update_data(self, iterCount, iterSize, curIter):
        print("exposed_update_data")
        if self.state:
            raise ValueError("User token is stale")
        self.broadcast_update_data(iterCount, iterSize, curIter)

    def exposed_logout(self):
        if self.state:
            return
        self.state = True
        self.callback_send_pi = None
        self.callback_update_data = None
        clients.discard(self)
        print("* Goodbye %s *" % (self.name,))

    def broadcast(self, text):
        for client in clients:
            try:
                client.callback_send_pi(text)
                # print("I send ", text, " to ", client.name, " count = ", self.count)
            except:
                print("EXCEPTION broadcast")

    def broadcast_update_data(self, iterCount, iterSize, curIter):
        for client in clients:
            try:
                client.callback_update_data(iterCount, iterSize, curIter)
                # print("I send ", text, " to ", client.name, " count = ", self.count)
                # self.count += 1
            except:
                print("EXCEPTION broadcast_update_data")

    def exposed_get_clients_count(self):
        return len(clients)

    def exposed_get_active_clients_count(self):
        count = 0
        for client in clients:
            if not client.state:
                count += 1
        return count

    def exposed_get_rank(self):
        i = 0
        for client in clients:
            if client == self:
                return i
            i += 1
        raise ValueError("CLIENT NOT FOUND")


class RegisterService(Service):
    def on_connect(self):
        self.client = None

    def on_disconnect(self):
        if self.client:
            self.client.exposed_logout()

    def exposed_login(self, username, send_pi, update_data):
        if self.client and not self.client.state:
            raise ValueError("already logged in")
        else:
            self.client = ClientToken(username, async(send_pi), async(update_data))
            return self.client


if __name__ == "__main__":
    t = ThreadedServer(RegisterService, port = 19913)
    t.start()

