#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import datetime
from sub_common import *

# 设置log
logger = get_logger("process.log")

# 特定参数
TABLE_NAME = "UMP_MO_OS"
TABLE_APP_INFO = "APP_INFO"

# 设置全局变量
write_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
global counter


def main():
    logger.info("Begin to insert to table:%s",TABLE_NAME)
    delsql = "delete from {0} ".format(TABLE_NAME)
    clean_db(delsql)
    logger.info("Table %s has been cleaned!",TABLE_NAME)
    process_import()
    logger.info("Success insert records:%s.",counter)

    logger.info("Begin to update to table:%s", TABLE_NAME)
    post_process_oracle()
    post_process_weblogic()
    post_process_tuxedo()
    logger.info("Success insert records:%s.", counter)



def process_import():
    global counter
    counter = 0
    conn = get_conn()
    cursor = conn.cursor();
    sql = '''select 
                PHYSICIP,AGENTID,SYSCODE,APPFULLNAME,USETYPE,HOSTNAME,SYSTEMVERSION,IP,FLOATIP,MAPPINGIP,APPLICATIONTYPE,DISASTERTYPE 
            from 
                CMDB_OS_RAW
            where 
                USETYPE='生产机' 
        '''
    cursor.execute(sql);
    rows = cursor.fetchall()
    if len(rows) > 0:
        i = 0
        for i in range(len(rows)):
            ip_address = str(rows[i][0])
            agentid = str(rows[i][1])
            app_code = str(rows[i][2])
            app_name = str(rows[i][3])
            usetype = str(rows[i][4])
            hostname = str(rows[i][5])
            systemversion = str(rows[i][6])
            ip = str(rows[i][7])
            floatip = str(rows[i][8])
            mappingip = str(rows[i][9])
            applicationtype = str(rows[i][10])
            disastertype = str(rows[i][11])

            keyword = ip_address
            volume_type = ""
            is_oracle = 0
            is_weblogic = 0
            is_ism = 0
            is_tuxedo = 0
            is_vcs = 0
            if systemversion.find("SUSE"):
                os_type = "SUSE"
            elif systemversion.find("RED HAT"):
                os_type = "REDHAT"
            elif systemversion.find("AIX"):
                os_type = "AIX"
            elif systemversion.find("HP-UX"):
                os_type = "HP-UX"
            elif systemversion.find("Microsoft"):
                os_type = "WINDOWS"
            else:
                os_type = "UNKNOWN"

            sql = '''insert into {0} (  WRITE_TIME,KEYWORD,IP_ADDRESS,AGENTID,APP_CODE,APP_NAME,USETYPE,
            HOSTNAME,OS_TYPE,VERSION,IP_ALL,VIP,MAPPINGIP,VOLUME_TYPE,APPLICATIONTYPE,DISASTERTYPE,
            IS_ORACLE,IS_WEBLOGIC,IS_ASM,IS_TUXEDO,IS_VCS) values( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )
            '''.format(TABLE_NAME)
            cursor.execute(sql,(write_time,keyword,ip_address,agentid,app_code,app_name,usetype,hostname,os_type,systemversion,ip,
                                floatip,mappingip,volume_type,applicationtype,disastertype,is_oracle,is_weblogic,is_ism,is_tuxedo,
                                is_vcs))
            counter += 1
    conn.commit()
    conn.close()

def post_process_oracle():
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select AGENTID FROM ump.CMDB_ORACLESID_RAW where USETYPE='生产机'"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        agentid = row[0]
        sql = "update {0} set IS_ORACLE=TRUE where AGENTID='{1}'".format(TABLE_NAME,agentid)
        cursor.execute(sql)
    conn.commit()
    conn.close()

def post_process_weblogic():
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select AGENTID FROM ump.CMDB_WEBLOGIC_RAW where USETYPE='生产机'"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        agentid = row[0]
        sql = "update {0} set IS_WEBLOGIC=TRUE where AGENTID='{1}'".format(TABLE_NAME,agentid)
        cursor.execute(sql)
    conn.commit()
    conn.close()

def post_process_tuxedo():
    conn = get_conn()
    cursor = conn.cursor()
    sql = "select AGENTID FROM ump.CMDB_TUXEDO_RAW where USETYPE='生产机'"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        agentid = row[0]
        sql = "update {0} set IS_TUXEDO=TRUE where AGENTID='{1}'".format(TABLE_NAME,agentid)
        cursor.execute(sql)
    conn.commit()
    conn.close()

if __name__ == '__main__':
        main()