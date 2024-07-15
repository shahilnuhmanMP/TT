

import multiprocessing

bind='0.0.0.0:8000'

workers = multiprocessing.cpu_count() * 2 + 1
# Worker class for handling requests
worker_class = "sync"
# Number of threads per worker
threads = 1
# Maximum number of requests a worker will process before restarting
max_requests = 1000
# Maximum number of requests a worker will process before graceful restart
max_requests_jitter = 100
# Timeout for handling a request
timeout = 30
# Keep alive connections
keepalive = 2
# Access log file
accesslog = "/home/indmerc/tinytaskers/logs/gunicorn_access.log"
# Error log file
errorlog = "/home/indmerc/tinytaskers/logs/gunicorn_error.log"
# Log level
loglevel = "info"
