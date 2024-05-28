from django.apps import AppConfig
from threading import Thread
import time, queue, random

# class TestThread(Thread):

#     def run(self):
#         print("running thread")

class CrudeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crude'
    #TODO : LOG USER OUT FROM MULTIPLE DEVICES so write a middleware that check the session key and prevent double login

    # def ready(self) -> None:
    #     print("hello there")
    #     from transactions.models import Transactions
    #     from rechargeapp.views import ProcessAirtimePurchase, ProcessDataPurchase
    #     from rechargeapp.cable_view import ProcessCablePurchase
    #     from electricity.views import ProcessElectricityPurchase

    #     def feed_thread():
    #         while True:
    #             print("sleeping")
    #             time.sleep(random.randint(5, 10))
    #             #get the last pending record and process
    #             fetch_records = Transactions.objects.filter(status="QUEUE")
    #             if fetch_records.exists():
    #                 for index, r in enumerate(fetch_records):
    #                     delay = (index + 1) * 8
    #                     time.sleep(delay)
    #                     r.status = "PROCESSED"
    #                     r.save()
    #                     #check the bill_type and run the code portion for it
    #                     if r.bill_type == "AIRTIME":
    #                         print("Airtime...picked")
    #                         ProcessAirtimePurchase(r.id)
    #                         print("Airtime...done")
    #                         time.sleep(random.randint(2, 8))
    #                         continue
    #                     elif r.bill_type == "DATA":
    #                         print("Data...picked")
    #                         ProcessDataPurchase(r.id)
    #                         print("Data...done")
    #                         time.sleep(random.randint(2, 8))
    #                         continue
    #                     elif r.bill_type == "CABLE":
    #                         print("Cable...picked")
    #                         ProcessCablePurchase(r.id)
    #                         print("Cable...done")
    #                         time.sleep(random.randint(2, 8))
    #                         continue
    #                     elif r.bill_type == "ELECTRICITY":
    #                         print("Electricity...picked")
    #                         ProcessElectricityPurchase(r.id)
    #                         print("Electricity...done")
    #                         time.sleep(random.randint(2, 8))
    #                         continue

    #     t = Thread(target=feed_thread, args = (), daemon=True)
    #     t.setDaemon(True)
    #     t.start()


        # return super().ready()