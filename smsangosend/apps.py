from django.apps import AppConfig
from threading import Thread
import time, queue, random

class SmsangosendConfig(AppConfig):
    name = 'smsangosend'

    # def ready(self) -> None:
    #     print("hello there")
    #     from smsangosend.models import SmsangoSendSMS
    #     from smsangosend.tasks import send_bulk_sms_bg, SendScheduledSMS_bg

    #     def feed_sms_thread():
    #         while True:
    #             print("sleeping == 0000000")
    #             time.sleep(random.randint(5, 10))
    #             #get the last pending record and process
    #             fetch_records = SmsangoSendSMS.objects.filter(status="QUEUE")
    #             if fetch_records.exists():
    #                 for r in fetch_records:
    #                     #check the bill_type and run the code portion for it
    #                     if r.scheduledsms is False:
    #                         time.sleep(random.randint(30, 40))
    #                         print("...waiting")
    #                         send_bulk_sms_bg(r.user.id, r.sender, r.recipients, r.numcount, r.messagecontent, r.smsroute, r.pages)
    #                         time.sleep(random.randint(20, 30))
    #                     else:
    #                         time.sleep(random.randint(5, 10))
    #                         SendScheduledSMS_bg(r.user.id, r.sender, r.recipients, r.numcount, r.messagecontent, r.smsroute, r.totalsms, 0.0, r.scheduleidnum, r.pages)
    #                         time.sleep(random.randint(5, 10))


    #     t = Thread(target=feed_sms_thread, args = (), daemon=True)
    #     t.setDaemon(True)
    #     t.start()


    #     return super().ready()