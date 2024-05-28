import queue, threading, time, random

# q = queue.Queue()

# def add_to_queue(data):
#     q.put(data)
#     t = threading.Thread(target=feed_thread, args = (q,), daemon=True)
#     t.setDaemon(True)
#     t.start()

# def feed_thread(q):
#     while not q.empty():
#         print('starting thread')
#         time.sleep(10)
#         #get the last pending record and process
#         print(q.get())
#         print('put something')


