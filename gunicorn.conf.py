bind = "0.0.0.0:8000"  #
workers = 3
user = "webapps"
group = "www-data"

limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
timeout = 30
keepalive = 2

accesslog = "/var/log/chesley_web/django/access.log"
errorlog = "/var/log/chesley_web/django/error.log"
