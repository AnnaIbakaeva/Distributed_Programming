from __future__ import with_statement
from rpyc import Service, async
from rpyc.utils.server import ThreadedServer
from threading import RLock


# broadcast_lock = RLock()
clients = set()


class ClientToken(object):
    def __init__(self, name, callback):
        self.name = name
        self.state = False
        self.callback = callback
        print("* Hello %s *" % (self.name))
        self.count = 0
        clients.add(self)

    def exposed_say(self, message):
        if self.state:
            raise ValueError("User token is stale")
        self.broadcast("[%s] %s" % (self.name, message))

    def exposed_logout(self):
        if self.state:
            return
        self.state = True
        self.callback = None
        clients.discard(self)
        print("* Goodbye %s *" % (self.name,))

    def broadcast(self, text):
        for client in clients:
            try:
                client.callback(text)
                print("I send ", text, " to ", client.name, " count = ", self.count)
                self.count += 1
            except:
                print("EXCEPTION")

    def exposed_get_clients_count(self):
        return len(clients)

    def exposed_get_active_clients_count(self):
        count = 0
        for client in clients:
            if client.state:
                count += 1
        return count

    def exposed_get_rank(self):
        for i in range(0, len(clients)):
            if clients[i] == self:
                return i
        return 99999


class RegisterService(Service):
    def on_connect(self):
        self.client = None

    def on_disconnect(self):
        if self.client:
            self.client.exposed_logout()

    def exposed_login(self, username, callback):
        if self.client and not self.client.state:
            raise ValueError("already logged in")
        else:
            self.client = ClientToken(username, async(callback))
            return self.client


if __name__ == "__main__":
    t = ThreadedServer(RegisterService, port = 19912)
    t.start()

