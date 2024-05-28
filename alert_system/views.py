from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from alert_system.models import AlertSystem, UserReadAlert, TutorialNews


def process_read_alert(request, pk):
  alert = AlertSystem.objects.get(pk=pk)
  chk_if_read_alert = UserReadAlert.objects.filter(alert=alert, user=request.user)
  if len(chk_if_read_alert) > 0:
    chk_if_read_alert[0].read_count += 1
    chk_if_read_alert[0].save()
  else:
    UserReadAlert.objects.get_or_create(
      alert=alert, user=request.user 
    )

  return JsonResponse({"message": "User has read the alert"})


def tutorial_news(request):
  all_news = TutorialNews.objects.all()
  get_news = all_news.filter(pin_to_top=False)
  get_pinned_news = all_news.filter(pin_to_top=True)
  paginator = Paginator(get_news, 20)#show 20 per page
  page = request.GET.get('page')
  try:
    historys = paginator.page(page)
  except PageNotAnInteger:
    # If page is not an integer, deliver first page.
    historys = paginator.page(1)
  except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
    historys = paginator.page(paginator.num_pages)
  return render(request, 'tutorial_news/news.html', {'historys': historys, 'get_pinned_news': get_pinned_news})
