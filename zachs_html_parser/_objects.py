import re


class _href(object):
    def __init__(self, href_string):
        self.text = href_string

    # [6:-1] because the first 6 characters are href=" and the last character is "
    def get_link(self):
        return self.text[6:-1]


class _a(object):
    def __init__(self, anchor_string):
        self.text = anchor_string

    def string(self):
        return str(self.text)

    def __str__(self):
        return self.string()

    def href(self):
        # findall returns a list which should have only one object, so [0]
        raw_href = re.findall(r'href=\s?".+?"', self.text)[0]
        href_class = _href(raw_href)
        return href_class.get_link()
