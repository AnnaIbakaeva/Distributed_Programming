import threading

response = None
def user_input():
    global response
    response = input("Do you wish to reconnect? ")

user = threading.Thread(target=user_input)
user.daemon = True
user.start()
user.join()
if response is None:
    print ('Exiting')
else:
    print ('As you wish')