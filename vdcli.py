#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import argparse
import subprocess
import os
import os.path
import shutil
import tempfile
from urllib import urlretrieve

from progressbar import ProgressBar, Percentage, Bar, FileTransferSpeed, Timer

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


def download_file(url, title, info=None):
    def download_process(count, bsize, tsize):
        if pbar.start_time is None:
            pbar.start(tsize + bsize - tsize % bsize)
        dsize = count * bsize
        pbar.update(dsize if dsize < tsize else tsize)

    pbar = ProgressBar(
        widgets=['[%s]' % info, Percentage(), Bar(), Timer(), ' ', FileTransferSpeed()],
    )
    tmpfile, header = urlretrieve(url, reporthook=download_process)
    pbar.finish()
    tmp_dir = os.path.dirname(tmpfile)
    ext = os.path.splitext(tmpfile)[1]
    outfile = os.path.join(tmp_dir, title + ext)
    shutil.copyfile(tmpfile, outfile)
    return outfile

if __name__ == '__main__':
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
        dfiles = []
        title = 'title'
        total = len(urls)
        tl = len(str(total))
        tfmt = '%%0%dd' % tl
        for x in range(total):
            if args.no_download:
                print((tfmt + ': %s') % (x + 1, urls[x]))
                continue
            filename = download_file(
                urls[x],
                title=('%s.' + tfmt + '.part') % (title, x + 1),
                info=(tfmt + '/%s') % (x + 1, total),
            )
            dfiles.append(filename)
        if dfiles:
            ext = os.path.splitext(dfiles[0])[1]
            outfile = title + ext
            if len(dfiles) == 1:
                shutil.move(dfiles[0], outfile)
                print('Save as %s' % outfile)
            else:
                ftmp = tempfile.NamedTemporaryFile(prefix=title, delete=False)
                tmp_name = ftmp.name
                ftmp.write('\n'.join(['file "%s"' % df for df in dfiles]))
                ftmp.close()
                merge = ['ffmpeg']
                merge.append('-f concat')
                merge.append('-i %s' % tmp_name)
                merge.append('-c copy')
                merge.append(outfile)
                ret = subprocess.call(merge)
                if ret == 0:
                    os.remove(tmp_name)
                    for df in dfiles:
                        os.remove(df)
                    print('Save as %s' % outfile)
                else:
                    print('FFMPEG error: ' + ' '.join(merge))
                    print('Video part:', dfiles)
