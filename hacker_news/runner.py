from scrapy.cmdline import execute
execute(['scrapy', 'crawl', 'clean'])


def test:

    with open('xpaths.json') as data_file:
        dict_source = json.load(data_file)[1]

    for k, v in dict_source.items():
        print(k, v)
        if k and v != "":
            print(response.xpath(v).extract())
