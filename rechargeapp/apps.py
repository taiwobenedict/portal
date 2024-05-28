from django.apps import AppConfig
from threading import Thread
import time, queue, random

class TestThread(Thread):

    def run(self):
        print("running thread")

class RechargeappConfig(AppConfig):
    name = 'rechargeapp'

    # def ready(self) -> None:
    #     print("hello there")
    #     from rechargeapp.models import AirtimeTopup, MtnDataShare, CableRecharge

    #     def feed_thread():
    #         while True:
    #             time.sleep(random.randint(5, 10))
    #             #get the last pending record and process
    #             fetch_records = AirtimeTopup.objects.filter(status="QUEUE")
    #             if fetch_records.exists():
    #                 for r in fetch_records:
    #                     print(r.ordernumber, r.status)
    #                     time.sleep(2)
    #                     print("...waiting")
    #                     time.sleep(8)
    #                     r.status = "SUCCESS"
    #                     r.save()
    #                     print(r.ordernumber, r.status)

    #     t = Thread(target=feed_thread, args = (), daemon=True)
    #     t.setDaemon(True)
    #     t.start()


    #     return super().ready()