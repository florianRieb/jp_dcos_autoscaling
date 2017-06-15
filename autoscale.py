"""
Created on 31.05.2017

@author: Florian
"""

import sys
import requests
import json
import math
import time

#fix Marathon Host IP like "http://ip"
#marathon_host = "http://134.103.195.127"

class Marathon(object):
    def __init__(self, marathon_host):
        self.name = marathon_host
        self.uri = (marathon_host)
        self.headers = {'Authorization': 'token=' + dcos_auth_token, 'Content-type': 'application/json'}



    def get_all_apps(self):
        response = requests.get(self.uri + '/service/marathon/v2/apps', headers=self.headers, verify=False).json()
        if response['apps'] == []:
            print("No Apps found on Marathon")
            sys.exit(1)
        else:
            apps = []
            for i in response['apps']:
                appid = i['id'].strip('/')
                apps.append(appid)
            print("Found the following App LIST on Marathon =", apps)
            self.apps = apps  # TODO: declare self.apps = [] on top and delete this line, leave the apps.append(appid)
            return apps

    def get_app_details(self, marathon_app):
        response = requests.get(self.uri + '/service/marathon/v2/apps/' + marathon_app, headers=self.headers, verify=False).json()
        #print('Marathon Application = ' + str(response))
        if (response['app']['tasks'] == []):
            print('No task data on Marathon for App !', marathon_app)
        else:
            app_instances = response['app']['instances']
            self.appinstances = app_instances
            print(marathon_app, "has", self.appinstances, "deployed instances")
            app_task_dict = {}
            for i in response['app']['tasks']:
                taskid = i['id']
                hostid = i['host']
                slaveId = i['slaveId']
                #print('DEBUG - taskId=', taskid + ' running on ' + hostid + 'which is Mesos Slave Id ' + slaveId)
                app_task_dict[str(taskid)] = str(slaveId)
            return app_task_dict

    def scale_app(self, marathon_app, autoscale_multiplier):
        target_instances_float = self.appinstances * autoscale_multiplier
        target_instances = math.ceil(target_instances_float)
        if (target_instances > max_instances):
            print("Reached the set maximum instances of", max_instances)
            target_instances = max_instances
        else:
            target_instances = target_instances
        data = {'instances': target_instances}
        json_data = json.dumps(data)
        # headers = {'Content-type': 'application/json'}
        response = requests.put(self.uri + '/service/marathon/v2/apps/' + marathon_app, json_data, headers=self.headers,
                                verify=False)
        print('Scale_app return status code =', response.status_code)

    def scale_down_app(self, marathon_app, autoscale_multiplier):
        target_instances = math.ceil(self.appinstances / autoscale_multiplier)

        if (target_instances < min_instances):
            print("No scale, reached the minimum instances of ", min_instances)
            target_instances = min_instances
        else:
            target_instances = target_instances

        if (self.appinstances != target_instances):
            data = {'instances': target_instances}
            json_data = json.dumps(data)
          # headers = {'Content-type': 'application/json'}
            response = requests.put(self.uri + '/service/marathon/v2/apps/' + marathon_app, json_data,
                                             headers=self.headers, verify=False)
            print('Scale_down_app return status code =', response.status_code)


def get_task_agentstatistics(task, agent):
    # Get the performance Metrics for all the tasks for the Marathon App specified
    # by connecting to the Mesos Agent and then making a REST call against Mesos statistics
    # Return to Statistics for the specific task for the marathon_app
    dcos_headers = {'Authorization': 'token=' + dcos_auth_token, 'Content-type': 'application/json'}
    response = requests.get(marathon_host + '/slave/' + agent + '/monitor/statistics.json', verify=False, headers=dcos_headers, allow_redirects=True).json()
    # print ('DEBUG -- Getting Mesos Metrics for Mesos Agent =',agent)
    for i in response:
        executor_id = i['executor_id']
        # print("DEBUG -- Printing each Executor ID ", executor_id)
        if (executor_id == task):
            task_stats = i['statistics']
            print('****Specific stats for task', executor_id, '=', task_stats)
            return task_stats


def get_token():
    with open('tokenfile') as f:
        token = f.read()
    f.closed
    return str(token)


def timer():
    print("Successfully completed a cycle, sleeping for 30 seconds ...")
    time.sleep(30)
    return


if __name__ == "__main__":
    import argparse
    print("This application tested with Python3 only")

    parser = argparse.ArgumentParser(description='Marathon autoscale app.')

    parser.add_argument('--master', help='The DNS hostname or IP of your Marathon Instance', required=True)

    parser.add_argument('--max_mem_percent',
                             help='The Max percent of Mem Usage averaged across all Application Instances to trigger Autoscale (ie. 80)',
                             required=True, type=float)
    parser.add_argument('--max_cpu_time',
                             help='The Max percent of CPU Usage averaged across all Application Instances to trigger Autoscale (ie. 80)',
                             required=True, type=float)
    parser.add_argument('--trigger_mode', help='Which metric(s) to trigger Autoscale (' and ', ' or ')',
                             required=True)
    parser.add_argument('--autoscale_multiplier', help='Autoscale multiplier for triggered Autoscale (ie 1.5)',
                             required=True, type=float)
    parser.add_argument('--max_instances',
                         help='The Max instances that should ever exist for this application (ie. 20)',
                             required=True, type=int)
    parser.add_argument('--marathon-app',
                             help='Marathon Application Name to Configure Autoscale for from the Marathon UI',
                             required=True)
    parser.add_argument('--min_instances', help='Minimum number of instances to maintain', required=True, type=int)
    parser.add_argument('--cool-down-factor', help='Number of cycles to avoid scaling again', required=True,
                             type=int)
    parser.add_argument('--trigger_number', help='Number of cycles to avoid scaling again', required=True,
                             type=int)

    try:
        args = parser.parse_args()
    except Exception as e:
        parser.print_help()
        sys.exit(1)

    marathon_host = args.master
    max_mem_percent = float(args.max_mem_percent)
    max_cpu_time = float(args.max_cpu_time)
    trigger_mode = args.trigger_mode
    autoscale_multiplier = float(args.autoscale_multiplier)
    max_instances = float(args.max_instances)
    marathon_app = args.marathon_app
    min_instances = float(args.min_instances)
    cool_down_factor = float(args.cool_down_factor)
    trigger_number = float(args.trigger_number)

    # Initialize variables
    cool_down = 0
    trigger_var = 0

    # Add own Token
    dcos_auth_token = ""
    dcos_auth_token = get_token()

    running = 1
    while running == 1:

        # Initialize the Marathon object
        aws_marathon = Marathon(marathon_host)
        #liest Argumente aus
       # aws_marathon.getArgs()
        print("Marathon URI = ...", aws_marathon.uri)
        print("Marathon Headers = ...", aws_marathon.headers)
        print("Marathon name = ...", aws_marathon.name)
        # Call get_all_apps method for new object created from aws_marathon class and return all apps
        marathon_apps = aws_marathon.get_all_apps()
        print("The following apps exist in Marathon...", marathon_apps)
        # Quick sanity check to test for apps existence in MArathon.
        if (marathon_app in marathon_apps):
            print("  Found your Marathon App=", marathon_app)
        else:
            print("  Could not find your App =", marathon_app)
            timer()
            continue

        # Return a dictionary comprised of the target app taskId and hostId.
        app_task_dict = aws_marathon.get_app_details(marathon_app)
        print("    Marathon  App 'tasks' for", marathon_app, "are=", app_task_dict)

        app_cpu_values = []
        app_mem_values = []
        # for k,v in Dictionarie.items()
        for task, agent in app_task_dict.items():
            # cpus_time =(task_stats['cpus_system_time_secs']+task_stats['cpus_user_time_secs'])
            # print ("Combined Task CPU Kernel and User Time for task", task, "=", cpus_time)
            print('Task = ' + task)
            print('Agent = ' + agent)
            # Compute CPU usage
            task_stats = get_task_agentstatistics(task, agent)
            cpus_system_time_secs0 = float(task_stats['cpus_system_time_secs'])
            cpus_user_time_secs0 = float(task_stats['cpus_user_time_secs'])
            timestamp0 = float(task_stats['timestamp'])

            time.sleep(1)

            task_stats = get_task_agentstatistics(task, agent)
            cpus_system_time_secs1 = float(task_stats['cpus_system_time_secs'])
            cpus_user_time_secs1 = float(task_stats['cpus_user_time_secs'])
            timestamp1 = float(task_stats['timestamp'])
            # user-mode + system-mode der cpu operationen
            cpus_time_total0 = cpus_system_time_secs0 + cpus_user_time_secs0
            cpus_time_total1 = cpus_system_time_secs1 + cpus_user_time_secs1
            cpus_time_delta = cpus_time_total1 - cpus_time_total0
            timestamp_delta = timestamp1 - timestamp0

            # CPU percentage usage
            usage = float(cpus_time_delta / timestamp_delta) * 100

            # RAM usage
            mem_rss_bytes = int(task_stats['mem_rss_bytes'])
            print("task", task, "mem_rss_bytes=", mem_rss_bytes)
            mem_limit_bytes = int(task_stats['mem_limit_bytes'])
            print("task", task, "mem_limit_bytes=", mem_limit_bytes)
            mem_utilization = 100 * (float(mem_rss_bytes) / float(mem_limit_bytes))
            print("task", task, "mem Utilization=", mem_utilization)
            print()

            # app_cpu_values.append(cpus_time)
            app_cpu_values.append(usage)
            app_mem_values.append(mem_utilization)

        # Normalized data for all tasks into a single value by averaging
        app_avg_cpu = (sum(app_cpu_values) / len(app_cpu_values))
        print('Current Average  CPU Time for app', marathon_app, '=', app_avg_cpu)
        app_avg_mem = (sum(app_mem_values) / len(app_mem_values))
        print('Current Average Mem Utilization for app', marathon_app, '=', app_avg_mem)
        # Evaluate whether an autoscale trigger is called for
        print('\n')
        if (trigger_mode == "and"):
            if (app_avg_cpu > max_cpu_time) and (app_avg_mem > max_mem_percent) and (trigger_var >= trigger_number):
                print("Autoscale triggered based on 'both' Mem & CPU exceeding threshold")
                aws_marathon.scale_app(marathon_app, autoscale_multiplier)
                trigger_var = 0

            elif (app_avg_cpu < max_cpu_time) and (app_avg_mem < max_mem_percent) and (cool_down >= cool_down_factor):
                print("Autoscale down triggered based on 'both' Mem & CPU are down the threshold")
                aws_marathon.scale_down_app(marathon_app, autoscale_multiplier)
                cool_down = 0
            elif (app_avg_cpu > max_cpu_time) and (app_avg_mem > max_mem_percent):
                trigger_var += 1
                cool_down = 0
                print("Limits exceeded but waiting for trigger_number to be exceeded too to scale up, ", trigger_var)

            elif (app_avg_cpu < max_cpu_time) and (app_avg_mem < max_mem_percent) and (cool_down < cool_down_factor):
                cool_down += 1
                trigger_var = 0
                print("Limits are not exceeded but waiting for trigger_number to be exceeded too to scale down, ",
                      cool_down)
            else:
                print("Both values were not greater than autoscale targets")
        elif (trigger_mode == "or"):
            if ((app_avg_cpu > max_cpu_time) or (app_avg_mem > max_mem_percent)) and (trigger_var >= trigger_number):
                print("Autoscale triggered based Mem 'or' CPU exceeding threshold")
                aws_marathon.scale_app(marathon_app, autoscale_multiplier)
                trigger_var = 0
            elif ((app_avg_cpu < max_cpu_time) or (app_avg_mem < max_mem_percent)) and (cool_down >= cool_down_factor):
                print("Autoscale triggered based on Mem or CPU are down the threshold")
                aws_marathon.scale_down_app(marathon_app, autoscale_multiplier)
                cool_down = 0
            elif (app_avg_cpu > max_cpu_time) or (app_avg_mem > max_mem_percent):
                trigger_var += 1
                cool_down = 0
                print("Limits exceeded but waiting for trigger_number to be exceeded too to scale up, ", trigger_var)
            elif (app_avg_cpu < max_cpu_time) or (app_avg_mem < max_mem_percent):
                cool_down += 1
                trigger_var = 0
                print("Limits are not exceeded but waiting for trigger_number to be exceeded too to scale down, ",
                      cool_down)
            else:
                print("Neither Mem 'or' CPU values exceeding threshold")
        timer()
