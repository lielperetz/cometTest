import sys
import urllib.request
from queue import Queue
from urllib.parse import urlparse, urljoin
from html.parser import HTMLParser


class WikiScrapper(HTMLParser):
    def __init__(self, content, filter_func=None):
        self._links = set()

        self._filter_func = filter_func

        super().__init__()
        super().feed(content)

    @property
    def links(self):
        return self._links

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return

        for key, value in attrs:
            if key != "href":
                continue

            if self._filter_func and not self._filter_func(value):
                break

            self._links.add(value)
            break


def generate_original_link(wiki_url):
    parsed_url = urlparse(wiki_url)
    return parsed_url.path


def get_links_from_url(url, filter_func=None):
    with urllib.request.urlopen(url) as response:
        # Decoding the result into str
        source = response.read().decode("utf-8", errors='ignore')
        return extract_links(source, filter_func)


def extract_links(content, filter_func=None):
    parser = WikiScrapper(content, filter_func)
    return parser.links


def is_wiki_page(link):
    if not link.startswith("/wiki/"):
        return False

    if ":" in link:
        return False

    return True


def join_url(wiki_url, link):
    return urljoin(wiki_url, link)


def find_and_print_link_back(q, results):
    while not q.empty():
        url = q.get()
        url_links = get_links_from_url(url)
        if len(url_links):
            results.append(url)
            print(url)


def main(wiki_url):
    if wiki_url.find("/wiki/") == -1:
        print('Please run with wiki page')
        return

    original_link = generate_original_link(wiki_url)
    filter_self_link = lambda x: x == original_link
    all_links_in_original_link = get_links_from_url(wiki_url, is_wiki_page)

    queue_wiki_link_back = Queue()
    for link in all_links_in_original_link:
        if filter_self_link(link):
            continue
        url = join_url(wiki_url, link)
        queue_wiki_link_back.put(url)

    find_and_print_link_back(queue_wiki_link_back, [])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Use this command: %s <wikiLInk>' % sys.argv[0])
    main(sys.argv[1])