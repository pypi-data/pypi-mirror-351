import argparse
import json
import re
import urllib.request

import lxml.html

PARSER = argparse.ArgumentParser(description='Get Ubuntu versioning information from Wikipedia.', epilog="@readwithai 📖 https://readwithai.substack.com/p/habits ⚡️ machine-aided reading ✒️")
PARSER.add_argument('--json', action='store_true', default=False)




def main():
    # fetch https://en.wikipedia.org/wiki/Ubuntu_version_history
    # use standard libary not requests

    args = PARSER.parse_args()
    url = "https://en.wikipedia.org/wiki/Ubuntu_version_history"
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')
    tree = lxml.html.fromstring(text)
    for x in tree.xpath("//h3"):
        text = x.xpath("text()")[0]
        m = re.search(r"Ubuntu (\d+\.\d+)((?: LTS)?) \(([^)]*)\)", text)
        if m is None:
            raise ValueError(text)
        version, lts_string, name = m.groups()
        adjective, animal = name.split()
        lts = bool(lts_string)
        if args.json:
            print(json.dumps(dict(version=version, name=adjective.lower(), is_lts=lts, full_name=name)))

        else:
            print(version, adjective.lower(), lts)
