from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings
from django.contrib import messages

def internal_server_error(request):
    print("Did it get here in the first place")
    return render(request, "500.html")

def not_found_error(request, exception):
    return render(request, "404.html")

#restart the queue if any issues
from django.contrib.auth.decorators import login_required

@login_required(login_url=settings.LOGIN_URL)
def restart_pm2(request):
    if not request.user.is_superuser:
        return redirect(settings.LOGIN_URL)
    import os, shlex, subprocess
    from subprocess import Popen, PIPE
    cmd = "source /home/akravwsh/nodevenv/node-vbp4/14/bin/activate && cd /home/akravwsh/node-vbp4 && yarn pm2 restart 0"
    try:
        x = subprocess.check_output(cmd, shell=True)
        messages.success(request, x.decode().strip())
        return redirect("/")
    except Exception as e:
        # cmd = "ls -la && venv\\Scripts\\activate && python manage.py migrate"
        # x = subprocess.check_output(cmd, shell=True)
        messages.error(request, str(e))
        return redirect("/")


@login_required(login_url=settings.LOGIN_URL)
def update_scripts(request):
    if not request.user.is_superuser:
        return redirect(settings.LOGIN_URL)
    import os, shlex, subprocess
    from subprocess import Popen, PIPE
    cmd = "git pull origin main && python manage.py makemigrations && python manage.py migrate"
    try:
        x = subprocess.check_output(cmd, shell=True)
        messages.success(request, x.decode().strip() + "\n Restart the App to complete the update")
        return redirect("/")
    except Exception as e:
        messages.error(request, str(e))
        return redirect("/")

    # process = Popen(shlex.split(cmd), stdout=PIPE)
    # return HttpResponse((process.communicate())[0].strip())