#!/usr/bin/env python3
import math
import mon360_env as env
import os
import psutil
import re
import time
from datetime import datetime

def get_cpu(v_OutputFile):
    start_time = datetime.now()
    print('Getting CPU metric')
    v_curtime = time.time()
    v_cpupct = psutil.cpu_percent()
    v_OutputFile.write('SRV_HEATH,CUSTOMER=' + env.CUSTOMER + ',HOSTNAME=' + env.HOSTNAME + ',RESOURCE=CPU_PCT_USED VALUE=' + str(v_cpupct) + ' ' + str(math.ceil(v_curtime)) + '\n')
    end_time = datetime.now()
    print('    Complete: {}'.format(end_time - start_time))

def get_mem(v_OutputFile):
    start_time = datetime.now()
    print('Getting MEM metric')
    v_curtime = time.time()
    v_mempct = psutil.virtual_memory()[2]
    v_OutputFile.write('SRV_HEATH,CUSTOMER=' + env.CUSTOMER + ',HOSTNAME=' + env.HOSTNAME + ',RESOURCE=MEM_PCT_USED VALUE=' + str(v_mempct) + ' ' + str(math.ceil(v_curtime)) + '\n')
    end_time = datetime.now()
    print('    Complete: {}'.format(end_time - start_time))

def get_disk(v_OutputFile):
    start_time = datetime.now()
    print('Getting DISK metric')
    v_curtime = time.time()
    for i in range(len(psutil.disk_partitions())):
        v_disk = psutil.disk_partitions()[i][1]
        v_diskpct = psutil.disk_usage(psutil.disk_partitions()[i][1])[3]
        v_OutputFile.write('SRV_HEATH,CUSTOMER=' + env.CUSTOMER + ',HOSTNAME=' + env.HOSTNAME + ',RESOURCE=DISK:' + v_disk.replace(" ", "_") + ' VALUE=' + str(v_diskpct) + ' ' + str(math.ceil(v_curtime)) + '\n')
    end_time = datetime.now()
    print('    Complete: {}'.format(end_time - start_time))

def get_latency(v_OutputFile):
    start_time = datetime.now()
    print('Getting LATENCY metric')
    v_curtime = time.time()
    cmd = 'nmap -Pn -T4 -n -p 22 -d3 ' + env.INFLUXDBSERVER + ' |grep "TIMING STATS"'
    stream = os.popen(cmd)
    v_latency = stream.readlines()
    v_latency = str(v_latency[0]).split()
    v_latency = re.findall(r"[-+]?\d*\.\d+|\d+", str(v_latency[2]))
    v_laten = float(str(v_latency[0]))
    v_OutputFile.write('SRV_HEATH,CUSTOMER=' + env.CUSTOMER + ',HOSTNAME=' + env.HOSTNAME + ',RESOURCE=LATENCY VALUE=' + str(v_laten) + ' ' + str(math.ceil(v_curtime)) + '\n')
    end_time = datetime.now()
    print('    Complete: {}'.format(end_time - start_time))

def main(v_OutputFile, v_runtime):
    get_cpu(v_OutputFile)
    get_mem(v_OutputFile)
    get_latency(v_OutputFile)
    if v_runtime[11:13] == "00" or v_runtime[11:13] == "30":
        get_disk(v_OutputFile)
