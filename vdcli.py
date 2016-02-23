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


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--quality', default='720p', help='Quality: 720p, 480p, 360p')
    parser.add_argument('url', help='video url on youku, tudou, letv, sohu, acfun, bilibili, iqiyi')
    args = parser.parse_args()

    video_parser = get_parser(args.url)
    video_parser.videoLink = args.url
    video_parser.videoType = QUALITY[args.quality]
    urlList = video_parser.chaseUrl()

    if urlList['stat'] == 0:
        if len(urlList['msg']) == 1:
            frag = urlList['msg']
        else:
            count = 0
            frag = []
            for url in urlList['msg']:
                count += 1
                frag.append('Fragment %s: %s' % (count, url))
        print('\n'.join(frag))
