#import pygtk
#pygtk.require('2.0')
#import gtk
#import gobject
import rpyc


class ChatClient(object):
    def __init__(self):
        self.conn = None
        self.user = None
        self.text_input = ""

        self.on_connect()

        while(True):
            print("Hello! Please, type the text!")
            self.text_input = input()
            self.on_send()

    def disconnect(self):
        if self.conn:
            try:
                self.user.logout()
            except:
                pass
            self.conn.close()
            self.user = None
            self.conn = None

    def on_close(self, widget):
        self.disconnect()

    #
    # connect/disconnect logic
    #
    def on_connect(self):
        try:
            self.conn = rpyc.connect("localhost", 19912)
        except Exception:
            self.conn = None
            return

        try:
            self.user = self.conn.root.login("spam", "bacon", self.on_message)
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
        text = self.text_input
        print("Send ", text)
        #self.txt_input.set_text("")
        if text.strip():
            self.user.say(text)

    #
    # called by the server, with the text to append to the GUI
    #
    def on_message(self, text):
        print ("Received: ", text)
        self.text_input = text
        #buf = self.txt_main.get_buffer()
        #buf.place_cursor(buf.get_end_iter())
        #buf.insert_at_cursor(text + "\n")


if __name__ == "__main__":
    cc = ChatClient()

