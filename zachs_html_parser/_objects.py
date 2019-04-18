import re


class _a(object):
    def __init__(self, anchor_string):
        self.text = anchor_string

    def string(self):
        return str(self.text)

    def __str__(self):
        return self.string()

    def href(self):
        # findall returns a list which should have only one object, so [0]
        try:
            href = re.findall(r"""href=(["'])(.+?)\1""", self.text)[0][1]
            return href
        except IndexError:
            print(f'\nhref not found for {self.string()}, ignoring\n')

    def desc(self):
        regex = re.findall(r'>.*?</a>', self.string())[0]
        if len(regex) > 5:
            return regex[1:-4]
