from django.http import HttpResponseForbidden


def verify_request(func):
    """
    verify user request
    """

    def wrapper(request):
        if not request.POST.get('uid', ''):
            return HttpResponseForbidden()
        return func(request)

    return wrapper


