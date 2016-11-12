from __future__ import with_statement
from rpyc import Service, async
from rpyc.utils.server import ThreadedServer


clients = []


class ClientToken(object):
    def __init__(self, name, send_pi, update_data):
        self.name = name
        self.stale = False
        self.callback_send_pi = send_pi
        self.callback_update_data = update_data
        print("* Hello %s *" % (self.name))
        self.count = 0
        clients.append(self)

        print("")
        print("All clients:")
        for c in clients:
            print(c.name)

    def exposed_send_pi(self, message, curIter):
        if self.stale:
            raise ValueError("User token is stale")
        self.broadcast_send_pi(self.name, message, curIter)

    def exposed_update_data(self, iterCount, iterSize, curIter):
        if self.stale:
            raise ValueError("User token is stale")
        self.broadcast_update_data(iterCount, iterSize, curIter)

    def exposed_logout(self):
        if self.stale:
            return
        self.stale = True
        self.callback_send_pi = None
        self.callback_update_data = None
        #clients.remove(self)
        self.update_client_stale()
        print("* Goodbye %s *" % (self.name))

    def update_client_stale(self):
        for c in clients:
            if c.name == self.name:
                c.stale = self.stale

    def broadcast_send_pi(self, name, pi, curIter):
        for client in clients:
            try:
                client.callback_send_pi(name, pi, curIter)
            except:
                print("EXCEPTION broadcast")

    def broadcast_update_data(self, iterCount, iterSize, curIter):
        for client in clients:
            try:
                client.callback_update_data(self.name, iterCount, iterSize, curIter)
                # print("I send ", text, " to ", client.name, " count = ", self.count)
                # self.count += 1
            except:
                print("EXCEPTION broadcast_update_data")

    def exposed_get_active_clients_count(self):
        count = 0
        for client in clients:
            if not client.stale:
                count += 1
        return count

    def exposed_get_clients_count(self):
        return len(clients)

    def exposed_get_rank(self):
        i = 0
        for client in clients:
            if client.name == self.name:
                return i
            i += 1
        raise ValueError("CLIENT NOT FOUND")

    def exposed_get_received_data_count(self):
        count = 0
        for client in clients:
            count += client.callback_get_received_data_count()
        return count

    def exposed_get_wait_me_clients_count(self):
        count = 0
        for client in clients:
            if not client.stale and client.callback_is_waiting():
                count += 1
        return count


class RegisterService(Service):
    def on_connect(self):
        self.client = None

    def on_disconnect(self):
        if self.client:
            self.client.exposed_logout()

    def exposed_login(self, username, send_pi, update_data):
        if self.client and not self.client.stale:
            raise ValueError("already logged in")
        else:
            self.client = ClientToken(username, async(send_pi), async(update_data))
            return self.client


if __name__ == "__main__":
    t = ThreadedServer(RegisterService, port=19912)
    t.start()

