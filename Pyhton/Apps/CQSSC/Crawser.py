#encoding:utf8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import Network.NetworkManager as NM
import Dao.MysqlDBManager as DBM

import Yuce as Yuce
import CalculateManager as CalculateManager
import MysqlDBConfig as CF
import DatabaseCreator as DBC
import time
import json
import Util.DateUtil as DU
import demjson

timeInset = 5
beginTime = '10:00'
endTime = '01:55'

crawser_url = "http://www.cp098.com/cqssc/getHistoryData?count=1&t=0.5354527991439386"

class Crawser(object):
    def __init__(self):
        super(Crawser, self).__init__()

    # 判断是否需要抓取
    def judge_need_crawser(self):

        current = time.time()
        current = float(current)
        x = time.localtime(current)
        x = time.strftime('%H%M', x)

        if int(x) < 1000 and int(x) > 160:
            print  '重庆时时彩 =======>  当前时间不需要抓取 -----'
            return 0

        sql = "select {0} from {1} order by {2} desc limit 1".format(CF.HISTIME, CF.HISTAB, CF.HISQI)
        result = DBM.maka_do_sql(sql)

        if not result :
            return 1

        if len(result) == 0:
            return 1

        lastTime = result[0][0]
        print  lastTime
        lastTimeSeconds = DU.date_to_time(lastTime)

        currentInset = timeInset
        if int(x) > 1000 and int(x) < 2200:
            currentInset = 10

        if current - lastTimeSeconds >= currentInset * 60:
            print '重庆时时彩 ***********需要抓取********** {0} {1} *****'.format(lastTimeSeconds, current)
            return 1

        return 0

    def crawser_index(self):

        print  '重庆时时彩 -----------> 开始抓取'

        if self.judge_need_crawser() == 1 :
            DBC.CreateTableHistoryIfNotEXist()
            result = NM.web_getcontent(crawser_url)

            if len(result) == 0:
                return


            sss = json.loads(result)
            rows = sss['rows']
            row = rows[0]

            shijian = row['lotteryTime'][:16]
            numbers = str(row['n1']) + ',' + str(row['n2']) + ',' + str(row['n3']) + ',' + str(row['n4']) + ',' + str(
                row['n5'])
            qishu = row['termNum']

            sql = "select {0} from {1} order by {0} desc limit 1".format(CF.HISQI, CF.HISTAB)
            result = DBM.maka_do_sql(sql)
            databaseQishu = '0'
            if len(result) > 0:
                databaseQishu = result[0][0]

            if qishu <= databaseQishu :
                print  '重庆时时彩 &&&&&&&&&&&&&&& 抓取的数据在数据库中已存在 &&&&&&&&&&&&&'
                return

            sql = "INSERT INTO {0} ({1},{2},{3},{4},{5},{6},{7}) VALUES ( \
                                    '{8}','{9}',{10},{11},{12},{13},{14});".format( \
                CF.HISTAB, CF.HISQI, CF.HISTIME, CF.HISN1, CF.HISN2, CF.HISN3, CF.HISN4, CF.HISN5, \
                qishu, shijian, str(row['n1']), str(row['n2']), str(row['n3']), str(row['n4']), str(row['n5']))
            DBM.maka_do_sql(sql)

            print  '重庆时时彩 ########## 插入SQL:'+sql+' ############'

            time.sleep(1)
            print '重庆时时彩 -------进入预测-------'
            yc = Yuce.Yuce()
            yc.startYuce()

            print '重庆时时彩 -------进入统计-------'
            DBC.CreateTableTongjiIfNotEXist()
            cm = CalculateManager.CalculateManager()
            cm.calculate()

            print '重庆时时彩 -------删除原统计数据---------'
            jso = demjson.encode(cm.results)
            sql = "DELETE FROM {0} WHERE {1} > 0;".format(CF.TJTAB, CF.TJQI)
            DBM.maka_do_sql(sql)

            print '重庆时时彩 ^^^^^^^^^^^插入新的统计^^^^^^^^^^^'
            sql = "INSERT INTO {0} ({1},{2}) VALUES ('{3}','{4}');".format(CF.TJTAB, CF.TJQI, CF.TJRS,
                                                                               qishu, jso)
            DBM.maka_do_sql(sql)

