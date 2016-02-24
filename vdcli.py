#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from Module import youkuClass
from Module import tudouClass
from Module import sohuClass
from Module import letvClass
from Module import bilibiliClass
from Module import acfunClass
from Module import iqiyiClass


QUALITY = {'720p': 's', '480p': 'h', '360p': 'n'}


def get_parser(url):
    if 'youku' in url:
        getClass = youkuClass.ChaseYouku()
    elif 'sohu' in url:
        getClass = sohuClass.ChaseSohu()
    elif 'letv' in url:
        getClass = letvClass.ChaseLetv()
    elif 'tudou' in url and 'acfun' not in url:
        getClass = tudouClass.ChaseTudou()
    elif 'bilibili' in url:
        getClass = bilibiliClass.ChaseBilibili()
    elif 'acfun' in url:
        getClass = acfunClass.ChaseAcfun()
    elif 'iqiyi' in url:
        getClass = iqiyiClass.ChaseIqiyi()
    else:
        raise NotImplementedError(url)
    return getClass


def download_file(url, title=None):
    def download_process(count, bsize, tsize):
        if pbar.start_time is None:
            pbar.start(tsize)
        dsize = count * bsize
        pbar.update(dsize if dsize < tsize else tsize)

    import shutil
    from urllib import urlretrieve

    from progressbar import ProgressBar, Percentage, Bar, FileTransferSpeed, Timer

    pbar = ProgressBar(
        widgets=[Percentage(), Bar(), Timer(), ' ', FileTransferSpeed()],
    )
    tmp, header = urlretrieve(url, reporthook=download_process)
    pbar.finish()
    ext = header.getsubtype().split('-')[1]
    filename = '%s.%s' % (title, ext)
    shutil.copyfile(tmp, filename)
    return filename


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quality', default='720p', help='Quality: 720p, 480p, 360p')
    parser.add_argument('--no-download', action='store_true', help='No download, only show download url.')
    parser.add_argument('url', help='video url on youku, tudou, letv, sohu, acfun, bilibili, iqiyi')
    args = parser.parse_args()

    video_parser = get_parser(args.url)
    video_parser.videoLink = args.url
    video_parser.videoType = QUALITY[args.quality]
    urlList = video_parser.chaseUrl()

    if urlList['stat'] == 0 and urlList['msg']:
        urls = urlList['msg']
        for x in range(len(urls)):
            if args.no_download:
                print('%s: %s' % (x, urls[x]))
                continue
            filename = download_file(urls[x])
            print('Save as %s' % filename)
