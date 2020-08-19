#!/usr/bin/env python3
import base64
import math
import mon360_env as env
import os
import psutil
import pyinputplus as pyinput
import time
from os import system, name

def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

def build_cfg():
    # Build the Environment Variable configuration file based on user responses
    # Define InfluDB Server
    v_influxDBhost = pyinput.inputStr(prompt="Specify InfluDB server location (IP Address/host name/DNS name) [" + env.INFLUXDBSERVER + "]: ", blank=True)
    if v_influxDBhost:
        env.INFLUXDBSERVER = v_influxDBhost
    # Define OS user that owns InfluxDB database
    v_influxosusr = pyinput.inputStr(prompt="Specify the OS user that owns InfluxDB database [" + env.INFLUXDBSRVUSR + "]: ", blank=True)
    if v_influxosusr:
        env.INFLUXDBSRVUSR = v_influxosusr
    # Define the Customer Owner of the server where mon360 is being installed
    v_customer = pyinput.inputStr(prompt="Customer's name [" + env.CUSTOMER + "] : ", blank=True)
    if v_customer:
        v_customer = v_customer.replace(" ", "_")
        env.CUSTOMER = v_customer
    # Automaticaly get server information
    env.HOSTNAME = os.uname()[1]
    env.CPU_COUNT = os.cpu_count()
    env.TOTAL_MEM = math.floor(psutil.virtual_memory()[0] / (1024 ** 2))
    # Define Oracle Database Server (usually the same one that mon360 is being installed)
    v_OracleDBserver = pyinput.inputStr("Oracle Database Server [" + env.ORACLEDBSERVER + "]: ", blank=True)
    if v_OracleDBserver:
        env.ORACLEDBSERVER = v_OracleDBserver
    # Define port that Oracle Listener is listening
    v_OracleDBport = pyinput.inputInt(prompt="Oracle Database Listener Port [" + env.ORACLEDBPORT + "]: ", blank=True)
    if v_OracleDBport:
        env.ORACLEDBPORT = v_OracleDBport
    # Define which database(s) will be monitored on the server
    v_OracleDBsid = pyinput.inputStr(prompt="Oracle Database SID (comma separated. eg: SID1, SID2). [" + env.ORACLEDBSID + "]: ", blank=True)
    if v_OracleDBsid:
        v_OracleDBsid = v_OracleDBsid.replace(" ", "")
        env.ORACLEDBSID = v_OracleDBsid
    # Define the username with, at least, oper privileges to collect data from database
    while True:
        v_OracleDBusr = pyinput.inputStr(prompt="Username with DBA privs (comma separated for each SID. eg: SYSTEM, SYS, MONITOR). [" + env.ORACLEDBUSR + "]: ", blank=True)
        if not v_OracleDBusr:
            v_OracleDBusr = env.ORACLEDBUSR
        if v_OracleDBusr and (len(v_OracleDBusr.split(",")) == len(env.ORACLEDBSID.split(","))):
            v_OracleDBusr = v_OracleDBusr.replace(" ", "")
            env.ORACLEDBUSR = v_OracleDBusr
            break
        else:
            print("Number of users do not match the number of Database instances!")

    # Define the password for the DB user(s)
    while True:
        v_OracleDBpwd = pyinput.inputPassword(prompt="User password (comma separated for each SID. eg: pwd1, pwd2)  Encrypted pwd: [" + env.ORACLEDBPWD + "] :", mask='*', blank=True)
        if v_OracleDBpwd:
            if len(v_OracleDBpwd.split(",")) == len(env.ORACLEDBUSR.split(",")):
                v_OracleDBpwd = v_OracleDBpwd.replace(" ", "")
                v_temppwd = []
                v_temppwd = v_OracleDBpwd.split(",")
                for i in range(len(v_temppwd)):
                    v_temppwd[i] = v_temppwd[i].encode("utf-8")
                    v_temppwd[i] = str(base64.b64encode(v_temppwd[i]))
                env.ORACLEDBPWD = v_temppwd[0]
                for i in range(1, len(v_temppwd)):
                    env.ORACLEDBPWD = env.ORACLEDBPWD + "," + str(v_temppwd[i])
                break
            else:
                print("Number of passwords do not match the number of users! [" + str(len(env.ORACLEDBUSR.split(","))) + "]")
        if not v_OracleDBpwd:
            if len(env.ORACLEDBPWD.split(",")) != len(env.ORACLEDBUSR.split(",")):
                print("Number of passwords from previous configuration do not match the number of users! [" + str(len(env.ORACLEDBUSR.split(","))) + "]")
            else:
                break
    # Define if there is/are Standby Databases for the Databases on the server
    v_has_stbydb = pyinput.inputYesNo(prompt="Are there Standby Databases? [y/n] [" + env.HASSTBYDB + "] :", yesVal='YES', noVal='NO', caseSensitive=False, blank=True)
    if not v_has_stbydb:
        v_has_stbydb = env.HASSTBYDB
    else:
        env.HASSTBYDB = v_has_stbydb
    if env.HASSTBYDB == 'YES':
        # Define Standby Database Server, Listener Port, Databases
        if env.ORACLESTBYDBSERVER:
            # Consider previous configuration, if any
            print("1 - Keep previous configuration:")
            print("    Standby Database Server: " + env.ORACLESTBYDBSERVER)
            print("    Standby Database Port: " + env.ORACLESTBYDBPORT)
            print("    Standby Database SID(s): " + env.ORACLESTBYDBSID)
            print("    Standby Database User(s): " + env.ORACLESTBYDBUSR)
            print()
            print("2 - Configuration for all databases from this session.")
            print("    Standby Database SID(s) on this session: " + env.ORACLEDBSID)
            print()
            print("3 - Custom configuration.")
            print()
            v_OracleStbyDBsid = pyinput.inputChoice(['1', '2', '3'])
            if v_OracleStbyDBsid != "1":
                # Configure for all databases defined on the current configuration session
                if v_OracleStbyDBsid == "2":
                    while True:
                        v_OracleStbyDBserver = pyinput.inputStr("Oracle Standby Database Server(s) (comma separated for each Primary DB. eg: host1, host2, host2): ")
                        env.ORACLESTBYDBSERVER = v_OracleStbyDBserver
                        if len(env.ORACLESTBYDBSERVER.split(",")) == len(env.ORACLEDBSID.split(",")):
                            break
                        else:
                            print("Number of Standby Databases Servers do not match the number of Database instances!")
                    while True:
                        v_OracleStbyDBport = pyinput.inputInt(prompt="Oracle Standby Database Listener Port (comma separated for each Primary DB. eg: 1521, 1525, 1525): ")
                        env.ORACLESTBYDBPORT = v_OracleDBport
                        if len(env.ORACLESTBYDBPORT.split(",")) == len(env.ORACLESTBYDBSERVER.split(",")):
                            break
                        else:
                            print("Number of Standby Databases Ports do not match the number of Standby Database Server(s)!")
                    env.ORACLESTBYDBSID = env.ORACLEDBSID
                    env.ORACLESTBYDBUSR = env.ORACLEDBUSR
                    env.ORACLESTBYDBPWD = env.ORACLEDBPWD
                # Configure for specific database from this configuration session
                elif v_OracleStbyDBsid == "3":
                    # Define Standby Database Server(s)
                    while True:
                        v_OracleStbyDBserver = pyinput.inputStr("Oracle Standby Database Server(s) (comma separated for each Primary DB. eg: host1, NULL, host2 - Type NULL for databases without standby database): ")
                        env.ORACLESTBYDBSERVER = v_OracleStbyDBserver
                        if len(env.ORACLESTBYDBSERVER.split(",")) == len(env.ORACLEDBSID.split(",")):
                            break
                        else:
                            print("Number of Standby Databases Servers do not match the number of Database instances!")
                    # Define Standby Database Listener Port
                    while True:
                        v_OracleStbyDBport = pyinput.inputInt(prompt="Oracle Standby Database Listener Port (comma separated for each Primary DB. eg: 1521, NULL, 1525 - Type NULL for databases without standby database): ")
                        env.ORACLESTBYDBPORT = v_OracleDBport
                        if len(env.ORACLESTBYDBPORT.split(",")) == len(env.ORACLESTBYDBSERVER.split(",")):
                            break
                        else:
                            print("Number of Standby Databases Ports do not match the number of Standby Database Server(s)!")
                    # Define Oracle Standby Databases. User and Pwd are the same as the Primary
                    while True:
                        v_OracleStbyDBsid = pyinput.inputStr(prompt="Oracle Standby Database SID (comma separated. eg: SID1, NULL, SID2 - Type NULL for databases without standby database): ")
                        if len(v_OracleStbyDBsid.split(",")) == len(env.ORACLEDBSID.split(",")):
                            v_OracleStbyDBsid = v_OracleStbyDBsid.replace(" ", "")
                            env.ORACLESTBYDBSID = v_OracleStbyDBsid
                            env.ORACLESTBYDBUSR = env.ORACLEDBUSR
                            env.ORACLESTBYDBPWD = env.ORACLEDBPWD
                            break
                        else:
                            print("Number of Standby Databases do not match the number of Database instances!")
            else:
                # Keep previous configuration
                env.ORACLESTBYDBSID = env.ORACLEDBSID
                env.ORACLESTBYDBUSR = env.ORACLEDBUSR
                env.ORACLESTBYDBPWD = env.ORACLEDBPWD
        else:
            # New configuration once there is no previous configuration
            # Define Standby Database Server(s)
            while True:
                v_OracleStbyDBserver = pyinput.inputStr("Oracle Standby Database Server(s) (comma separated for each Primary DB. eg: host1, NULL, host2 - Type NULL for databases without standby database): ")
                env.ORACLESTBYDBSERVER = v_OracleStbyDBserver
                if len(env.ORACLESTBYDBSERVER.split(",")) == len(env.ORACLEDBSID.split(",")):
                    break
                else:
                    print("Number of Standby Databases Servers do not match the number of Database instances!")
            # Define Standby Database Listener Port
            while True:
                v_OracleStbyDBport = pyinput.inputInt(prompt="Oracle Standby Database Listener Port (comma separated for each Primary DB. eg: 1521, NULL, 1525 - Type NULL for databases without standby database): ")
                env.ORACLESTBYDBPORT = v_OracleDBport
                if len(env.ORACLESTBYDBPORT.split(",")) == len(env.ORACLESTBYDBSERVER.split(",")):
                    break
                else:
                    print("Number of Standby Databases Ports do not match the number of Standby Database Server(s)!")
            # Define Oracle Standby Databases. User and Pwd are the same as the Primary
            while True:
                v_OracleStbyDBsid = pyinput.inputStr(prompt="Oracle Standby Database SID (comma separated. eg: SID1, NULL, SID2 - Type NULL for databases without standby database): ")
                if len(v_OracleStbyDBsid.split(",")) == len(env.ORACLEDBSID.split(",")):
                    v_OracleStbyDBsid = v_OracleStbyDBsid.replace(" ", "")
                    env.ORACLESTBYDBSID = v_OracleStbyDBsid
                    env.ORACLESTBYDBUSR = env.ORACLEDBUSR
                    env.ORACLESTBYDBPWD = env.ORACLEDBPWD
                    break
                else:
                    print("Number of Standby Databases do not match the number of Database instances!")
    else:
        # Clrar Standby Database configuration if No Standby is selected
        env.ORACLESTBYDBSERVER = ""
        env.ORACLESTBYDBPORT = ""
        env.ORACLESTBYDBSID = ""
        env.ORACLESTBYDBUSR = ""
        env.ORACLESTBYDBPWD = ""
    write_cfg()

def clear_cfg():
    # Reset all Environment Variable to NULL
    env.INFLUXDBSERVER = ""
    env.INFLUXDBUSRPWD = ""
    env.CUSTOMER = ""
    env.HOSTNAME = ""
    env.ORACLEDBSERVER = ""
    env.ORACLEDBPORT = ""
    env.ORACLEDBSID = ""
    env.ORACLEDBUSR = ""
    env.ORACLEDBPWD = ""
    env.HASSTBYDB = ""
    env.ORACLESTBYDBSERVER = ""
    env.ORACLESTBYDBPORT = ""
    env.ORACLESTBYDBSID = ""
    env.ORACLESTBYDBUSR = ""
    env.ORACLESTBYDBPWD = ""
    write_cfg()

def write_cfg():
    # Write Environment variables file based on the configuration
    f = open('./mon360_env.py', 'w')
    f.write('INFLUXDBSERVER = "' + env.INFLUXDBSERVER + '"' + '\n')
    f.write('INFLUXDBUSRPWD = "' + env.INFLUXDBUSRPWD + '"' + '\n')
    f.write('CUSTOMER = "' + env.CUSTOMER + '"' + '\n')
    f.write('HOSTNAME = "' + env.HOSTNAME + '"' + '\n')
    if v_flag == "Config":
        f.write('CPU_COUNT = ' + str(env.CPU_COUNT) + '\n')
        f.write('TOTAL_MEM = ' + str(env.TOTAL_MEM) + '\n')
    else:
        f.write('CPU_COUNT = ""' + '\n')
        f.write('TOTAL_MEM = ""' + '\n')
    f.write('ORACLEDBSERVER = "' + env.ORACLEDBSERVER + '"' + '\n')
    f.write('ORACLEDBPORT = "' + str(env.ORACLEDBPORT) + '"' + '\n')
    f.write('ORACLEDBSID = "' + env.ORACLEDBSID + '"' + '\n')
    f.write('ORACLEDBUSR = "' + env.ORACLEDBUSR + '"' + '\n')
    f.write('ORACLEDBPWD = "' + env.ORACLEDBPWD + '"' + '\n')
    f.write('HASSTBYDB = "' + env.HASSTBYDB + '"' + '\n')
    f.write('ORACLESTBYDBSERVER = "' + env.ORACLESTBYDBSERVER + '"' + '\n')
    f.write('ORACLESTBYDBPORT = "' + str(env.ORACLESTBYDBPORT) + '"' + '\n')
    f.write('ORACLESTBYDBSID = "' + env.ORACLESTBYDBSID + '"' + '\n')
    f.write('ORACLESTBYDBUSR = "' + env.ORACLESTBYDBUSR + '"' + '\n')
    f.write('ORACLESTBYDBPWD = "' + env.ORACLESTBYDBPWD + '"' + '\n')
    f.close()

def menu(v_role):
    clear()
    print("=============================")
    print(" mon360 configuration module")
    print("=============================")
    print()
    v_curtime = time.strftime("%Y-%m-%dT%H_%M_%SZ%z", time.localtime())
    global v_flag
    v_flag = pyinput.inputMenu(['Config', 'Clear'], numbered=True)
    os.rename('./mon360_env.py', './mon360_env.py.bkp' + v_curtime) # Take backup of previous configuration
    if v_flag == "Config":
        if v_role == "-client":
            build_cfg() # Build new configuration
        else:
            print("Configuring MON360 database")
            os.system(str('influx -execute \'DROP DATABASE "MON360"\''))
            os.system(str('influx -execute \'CREATE DATABASE "MON360"\''))
            os.system(str('influx -execute \'CREATE RETENTION POLICY "live_data_32d" ON "MON360" DURATION 32d REPLICATION 1 DEFAULT\''))
            os.system(str('influx -execute \'DROP RETENTION POLICY "autogen" on "MON360"\''))
            os.system(str('influx -execute \'CREATE RETENTION POLICY "cold_data_forever" ON "MON360" DURATION INF REPLICATION 1\''))
            clear_cfg() # No config file is needed for server side
            print("MON360 database successfully created into INfluxDB")
    else:
        if v_role == "-client":
            clear_cfg() # Clear configuration
        else:
            os.system(str('influx -execute \'DROP DATABASE "MON360"\''))
            clear_cfg() # Clear configuration
