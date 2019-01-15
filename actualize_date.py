#!/usr/bin/env python
import csv
import sys
import os
import re
import argparse
import time as time_mod
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

def start_read():
    args = handle_command_line(sys.argv)
    input_filename = args.input_file
    output_filename = args.output_file
    time_column = args.time_column

    if None != args.string_time:
        actual_date = args.string_time
    else:
        actual_date = find_time_in_file(args.time_file) 
    
    if None == actual_date:
        print ("Error parsing start time")
        return 1

    try:
        unix_time = time_mod.mktime(parse(actual_date).timetuple())
    except:
        unix_time = float(actual_date)

    base_datetime = datetime.fromtimestamp(unix_time)
    zero_date = parse("1970-01-01")

    with open(input_filename) as csv_file:
        dialect = csv.Sniffer().sniff(csv_file.read(4096))
        csv_file.seek(0)
        reader = csv.DictReader(csv_file, dialect=dialect)
        if None != output_filename:
            out_file = open(output_filename, 'w')
            writer = csv.DictWriter(out_file, fieldnames=reader.fieldnames)
            writer.writeheader()
        else:
            print(";".join(reader.fieldnames))

        for row in reader:
            row_date = parse(row[time_column])
            row_date = row_date + timedelta(hours=base_datetime.hour, minutes=base_datetime.minute, seconds=base_datetime.second, days=base_datetime.day)
            row_date = row_date + relativedelta(months=base_datetime.month, years=base_datetime.year)
            row_date = row_date - timedelta(days=1)
            row_date = row_date - relativedelta(months=zero_date.month, years=zero_date.year)
            row[time_column] = row_date
            if None != output_filename:
                writer.writerow(row)
            else:
                s = ""
                for field in reader.fieldnames:
                    s = s + str(row.get(field)) + ";" 
                s = s[:-1]
                print(s)

        csv_file.close()
        if None != output_filename:
            out_file.close()

def find_time_in_file(file_name):
    file = open(file_name, "r")
    for line in file:
        clean_line = re.sub(r"[^\d\w\s:\.]", "", line)
        try:
            parse(clean_line)
            return clean_line
        except:
            pass

    return None

def handle_command_line(args):
    args_parser = argparse.ArgumentParser(description='Actualize timestamp column by start date/time')
    args_parser.add_argument('-i', '--input_file', action='store', dest='input_file', required=True)
    args_parser.add_argument('-o', '--output_file', action='store', dest='output_file', required=False)
    args_parser.add_argument('-s', '--string_time', action='store', dest='string_time', help="start time string representation", required=False)
    args_parser.add_argument('-f', '--time_file', action='store', dest='time_file', help="file containing start time", required=False)
    args_parser.add_argument('-c', '--column_name', action='store', dest='time_column', help="Time column name in source file", required=False, default = "Time")
    args = args_parser.parse_args()
    if not (args.string_time or args.time_file):
        args_parser.error('Choose start time source')
    if (args.string_time and args.time_file):
        args_parser.error('Choose only one start time source')

    return args

if __name__ == '__main__':
    start_read()
