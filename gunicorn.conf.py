#import os
#import multiprocessing

#bind = 'unix:/home/indmerc/tinytaskers/task/task.sock'  # Use the default path for the .sock file
  # Bind Gunicorn to this host:port
#workers = multiprocessing.cpu_count() * 2 + 1  # Adjust the number of workers as needed
#timeout = 30  # Set a timeout (in seconds) for requests
#loglevel = "debug"  # Adjust log level as needed
#chdir='/home/indmerc/tinytaskers'
#pythonpath = os.path.join(chdir, 'myenv', 'bin', 'python')

#errorlog = "/home/indmerc/tinytaskers/logs/gunicorn_error.log"
#accesslog = "/home/indmerc/tinytaskers/logs/gunicorn_access.log"
import multiprocessing

#bind = "/home/indmerc/tinytaskers/task/task.sock"  # Path to your socket file
bind='0.0.0.0:10000'
# Number of workers, it should be (2 * number of CPU cores) + 1
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
