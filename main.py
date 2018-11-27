# encoding=utf-8

import argparse
from qingting import QingTing, download_date_programs

parser = argparse.ArgumentParser(description=u"下载蜻蜓FM电台节目，"
                                             u"目前蜻蜓FM保存电台节目时间大约为2个月，下载2个月之前的节目无效")
parser.add_argument("-c", "--channel", help=u"电台ID， 例如：20210885，不填写日期参数则默认下载前一天电台节目")
parser.add_argument("-d", "--date", help=u"电台日期， 例如：2018年1月1日记作20180101")
parser.add_argument("-s", "--startDate", help=u"开始日期， 例如：2018年1月1日记作20180101")
parser.add_argument("-e", "--endDate",  help=u"结束日期， 例如：2018年2月1日记作20180201")
parser.add_argument("-D", "--days",  help=u"日期区间， 例如：5，表示下载当前日期之前/之后5天的电台节目，"
                                          u"开始日期+日期区间表示开始日期后5天内的节目， "
                                          u"结束日期+日期区间表示结束日期前5天的内容")
args = parser.parse_args()

if args.channel:
    QingTing(channel_id=args.channel)
if args.channel and args.date:
    QingTing(channel_id=args.channel, current_date_str=args.date)
elif args.channel and args.startDate and args.endDate:
    download_date_programs(channel_id=args.channel, start_date=args.startDate, end_date=args.endDate)
elif args.channel and args.startDate and args.days:
    download_date_programs(channel_id=args.channel, start_date=args.startDate, days=args.days)
elif args.channel and args.endDate and args.days:
    download_date_programs(channel_id=args.channel, end_date=args.endDate, days=args.days)




