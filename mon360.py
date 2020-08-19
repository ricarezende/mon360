#!/usr/bin/env python3
import base64
import cx_Oracle
import fnmatch
import math
import mon360_env as env
import mon360_conf as conf
import mon360_os_metrics as os_metrics
import mon360_db_metrics as db_metrics
import os, signal
import psutil
import pyinputplus as pyinput
import re
import sys
import time
from datetime import datetime
from os import system, name
from paramiko import SSHClient
from scp import SCPClient

def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

def export_payload(v_runmode, v_payload):
    if v_runmode == "-dryrun":
        v_OutputFile = open(v_payload, 'r')
        Lines = v_OutputFile.readlines()[4:]
        v_OutputFile.close()
        for line in Lines:
            print(line.strip())
        os.rename('./' + v_payload, './backup/' + v_payload)
    else:
        start_time = datetime.now()
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(env.INFLUXDBSERVER, 22, env.INFLUXDBSRVUSR)
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(v_payload, '~/mon360/payload/.')
        end_time = datetime.now()
        print('Payload successfully sent to InfluxDB server: {}'.format(end_time - start_time))
        os.rename('./' + v_payload, './backup/' + v_payload)

def runServer(v_runtime, v_runmode):
    v_files_in_execution = []
    for v_live_files in os.listdir(str(os.getcwd())):
        if fnmatch.fnmatch(v_live_files, 'mon360.runServer.payloadfiles*.lst'):
            v_livefile = open(v_live_files, 'r')
            Lines = v_livefile.readlines()
            v_livefile.close()
            for line in Lines:
                v_files_in_execution.append(line)
    payload_path = str(os.getcwd() + '/payload')
    payload_files = os.listdir(payload_path)
    v_payloadfiles_in_this_execution_name = str('mon360.runServer.payloadfiles.' + v_runtime + '.lst')
    v_PayloadFiles = open(v_payloadfiles_in_this_execution_name, 'w')
    for f in payload_files:
        flag = 'N'
        for i in v_files_in_execution:
            if str(f).strip() == str(i).strip():
                flag = 'Y'
        if flag == 'N':
            v_PayloadFiles.write(f + '\n')
    v_PayloadFiles.close()
    v_PayloadFiles = open(v_payloadfiles_in_this_execution_name, 'r')
    v_payloadfiles_in_this_execution = v_PayloadFiles.readlines()
    v_PayloadFiles.close()
    if v_runmode == "-dryrun":
        for f in v_payloadfiles_in_this_execution:
            print(str('influx -import -path=./payload/' + str(f).strip() + ' -precision=s -database=MON360'))
    else:
        for f in v_payloadfiles_in_this_execution:
            os.system(str('influx -import -path=./payload/' + str(f).strip() + ' -precision=s -database=MON360'))
            os.rename('./payload/' + str(f).strip(), './backup/' + str(f).strip())
    os.remove(str('./' + v_payloadfiles_in_this_execution_name))

def help():
    clear()
    print("NAME")
    print("     mon360.py -- collects Operating System and Oracle database metrics and send to InfluxDB Database for Grafana dashboard")
    print()
    print("SYNOPSIS")
    print("     ./mon360.py [-server | -client | -help] [-run | -dryrun | -config]")
    print()
    print("DESCRIPTION")
    print("     mon360 is a program to provide a 360 degree monitoring tool using Open Source resources such as InfluxDB time-series database")
    print("     for data repository and Grafana for dashboard view.")
    print("     mon360 is in continous construction to include new metrics for the monitoring purposes.")
    print()
    print("     mon360 was developed by Ricardo Rezende and source code can be found in GitHub.")
    print()
    print("     The arguments are as follows:")
    print()
    print("   Argument 1:")
    print()
    print("     -server   mon360 execution on monitoring server side. Collected data will be loaded into InfluxDB DB.")
    print()
    print("     -client   mon360 execution on monitored server side. Data will be collected and sent to InfluDB DB Server.")
    print()
    print("     -help     this help screen. :)")
    print()
    print("     -stop     terminates all running mon360 deamon.")
    print()
    print("   Argument 2:")
    print()
    print("     -run      the actual execution of the program. If Argument 1 = -client: it collects data and sends to InfluxDB DB Server.")
    print("                                                    If Argument 1 = -server: it loads collected data into InfluxDB DB.")
    print()
    print("     -dryrun   a test execution. If Argument 1 = -client: it collects data and print payload on screen,")
    print("                                                          but do not send it to InfluxDB DB Server.")
    print("                                 If Argument 1 = -server: it prints the available payload on screen,")
    print("                                                          but do not insert it into InfluxDB DB.")
    print()
    print("     -config   interactive module to configure parameters for mon360 execution.")
    print()

def stop():
    mypid = os.getpid()
    for procs in os.popen("ps ax |grep mon360 |grep -v grep"):
        fields = procs.split()
        pid = fields[0]
        if pid != str(mypid):
            os.kill(int(pid), signal.SIGKILL)

def payload_cleanup():
    path = str(os.getcwd() + '/backup')
    now = time.time()
    for filename in os.listdir(path):
        if os.path.getmtime(os.path.join(path, filename)) < now - 7 * 86400:
            if os.path.isfile(os.path.join(path, filename)):
                os.remove(os.path.join(path, filename))

def main():
    while True:
        start_time = datetime.now()
        clear()
        print()
        print("mon360 execution start at: " + str(datetime.now()))
        print()
        v_runtime = time.strftime("%Y%m%dT%H%M%S", time.localtime())
        v_arguments = len(sys.argv) - 1
        if sys.argv[1] == "-help":
            help()
            exit()
        elif sys.argv[1] == "-stop":
            stop()
            exit()
        elif (v_arguments < 2):
            print("Missing Arguments")
            print()
            print("./mon360.py -help")
            print("for help")
            exit()
        else:
            v_role = sys.argv[1]
            v_runmode = sys.argv[2]
            if v_runmode not in ("-run", "-dryrun", "-config") or v_role not in ("-server", "-client", "-help"):
                print("Invalid arguments")
                print()
                print("./mon360.py -help")
                print("for help")
                exit()
            elif v_runmode == "-config":
                conf.menu(v_role)
                exit()
            elif v_role == "-client":
                v_runfile = str('mon360_run.' + env.CUSTOMER + '.' + env.HOSTNAME + '.' + v_runtime + '.out')
                v_OutputFile = open(v_runfile, 'w')
                v_OutputFile.write('# DML' + '\n' + '\n')
                v_OutputFile.write('# CONTEXT-DATABASE: MON360' + '\n' + '\n')
                # Collect client information
                os_metrics.main(v_OutputFile, v_runtime)
                db_metrics.main(v_OutputFile, v_runtime)
                v_OutputFile.close()
                # Send payload to InfluxDB DB Server
                export_payload(v_runmode, v_runfile)
                if v_runmode == "-dryrun":
                    break
                end_time = datetime.now()
                print()
                print('mon360 execution complete: {}'.format(end_time - start_time))
            elif v_role == "-server":
                runServer(v_runtime, v_runmode)
                end_time = datetime.now()
                print()
                print('mon360 execution complete: {}'.format(end_time - start_time))
                if v_runmode == "-dryrun":
                    break
        # Cleanup payload files everyday at 00:05
        if v_runtime[9:11] == "00" and v_runtime[11:13] == "05":
            payload_cleanup()
        time.sleep(30)

main()
