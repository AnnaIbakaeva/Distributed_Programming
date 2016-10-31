__author__ = 'Anna'
from rpyc import Service, async
from rpyc.utils.server import ThreadedServer


class RegisterService(Service):
    def on_connect(self):
        self.client = None

    def on_disconnect(self):
        if self.client:
            self.client.exposed_logout()

    def exposed_login(self, client):
        if self.client:
            raise ValueError("already logged in")
        else:
            self.client = client
            print("I login")

    def exposed_change_iterations_count(self, iterCount):
        self.client.iterationsCount = iterCount

if __name__ == "__main__":
    t = ThreadedServer(RegisterService, port = 19913)
    t.start()