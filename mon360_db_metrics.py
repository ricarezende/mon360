#!/usr/bin/env python3
import base64
import cx_Oracle
import math
import mon360_env as env
import os
import psutil
import re
import time
from datetime import datetime

def get_db_sessions(v_OutputFile, connection, ORASID):
    start_time = datetime.now()
    print('Getting DB_SESSIONS metric')
    v_curtime = time.time()
    # Get User sessions on database
    v_query= """SELECT USERNAME, COUNT(*)
               FROM V$SESSION
               WHERE USERNAME NOT IN ('SYS', 'SYSTEM', 'DBSNMP', 'OUTLN', 'MDSYS', 'ORDSYS', 'ORDPLUGINS', 'CTXSYS', 'DSSYS', 'PERFSTAT',
                                      'WKPROXY', 'WKSYS', 'XDB', 'ODM', 'ODM_MTR', 'OLAPSYS', 'TRACESVR',
                                      'REPADMINAURORA$ORB$UNAUTHENTICATED', 'AURORA$JIS$UTILITY$', 'OSE$HTTP$ADMIN', 'SCOTT', 'HR', 'OE',
                                      'PM', 'SH', 'QS', 'QS_ES', 'QS_WS', 'QS_OS', 'QS_CB', 'QS_CS', 'QS_ADM', 'QS_CBADM',
                                      'SECURITY_AUDIT', 'SYSMAN','ORACLE_OCM', 'TSMSYS', 'WMSYS', 'ANONYMOUS', 'APEX_INSTANCE_ADMIN_USER',
                                      'APEX_LISTENER', 'APEX_PUBLIC_USER', 'APEX_REST_PUBLIC_USER', 'APEX_180100', 'APPQOSSYS', 'AUDSYS',
                                      'DBSFWUSER', 'DIP', 'DVF', 'DVSYS', 'FLOWS_FILES', 'GGSYS', 'GSMADMIN_INTERNAL', 'GSMCATUSER',
                                      'GSMUSER', 'LBACSYS', 'MDDATA','OJVMSYS', 'ORDDATA', 'REMOTE_SCHEDULER_AGENT', 'SI_INFORMTN_SCHEMA',
                                      'SPATIAL_CSW_ADMIN_USR', 'SYSBACKUP', 'SYSDG', 'SYSKM', 'SYSRAC', 'SYS$UMF', 'USUTCP01', 'XS$NULL',
                                      'GSMCATUSER', 'SPATIAL_CSW_ADMIN_USR', 'SYS$UMF')
               GROUP BY USERNAME
               ORDER BY USERNAME"""
    cursor = connection.cursor()
    cursor.execute(v_query)
    v_sessions = []
    v_sessions = cursor.fetchall()
    v_total_sess = 0
    for j in range(len(v_sessions)):
        v_OutputFile.write('DB_SESSIONS,CUSTOMER=' + env.CUSTOMER + ',HOSTNAME=' + env.HOSTNAME + ',DATABASE=' + ORASID + ',SCHEMA=' + v_sessions[j][0] + ' VALUE=' + str(v_sessions[j][1]) + ' ' + str(math.ceil(v_curtime)) + '\n')
        v_total_sess = v_total_sess + v_sessions[j][1]
    v_OutputFile.write('DB_SESSIONS,CUSTOMER=' + env.CUSTOMER + ',HOSTNAME=' + env.HOSTNAME + ',DATABASE=' + ORASID + ',SCHEMA=ALL VALUE=' + str(v_total_sess) + ' ' + str(math.ceil(v_curtime)) + '\n')
    end_time = datetime.now()
    print('    Complete: {}'.format(end_time - start_time))

def get_db_size(v_OutputFile, connection, ORASID):
    start_time = datetime.now()
    print('Getting DB_SIZE metric')
    v_curtime = time.time()
    # Get database size by schema, excluding Oracle internal ones
    v_query= """SELECT OWNER, SUM(BYTES) BYTES
               FROM DBA_SEGMENTS
               WHERE OWNER NOT IN ('SYS', 'SYSTEM', 'DBSNMP', 'OUTLN', 'MDSYS', 'ORDSYS', 'ORDPLUGINS', 'CTXSYS',
                                   'DSSYS', 'PERFSTAT', 'WKPROXY', 'WKSYS', 'XDB', 'ODM', 'ODM_MTR', 'OLAPSYS',
                                   'TRACESVR', 'REPADMINAURORA$ORB$UNAUTHENTICATED', 'AURORA$JIS$UTILITY$',
                                   'OSE$HTTP$ADMIN', 'SCOTT', 'HR', 'OE', 'PM', 'SH', 'QS', 'QS_ES', 'QS_WS',
                                   'QS_OS', 'QS_CB', 'QS_CS', 'QS_ADM', 'QS_CBADM', 'SECURITY_AUDIT', 'SYSMAN',
                                   'ORACLE_OCM', 'TSMSYS', 'WMSYS', 'ANONYMOUS', 'APEX_INSTANCE_ADMIN_USER',
                                   'APEX_LISTENER', 'APEX_PUBLIC_USER', 'APEX_REST_PUBLIC_USER', 'APEX_180100',
                                   'APPQOSSYS', 'AUDSYS', 'DBSFWUSER', 'DIP', 'DVF', 'DVSYS', 'FLOWS_FILES',
                                   'GGSYS', 'GSMADMIN_INTERNAL', 'GSMCATUSER', 'GSMUSER', 'LBACSYS', 'MDDATA',
                                   'OJVMSYS', 'ORDDATA', 'REMOTE_SCHEDULER_AGENT', 'SI_INFORMTN_SCHEMA',
                                   'SPATIAL_CSW_ADMIN_USR', 'SYSBACKUP', 'SYSDG', 'SYSKM', 'SYSRAC', 'SYS$UMF',
                                   'USUTCP01', 'XS$NULL', 'GSMCATUSER', 'SPATIAL_CSW_ADMIN_USR', 'SYS$UMF')
               GROUP BY OWNER
               ORDER BY OWNER"""
    cursor = connection.cursor()
    cursor.execute(v_query)
    v_db_size = []
    v_db_size = cursor.fetchall()
    for j in range(len(v_db_size)):
        v_OutputFile.write('DB_SIZE,CUSTOMER=' + env.CUSTOMER + ',HOSTNAME=' + env.HOSTNAME + ',DATABASE=' + ORASID + ',SCHEMA=' + v_db_size[j][0] + ' VALUE=' + str(v_db_size[j][1]) + ' ' + str(math.ceil(v_curtime)) + '\n')
    # Get full database size
    v_query= """SELECT SUM(BYTES) BYTES
               FROM DBA_SEGMENTS"""
    cursor = connection.cursor()
    cursor.execute(v_query)
    v_db_size = []
    v_db_size = cursor.fetchall()[0][0]
    v_OutputFile.write('DB_SIZE,CUSTOMER=' + env.CUSTOMER + ',HOSTNAME=' + env.HOSTNAME + ',DATABASE=' + ORASID + ',SCHEMA=ALL VALUE=' + str(v_db_size) + ' ' + str(math.ceil(v_curtime)) + '\n')
    end_time = datetime.now()
    print('    Complete: {}'.format(end_time - start_time))

def get_tbs_size(v_OutputFile, connection, ORASID):
    start_time = datetime.now()
    print('Getting DB_TBSSIZE metric')
    v_curtime = time.time()
    # Get tablespaces size along with free space and used percentage
    v_query= """SELECT DF.TABLESPACE_NAME, DF.BYTES, FS.BYTES FREE, ROUND(((DF.BYTES-FS.BYTES)/DF.BYTES)*100,2) PCT_USED
                  FROM (SELECT TABLESPACE_NAME, SUM(BYTES) BYTES
                          FROM DBA_DATA_FILES
                          WHERE TABLESPACE_NAME NOT IN (SELECT TABLESPACE_NAME
                                                          FROM DBA_TABLESPACES
                                                          WHERE CONTENTS IN ('UNDO', 'TEMPORARY'))
                          GROUP BY TABLESPACE_NAME) DF
                  JOIN (SELECT TABLESPACE_NAME, SUM(BYTES) BYTES, MAX(BYTES) LARGEST
                          FROM DBA_FREE_SPACE
                          GROUP BY TABLESPACE_NAME) FS
                    ON DF.TABLESPACE_NAME = FS.TABLESPACE_NAME
                  ORDER BY 1"""
    cursor = connection.cursor()
    cursor.execute(v_query)
    v_tbs_size = []
    v_tbs_size = cursor.fetchall()
    for j in range(len(v_tbs_size)):
        v_OutputFile.write('DB_TBSSIZE,CUSTOMER=' + env.CUSTOMER + ',HOSTNAME=' + env.HOSTNAME + ',DATABASE=' + ORASID + ',TBS_NAME=' + str(v_tbs_size[j][0]) + ',TOTAL=' + str(v_tbs_size[j][1]) + ',FREE=' + str(v_tbs_size[j][2]) + ' PCT_USED=' + str(v_tbs_size[j][3]) + ' ' + str(math.ceil(v_curtime)) + '\n')
    end_time = datetime.now()
    print('    Complete: {}'.format(end_time - start_time))

def main(v_OutputFile, v_runtime):
    ORACLEDBSID = []
    ORACLEDBUSR = []
    ORACLEDBPWD = []
    ORACLEDBSID = env.ORACLEDBSID.split(",")
    ORACLEDBUSR = env.ORACLEDBUSR.split(",")
    ORACLEDBPWD = env.ORACLEDBPWD.split(",")
    for i in range(len(ORACLEDBSID)):
        connection = None
        conn_str = env.ORACLEDBSERVER + ":" + env.ORACLEDBPORT + "/" + ORACLEDBSID[i]
        usrpwd = base64.b64decode(str(ORACLEDBPWD[i]).replace("b", "").replace("'", ""))
        try:
            connection = cx_Oracle.connect(ORACLEDBUSR[i], usrpwd, conn_str, encoding='UTF-8')
            get_db_sessions(v_OutputFile, connection, ORACLEDBSID[i])
            if v_runtime[11:13] == "00" or v_runtime[11:13] == "30":
                get_db_size(v_OutputFile, connection, ORACLEDBSID[i])
                get_tbs_size(v_OutputFile, connection, ORACLEDBSID[i])
        except cx_Oracle.Error as error:
            print(error)
        finally:
            if connection:
                connection.close()
