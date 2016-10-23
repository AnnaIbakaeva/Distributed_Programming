# import rpyc
# import socket
#
#
# class MyService(rpyc.Service):
#     n = 100
#     rank = 0
#     current_port = 18861
#     # all_ips = [18861, 18862, 18863]
#     available_ips = [18862]
#     size = 3
#     current_pi = 0
#     received_pi = 0
#
#             #self.current_ip = socket.gethostbyname(socket.gethostname())
#
#     def on_connect(self):
#         print ("On connect")
#
#     def on_disconnect(self):
#         pass
#
#     # def exposed_check_available_ips(self):
#     #     for ip in self.all_ips:
#     #         try:
#     #             c = rpyc.connect("localhost", ip)
#     #             self.available_ips.append(ip)
#     #         except:
#     #             print (ip, " is unavailable!")
#     #     self.size = len(self.available_ips)
#
#     def exposed_recalculate_rank_and_residue(self):
#         print("Available ips: ", self.available_ips)
#         print("Current ", self.current_port)
#         self.rank = 0 #self.available_ips.index(self.current_port)
#         residue = self.n % self.size
#         k = self.n / self.size
#         if (residue > 0 & self.rank - residue < 0):
#             k += 1
#
#     def exposed_calculate_pi(self):
#         for i in range(self.rank, self.n, self.size):
#             self.current_pi += pow(-1, i) / (2 * i + 1)
#             print("I calculate pi = ", self.current_pi)
#             self.exposed_send_part_sum_pi()
#         return self.current_pi
#
#     def exposed_send_part_sum_pi(self):
#          for ip in self.available_ips:
#             try:
#                 c = rpyc.connect("localhost", ip)
#                 c.root.received_part_sum_pi(self.current_pi)
#                 print("I send pi = ", self.current_pi, " to ", ip)
#             except:
#                 print (ip, " is unavailable!")
#
#     def exposed_received_part_sum_pi(self, pi):
#         print("My pi = ", self.current_pi)
#         print("My received pi before sum ", self.received_pi)
#         print("I received ", pi)
#         self.received_pi += pi
#         print ("Summed! My current received pi = ", self.received_pi)
#
#     def exposed_get_received_pi(self):
#         return self.received_pi
#
#
# if __name__ == "__main__":
#     from rpyc.utils.server import ThreadedServer
#     t = ThreadedServer(MyService, port=18861)
#     t.start()


from __future__ import with_statement
from rpyc import Service, async
from rpyc.utils.server import ThreadedServer
from threading import RLock


broadcast_lock = RLock()
tokens = set()


class UserToken(object):
    def __init__(self, name, callback):
        self.name = name
        self.stale = False
        self.callback = callback
        self.broadcast("* Hello %s *" % (self.name))
        tokens.add(self)

    def exposed_say(self, message):
        if self.stale:
            raise ValueError("User token is stale")
        self.broadcast("[%s] %s" % (self.name, message))

    def exposed_logout(self):
        if self.stale:
            return
        self.stale = True
        self.callback = None
        tokens.discard(self)
        self.broadcast("* Goodbye %s *" % (self.name,))

    def broadcast(self, text):
        global tokens
        stale = set()
        with broadcast_lock:
            for tok in tokens:
                try:
                    tok.callback(text)
                except:
                    stale.add(tok)
            tokens -= stale


class ChatService(Service):
    def on_connect(self):
        self.token = None

    def on_disconnect(self):
        if self.token:
            self.token.exposed_logout()

    def exposed_login(self, username, callback):
        if self.token and not self.token.stale:
            raise ValueError("already logged in")
        else:
            self.token = UserToken(username, async(callback))
            return self.token


if __name__ == "__main__":
    t = ThreadedServer(ChatService, port = 19912)
    t.start()

