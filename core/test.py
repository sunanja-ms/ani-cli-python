from otakudesu import get_acefiles, getDownload
from krakenfiles import short_link


url = "https://otakudesu.best/episode/gnkkksrwokdk-episode-1-sub-indo/"

def test(url):
    all_stream = getDownload(url)
    return short_link(all_stream)


test1 = test(url)
print(test1)
