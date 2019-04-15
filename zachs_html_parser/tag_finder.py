import re

from zachs_html_parser import _objects

def a(html):
    list_of_anchors = []
    for x in re.findall(r'<a.+</a>', html):
        list_of_anchors.append(_objects._a(x))
    return list_of_anchors
