import threading
import time

def hello():
    print("hello, Timer")


t = threading.Timer(2, hello)
t.start()