from django.http import HttpResponse

def begin(request):
    return HttpResponse('hello')