#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py 
Author: "Ahmad Habosht"
Semester: "Fall 2024"

The python code in this file is original work written by
"Ahmad Habosht". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.
'''

import argparse
import os, sys

def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts", epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action="store_true", help="Prints sizes in human readable format")
    parser.add_argument("program", type=str, nargs='?', help="Program name to check memory usage")
    args = parser.parse_args()
    return args

def percent_to_graph(percent: float, length: int=20) -> str:
    "Turns a percent 0.0 - 1.0 into a bar graph"
    filled = int(percent * length) #Calculate the number of filled positions
    return "#" * filled + " " * (length - filled) #fill the bar with '#' and spaces

def get_sys_mem() -> int:
    "Return total system memory (used or available) in kB"
    f = open('/proc/meminfo', 'r') #Open the file /proc/meminfo and read its contents.
    for line in f:
        if line.startswith('MemTotal:'): #Locate the line that starts with MemTotal: .
            f.close()
            return int(line.split()[1])  #split the result into a list and return the 2nd value from that list.
    f.close()
    return 0

def get_avail_mem() -> int:
    "Return total memory that is available"
    f = open('/proc/meminfo', 'r') #Open the file /proc/meminfo and read its contents.
    for line in f:
        if line.startswith('MemAvailable:'): #Locate the line that starts with MemAvailbale: .
            f.close()
            return int(line.split()[1])  #split the result into a list and return the 2nd value from that list.
    f.close()
    return 0

def pids_of_prog(app_name: str) -> list:
    "Given an app name, return all pids associated with app"
    pids = os.popen(f"pidof {app_name}").read().strip() #This is to make the program run the pidof command of a certain app.
    return pids.split() #returns the result of pids in a list.

def rss_mem_of_pid(proc_id: str) -> int:
    "Given a process id, return the resident memory used, zero if not found"
    try:
        f = open(f"/proc/{proc_id}/status", "r") #open the file /proc/{proc_id}/status and read its contents, while noting that the {proc_id} is a given process ID for an application.>
        for line in f:
            if line.startswith('VmRSS:'): #Locate the line that starts with VmRSS: .
               f.close()
               return int(line.split()[1]) #if the line was found, return its content in a list and return the 2nd v>
    except FileNotFoundError: #if this error is received then return 0.
        return 0
    return 0

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "Turn 1,024 KiB into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes 
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

if __name__ == "__main__":
    args = parse_command_args()
    total_mem = get_sys_mem()
    avail_mem = get_avail_mem()
    used_mem = total_mem - avail_mem
    percent_used = used_mem / total_mem

    if not args.program:
        # Display system-wide memory usage
        graph = percent_to_graph(percent_used, args.length)
        if args.human_readable: #check if human readable format is requested
            used_mem_h = bytes_to_human_r(used_mem) #change used memory into human readable format
            total_mem_h = bytes_to_human_r(total_mem) #change total memory into human readable format
            print(f"Memory         [{graph} | {percent_used*100:.0f}%] {used_mem_h}/{total_mem_h}") 
        else:
            print(f"Memory         [{graph} | {percent_used*100:.0f}%] {used_mem}/{total_mem}")
    else:
        # Display memory usage for specific program
        pids = pids_of_prog(args.program) #get the process IDs for the program
        if not pids: #if no PID is found
            print(f"{args.program} not found.")
            sys.exit(1)

        total_rss = 0 #initial total memory for the program = 0
        for pid in pids: #loop through each PID
            rss_mem = rss_mem_of_pid(pid)
            total_rss += rss_mem
            percent = rss_mem / total_mem #calculate percentage
            graph = percent_to_graph(percent, args.length)
            if args.human_readable: #this is to format in human readable
                rss_mem_h = bytes_to_human_r(rss_mem)
                total_mem_h = bytes_to_human_r(total_mem)
                print(f"{pid:<15}[{graph} | {percent*100:.0f}%] {rss_mem_h}/{total_mem_h}")
            else:
                print(f"{pid:<15}[{graph} | {percent*100:.0f}%] {rss_mem}/{total_mem}")

        # Summarize total RSS for the program
        percent_total = total_rss / total_mem #calculate total percentage
        graph_total = percent_to_graph(percent_total, args.length) 
        if args.human_readable: #this is to format in human readable
            total_rss_h = bytes_to_human_r(total_rss)
            print(f"{args.program:<15}[{graph_total} | {percent_total*100:.0f}%] {total_rss_h}/{total_mem_h}")
        else:
            print(f"{args.program:<15}[{graph_total} | {percent_total*100:.0f}%] {total_rss}/{total_mem}")
