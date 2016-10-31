import threading

response = None
def user_input():
    global response
    response = input("Do you wish to reconnect? ")


def t_print():
    print("123213")

user = threading.Thread(target=user_input)
user.daemon = True
user.start()
user.join()

t1 = threading.Thread(target=user_input)
t1.daemon = True
t1.start()
t1.join()

if response is None:
    print ('Exiting')
else:
    print ('As you wish')