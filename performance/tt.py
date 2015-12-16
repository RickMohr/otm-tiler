import os
import sys
from requests_futures.sessions import FuturesSession
from time import time, sleep

n_trials = 5

def restart_tiler():
    os.system(' vagrant ssh tiler -c "sudo service otm-tiler restart >/dev/null" 2>&1 >/dev/null')
    sleep(10)

def fetch(host, instance_id, x_min, x_max, y_min, y_max):
    session = FuturesSession()

    def get_urls():
        url_recipe  = '{host}/tile/{buster}/database/otm/table/treemap_mapfeature/{zoom}/{x}/{y}.{format}?instance_id={instance_id}'
        #url_recipe += '&restrict=%5B%22Plot%22%5D&q=%7B%22mapFeature.updated_at%22%3A%7B%22MIN%22%3A%222010-12-16%2000%3A00%3A00%22%2C%22MAX%22%3A%222015-12-16%2023%3A59%3A59%22%7D%7D'

        params = {
            'host': host,
            'instance_id': instance_id,
            'buster': int(time()),
            'zoom': 11
        }
        urls = []

        def make_urls(format):
            for x in range(x_min, x_max + 1):
                for y in range(y_min, y_max + 1):
                    urls.append(url_recipe.format(format=format, x=x, y=y, **params))

        make_urls('grid.json')
        make_urls('png')
        return urls


    def write(s):
        sys.stdout.write(s)
        sys.stdout.flush()

    def time_requests():
        urls = get_urls()
        print('Requesting %s tiles like %s' % (len(urls), urls[0]))
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


#fetch('http://localhost:4000', 21, 348, 354, 816, 819)
fetch('https://d1j3wq1j1c7z22.cloudfront.net', 21, 348, 354, 816, 819)  # staging

