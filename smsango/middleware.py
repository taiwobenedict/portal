from django.utils import timezone
from urllib import response
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.auth.signals import user_logged_in
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
User = get_user_model()


class OnlyOneUserMiddleware:
    """
    Middleware to ensure that a logged-in user only has one session active.
    Will kick out any previous session. 
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        response = self.get_response(request)
        return response

    def process_request(self, request):
        if isinstance(request.user, User):
            user = request.user
            # print(request.META['HTTP_REFERER'], request.META['HTTP_HOST'])
            current_key = request.session.session_key
            if hasattr(request.user, 'userprofile'):
                active_key = request.user.userprofile.session_key
                if active_key != current_key:
                    Session.objects.filter(session_key=active_key).delete()
                    request.user.userprofile.session_key = current_key
                    request.user.userprofile.save()
            else:
                user.userprofile.session_key = current_key
                user.userprofile.save()

# class RedirectUserWithInsufficientFunds:
#     """
#         Redirect users with insufficient funds
#     """
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # self.process_request(request)
#         response = self.get_response(request)
#         return response

#     def process_view(self, request):
#         if isinstance(request.user, User):
#             user = request.user
#             print(request.path)
#             if any(respo in str(request.path) for respo in ["customer/recharge/", "customer/electricity/electricityPurchase", "customer/rechargeCardPrinting/"]:
#                 return redirect

