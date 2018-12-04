# encoding=utf-8

import requests
import os
import datetime
import ujson
import time
import math
import sys
import traceback


class QingTing:
    def __init__(self, channel_id, current_date_str=None):
        self.channel_id = channel_id
        self.download_dir = os.path.dirname(__file__)
        self.current_time = datetime.datetime.now() - datetime.timedelta(days=1)
        self.current_date_str = current_date_str if current_date_str else self.current_time.strftime('%Y%m%d')
        self.headers = {
            'Origin': 'http://www.qingting.fm',
            'Referer': 'http://www.qingting.fm/radios/' + channel_id,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
            'Host': 'i.qingting.fm',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        self.main()

    def main(self):
        channel_name = self.get_channel_name()
        if not channel_name:
            print u'当前电台未获取'
            return
        channel_file_path = os.path.join(self.download_dir, channel_name)
        if not os.path.exists(channel_file_path):
            os.makedirs(channel_file_path)
        date_file_path = os.path.join(channel_file_path, self.current_date_str)
        if not os.path.exists(date_file_path):
            os.makedirs(date_file_path)
        programs_list = self.get_programs_list()
        for index, program in enumerate(programs_list):
            program_name = program.get('name')
            broadcasters = program.get('broadcasters')
            start_time = program.get('start_time').split(' ')[-1].replace(':', '')
            end_time = program.get('end_time').split(' ')[-1].replace(':', '')
            self.download_programs(program_name, broadcasters, start_time, end_time, date_file_path, index)

    def get_channel_name(self):
        url = r'http://i.qingting.fm/wapi/channels/%s' % self.channel_id
        response = requests.get(url, headers=self.headers)
        if str(response.status_code) == '200':
            data = ujson.loads(response.text)
            name = data.get('data').get('name')
            return name
        else:
            return None

    def get_programs_list(self):
        url = r'http://i.qingting.fm/wapi/channels/%s/programs/date/%s' \
              % (self.channel_id, self.current_date_str)
        response = requests.get(url)
        data = ujson.loads(response.text)
        channel_list = data.get('data')
        return channel_list

    def download_programs(self, program_name, broadcasters, start_time, end_time, date_file_path, index):
        index += 1
        try:
            url = r'http://lcache.qingting.fm/cache/%s/%s/%s_%s_%s_%s_24_0.aac' \
                  % (self.current_date_str, self.channel_id, self.channel_id, self.current_date_str, start_time, end_time)
            if broadcasters:
                if len(broadcasters) == 1:
                    broadcasters_str = broadcasters[0]
                else:
                    broadcasters_str = '&'.join([broadcaster for broadcaster in broadcasters])
            else:
                broadcasters_str = ''
            if broadcasters_str:
                file_name = '%s_%s_%s_%s_%s_%s.aac' % (index, program_name, broadcasters_str, self.current_date_str, start_time, end_time)
            else:
                file_name = '%s_%s_%s_%s_%s.aac' % (index, program_name, self.current_date_str, start_time, end_time)
            file_path = os.path.join(date_file_path, file_name)
            audio_response = requests.get(url, stream=True)
            all_file_size = int(audio_response.headers['content-length'])
            if os.path.exists(file_path):
                current_file_size = os.path.getsize(file_path)
                if current_file_size != all_file_size:
                    os.remove(file_path)
                else:
                    return
            with open(file_path, 'ab') as f:
                print u'当前正在下载节目：%s' % file_name
                file_size = 0
                for block in audio_response.iter_content(chunk_size=1024):
                    if block:
                        f.write(block)
                        f.flush()
                        file_size += 1024
                        QingTing.download_bar(all_file_size, file_size)
                print u'下载完成'
        except Exception as e:
            print traceback.format_exc(e)

    @classmethod
    def convert_storage_read(cls, bytes_content):
        unit = 1024
        bytes_content = int(bytes_content)
        if bytes_content < unit:
            return '%.2f bytes' % bytes_content
        elif unit <= bytes_content < math.pow(unit, 2):
            return '%.2f kb' % (bytes_content / unit)
        elif math.pow(unit, 2) <= bytes_content < math.pow(unit, 3):
            return '%.2f mb' % (bytes_content / math.pow(unit, 2))
        else:
            return '%.2f gb' % (bytes_content / math.pow(unit, 3))

    @classmethod
    def download_bar(cls, file_all_size, file_current_size):
        download_flag = u'|'
        not_download_flag = u'·'
        percent = int(float(file_current_size) / file_all_size * 10)
        percent_bar_str = u'%s%s' % (download_flag * percent, not_download_flag * (10 - percent))
        download_percent = round((float(file_current_size) / file_all_size) * 100, 2)
        info_str = u'%s - %s%% | total_size: %s | download_size: %s' % (
            percent_bar_str,
            download_percent,
            QingTing.convert_storage_read(file_all_size),
            QingTing.convert_storage_read(file_current_size),
        )
        sys.stdout.write('\r' + info_str)


def convert_date_format(date_str):
    date_format = datetime.datetime.strptime(date_str, '%Y%m%d')
    return date_format


def download_date_programs(channel_id, days=None, start_date=None, end_date=None):
    if start_date and end_date:
        sd = convert_date_format(start_date)
        ed = convert_date_format(end_date)
        days = int((ed - sd).days) + 1
        for i in range(days):
            download_date = sd + datetime.timedelta(days=i)
            download_date_str = download_date.strftime('%Y%m%d')
            print u'当前正在下载：%s' % download_date_str
            QingTing(channel_id, download_date_str)
    elif start_date and days:
        sd = convert_date_format(start_date)
        days = int(days) + 1
        for i in range(days):
            download_date = sd + datetime.timedelta(days=i)
            download_date_str = download_date.strftime('%Y%m%d')
            print u'当前正在下载：%s' % download_date_str
            QingTing(channel_id, download_date_str)
    elif end_date and days:
        ed = convert_date_format(end_date)
        days = int(days) + 1
        for i in range(days):
            download_date = ed - datetime.timedelta(days=i)
            download_date_str = download_date.strftime('%Y%m%d')
            print u'当前正在下载：%s' % download_date_str
            QingTing(channel_id, download_date_str)


if __name__ == '__main__':
    pass