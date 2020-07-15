from django.http import HttpResponse


def haproxy_view(request):
    """Haproxy view
    :param request: Http request
    :return: plain text string 'ok'
    """
    content = 'ok'
    response = HttpResponse(content, content_type='text/plain')
    return response
