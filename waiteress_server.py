from waitress import serve
from ask_yakovlev.wsgi import application

if __name__ == '__main__':
    serve(
        application,
        host='0.0.0.0',
        port=8000,
        threads=4,
        url_scheme='https',
        ident=None,
        ipv6=False,
        cleanup_interval=30,
        channel_timeout=60,
        connection_limit=1000,
        asyncore_loop_timeout=1,
        send_bytes=18000,
        outbuf_overflow=364544,
        inbuf_overflow=364544,
        unix_socket=None,
        unix_socket_perms='600',
        trusted_proxy=None,
        trusted_proxy_count=1,
        trusted_proxy_headers={'x-forwarded-for'},
        clear_untrusted_proxy_headers=True,
        log_untrusted_proxy_headers=False
    )