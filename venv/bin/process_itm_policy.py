#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
from sub_common import *

# 设置log
logger = get_logger("process.log")

# 特定参数
TABLE_NAME = "ITM_POLICY"

# 设置全局变量
write_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
global counter
counter = 0
global agent_to_ip_dict
global agent_to_host_dict
global group_to_agent_dict

def main():
    logger.info("Begin to insert to table:%s.",TABLE_NAME)

    delsql = "delete from {0} ".format(TABLE_NAME)
    clean_db(delsql);

    query_sit()

    logger.info("Success insert records:%s.",counter)

def query_sit():
    agent_to_ip_dict()
    agent_to_host_dict()

    conn = get_conn()
    cursor = conn.cursor();
    sqlStr = "select SITNAME,DISTRIBUTION from ITM_SIT_INFO";
    cursor.execute(sqlStr); #循环所有situation
    rows_sit = cursor.fetchall()
    if len(rows_sit) > 0:
        for i in range(len(rows_sit)):

            #根据situation名字进行丰富
            sitname = str(rows_sit[i][0])
            sqlStr = "select SIT_DESC,N_ComponentType,N_Component,N_SubComponent from ITM_SIT_ENRICH where SITNAME = \'{0}\'".format(
                sitname)
            cursor.execute(sqlStr)
            rows_enrich = cursor.fetchall()
            if len(rows_enrich) == 0:
                sit_desc = ''
                n_componenttype = ''
                n_component = ''
                n_subcomponent = ''
            elif len(rows_enrich) > 0:
                sit_desc = rows_enrich[0][0]
                n_componenttype = rows_enrich[0][1]
                n_component = rows_enrich[0][2]
                n_subcomponent = rows_enrich[0][3]

            #根据situation名字查找sit原始信息
            sitname = str(rows_sit[i][0])
            sqlStr = "select ISSTD,PDT,THRESHOLD,SEVERITY from ITM_SIT_INFO " \
                     "where SITNAME = \'{0}\'".format(sitname)
            cursor.execute(sqlStr)
            rows_enrich = cursor.fetchall()
            if len(rows_enrich) == 0:
                isstd = ''
                pdt = ''
                threshold = ''
                severity = ''
            elif len(rows_enrich) > 0:
                isstd = rows_enrich[0][0]
                pdt = rows_enrich[0][1]
                threshold = rows_enrich[0][2]
                severity = rows_enrich[0][3]

            #根据下发的组或者agent列表进行处理
            dist = str(rows_sit[i][1]).split(',')
            group_flag = str(rows_sit[i][1]).find(':')  #根据冒号判断是发到组还是Agent。 如果未找到，则值为-1
            if  group_flag != -1 : #situation直接下发到Agent的情况
                for agent in dist:
                    try:
                        ip_address = agent_to_ip_dict[agent]
                    except:
                        ip_address = ''

                    try:
                        host = agent_to_host_dict[agent]
                    except:
                        host = ''

                    appname = iptoapp(ip_address)
                    import_data(cursor,sitname,host,ip_address,agent,appname[0],sit_desc,n_componenttype,n_component,n_subcomponent,severity)

            elif group_flag == -1 : #situation下发到组的情况

                for group in dist:
                    try:
                        agent_list = group_to_agent(group)
                        pass
                    except:
                        print(sitname,group)
                        continue
                    for agent in agent_list :
                        try:
                            host = agent_to_host_dict[agent]  # 找到主机名
                        except:
                            host = ''
                        try:
                            ip_address = agent_to_ip_dict[agent]  # 找到IP
                        except:
                            ip_address = ''
                        appname = iptoapp(ip_address)  # 根据IP地址，查找应用系统信息

                        import_data(cursor,sitname, host, ip_address, agent, appname[0], sit_desc, n_componenttype, n_component,n_subcomponent,severity)
                        pass
    conn.commit()
    conn.close()

def import_data(cursor,sitname,host,ip_address,agent,appname,sit_desc,n_componenttype,n_component,n_subcomponent,severity):
    global counter
    sqlStr = "insert into {0}  (WRITE_TIME,APP_NAME,IP_ADDRESS,AGENT_NAME,HOSTNAME,SIT_NAME,SIT_DESC,COMPONENT_TYPE,COMPONENT,SUB_COMPONENT,SEVERITY)" \
             "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ".format(TABLE_NAME)
    cursor.execute(sqlStr,(write_time,appname,ip_address,agent,host,sitname,sit_desc,n_componenttype,n_component,n_subcomponent,severity))
    counter += 1

def iptoapp(ip_address):
    appname = ()
    conn = get_conn()
    cursor = conn.cursor();
    sqlStr = "select APP_NAME from ITM_IPTOAPP where IP_ADDRESS = '" + ip_address + "'"
    cursor.execute(sqlStr);
    rows_app = cursor.fetchall()
    if len(rows_app) > 0 : #如果找到了APP，则赋值
        appname = rows_app[0]
    elif len(rows_app) == 0: #如果没找到，则赋默认值
        appname = ('',)
    conn.close()
    return(appname)


def agent_to_ip_dict():
    global agent_to_ip_dict
    agent_to_ip_dict = {}
    conn = get_conn()
    cursor = conn.cursor();
    cursor.execute("select AGENT_NAME,IP_ADDRESS from ITM_AGENT_INFO where IP_ADDRESS != ''");
    rows = cursor.fetchall()
    agent_to_ip_dict = {}
    for row in rows:
        agent_to_ip_dict[row[0]] = row[1]
    conn.close()

def agent_to_host_dict():
    global agent_to_host_dict
    agent_to_host_dict = {}

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("select AGENT_NAME,HOSTNAME from ITM_AGENT_INFO where HOSTNAME != ''");
    rows = cursor.fetchall()
    agent_to_host_dict = {}
    for row in rows:
        agent_to_host_dict[row[0]] = row[1]
    conn.close()

def group_to_agent(group_name):
    conn = get_conn()
    cursor = conn.cursor();
    cursor.execute("select AGENT_NAME from ITM_GROUP_INFO where GROUP_NAME = %s",group_name);
    rows = cursor.fetchall()
    agent_list = []
    for row in rows:
        agent_list.append(row[0])
    conn.close()
    return (agent_list)

if __name__ == '__main__':
        main()