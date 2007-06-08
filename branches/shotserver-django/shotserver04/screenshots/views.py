from django.shortcuts import render_to_response
from shotserver04.screenshots.models import Screenshot


def screenshot_list(request):
    screenshot_list = Screenshot.objects.all()[:100]
    return render_to_response('screenshots/screenshot_list.html', locals())
