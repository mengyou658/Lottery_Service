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
import sys
import time
import re
import json
import Util.DateUtil as DU
import demjson


crawser_url = "http://www.cp098.com/pk10/getHistoryData?count=1&t=0.5354527991439386"

class Crawser(object):
    def __init__(self):
        super(Crawser, self).__init__()

    #判断是否需要抓取
    def judge_need_crawser(self):
        return 1

    def crawser_index(self):
        DBC.CreateTableHistoryIfNotEXist()
        if self.judge_need_crawser() == 1 :
            result = NM.web_getcontent(crawser_url)
            sss = json.loads(result)
            rows = sss['rows']
            row = rows[0]

            time = row['lotteryTime'][:16]
            numbers = str(row['n1']) + ',' + str(row['n2']) + ',' + str(row['n3']) + ',' + str(row['n4']) + ',' + str(
                row['n5']) + ',' + str(row['n6']) + ',' + str(row['n7']) + ',' + str(row['n8']) + ',' + str(
                row['n9']) + ',' + str(row['n10'])
            qishu = row['termNum']

            sql = "INSERT INTO {0} ({1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}) VALUES ( \
            '{13}','{14}','{15}','{16}','{17}','{18}','{19}','{20}','{21}','{22}','{23}','{24}');".format( \
                CF.HISTAB, CF.HISQI, CF.HISTIME, CF.HISN1, CF.HISN2, CF.HISN3, CF.HISN4, CF.HISN5,CF.HISN6, CF.HISN7, CF.HISN8, CF.HISN9, CF.HISN10, \
                qishu, time, str(row['n1']), str(row['n2']), str(row['n3']), str(row['n4']), str(row['n5']), str(row['n6']), str(row['n7']), str(row['n8']), str(row['n9']),str(row['n10']))
            DBM.maka_do_sql(sql)
            
            time.sleep(1)
            yc =Yuce.Yuce()
            yc.startYuce()

            DBC.CreateTableTongjiIfNotEXist()
            cm = CalculateManager.CalculateManager()
            cm.calculate()
            json = demjson.encode(cm.results)
            sql = "DELETE FROM {0}.{1} WHERE {2} > 0;".format(CF.Database, CF.TJTAB, CF.TJQI)
            DBM.maka_do_sql(sql)
            sql = "INSERT INTO {0}.{1} ({2},{3}) VALUES ('{4}','{5}');".format(CF.Database, CF.TJTAB, CF.TJQI, CF.TJRS,
                                                                               qishu, json)
            DBM.maka_do_sql(sql)