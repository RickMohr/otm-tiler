import os
import sys
from requests_futures.sessions import FuturesSession
from time import time, sleep

n_trials = 5

def restart_tiler():
    os.system(' vagrant ssh tiler -c "sudo service otm-tiler restart >/dev/null" 2>&1 >/dev/null')
    sleep(10)

def fetch(host, instance_id, x_min, x_max, y_min, y_max):
    url_recipe  = '{host}/tile/{buster}/table/treemap_mapfeature/{zoom}/{x}/{y}.{format}?instance_id={instance_id}'
    params = {
        'host': host,
        'instance_id': instance_id,
        'buster': int(time()),
        'zoom': 11
    }
    urls = []
    session = FuturesSession()

    def make_urls(format):
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                urls.append(url_recipe.format(format=format, x=x, y=y, **params))

    make_urls('grid.json')
    make_urls('png')

    print('Requesting %s tiles like %s' % (len(urls), urls[0]))

    def write(s):
        sys.stdout.write(s)
        sys.stdout.flush()

    def time_requests():
        restart_tiler()
        start = time()
        futures = [session.get(u) for u in urls]
        for url, future in zip(urls, futures):
            response = future.result()
            if response.status_code == 200:
                write('.')
            else:
                print("Got %s for %s" % (response.status_code, url))
        elapsed = time() - start
        print(' {:.1f}'.format(elapsed))
        return elapsed

    print('%s Trials (restarting tiler before each): ' % n_trials)
    times = [time_requests() for i in range(0, n_trials)]
    average = reduce(lambda x, y: x + y, times) / len(times)

    print('\nAverage: {:.1f} sec'.format(average))


fetch('http://localhost:4000', 21, 348, 354, 816, 819)
#fetch('https://d9nki18bdqr9e.cloudfront.net', 21, 348, 354, 816, 819)

