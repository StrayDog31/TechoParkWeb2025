from urllib.parse import parse_qs
from wsgiref.util import request_uri


def simple_wsgi_app(environ, start_response):
    get_params = parse_qs(environ.get('QUERY_STRING', ''))

    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    post_params = parse_qs(request_body.decode('utf-8'))

    status = '200 OK'
    headers = [('Content-type', 'text/plain; charset=utf-8')]

    response_body = [
        "Welcome to simple WSGI app!\n",
        f"Request URL: {request_uri(environ)}\n\n",
        "GET parameters:\n",
        *[f"{k}: {v}\n" for k, v in get_params.items()],
        "\nPOST parameters:\n",
        *[f"{k}: {v}\n" for k, v in post_params.items()],
    ]

    start_response(status, headers)
    return [line.encode('utf-8') for line in response_body]