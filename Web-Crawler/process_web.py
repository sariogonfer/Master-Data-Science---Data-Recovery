from contextlib import contextmanager
from time import sleep
from queue import Queue, Full
from urllib.parse import urljoin
import _thread
import argparse
import signal
import re

import sys
import time

from bs4 import BeautifulSoup, SoupStrainer
import htmlmin
import requests

arg_parse = argparse.ArgumentParser()
arg_parse.add_argument('root_url', help='URL de la pagina desde donde ' \
                                        'empezar a procesar paginas.')
arg_parse.add_argument('--output', dest='output', action='store',
                       default=sys.stdout, help='Fichero de salida.')

MAX_QUEUE_SIZE = 100
THREAD_SLEEP_TIME = .5 # seconds
NUM_OF_THREAD = 1

_running = True

class NotValidPage(Exception):
    pass

def print_page(url, html, output):
    print(url, file=output)
    print(htmlmin.minify(html), file=output)

def get_nested_urls(html):
    for link in  BeautifulSoup(html, "html.parser",
            parse_only=SoupStrainer("a")):
        if link.has_attr('href'):
            yield link['href']

def get_page_content(url):
    try:
        resp = requests.get(url)
    except:
        raise NotValidPage
    return resp.text

def procces_url(q_urls, output=sys.stdout):
    url = q_urls.get()
    # print("Procesando: %s" % url)
    try:
        soup = get_page_content(url)
        print_page(url, soup, output)
        for nested_url in get_nested_urls(soup):
            try:
                nested_url = nested_url if re.match("^http[s]?://",
                        nested_url) else urljoin(url, nested_url)
                q_urls.put(nested_url, block=False)
            except Full:
                return True
    except NotValidPage:
        return True

@contextmanager
def output_context_manager(output):
    yield open(output, 'w') if isinstance(output, str) else output

def main(root_url, output=sys.stdout, num_of_thread = NUM_OF_THREAD,
         max_queue_size=MAX_QUEUE_SIZE, thread_sleep_time=THREAD_SLEEP_TIME):
    q_urls = Queue(max_queue_size)
    q_urls.put(root_url)
    with output_context_manager(output) as file_:
        while not q_urls.empty() and _running:
            _thread.start_new_thread(procces_url, (q_urls, ),
                                     dict(output=file_))
            time.sleep(thread_sleep_time)
    pass

if __name__ == "__main__":
    args = arg_parse.parse_args()
    def _stop(*_):
        global _running
        _running = False
    signal.signal(signal.SIGINT, _stop)
    main(args.root_url, output=args.output)
