import csv
import datetime
import pycountry
import sys


def open_csv_file(filename):
    """ Function handle opening files with encoding utf-8 and utf-16"""
    if filename[-4:] == '.csv':
        # For valid .csv file, try encoding utf-8 then utf-16
        try:
            with open(filename, newline='', encoding='utf-8') as fp:
                return convert_csv(fp)
        except UnicodeDecodeError:
            with open(filename, newline='', encoding='utf-16') as fp:
                return convert_csv(fp)
        except FileNotFoundError:
            sys.stderr.write(
                f'Fatal error. File {filename} does not exist.'
            )
            # Stop execution
            sys.exit()
    # If file extension is not .csv don't pass it into convert_csv
    else:
        sys.stderr.write(
            f'Fatal error. File {filename} is not valid csv file.'
        )
        # Stop execution
        sys.exit()


def convert_csv(fp):
    """
    Function converts data from csv, and returns it as sorted list of tuples
    """
    # Helper dict and list
    data_dict = {}
    output = []
    # Pass csv file to csv reader
    csv_reader = csv.reader(fp)
    for n, line in enumerate(csv_reader, 1):
        # Process rows that have exact 4 elements
        if len(line) == 4:

            # Change datetime format
            try:
                date = datetime.datetime.strptime(
                    line[0], "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
            # If date has wrong format, skip iteration
            except ValueError:
                sys.stderr.write(
                    f'Datetime format invalid. Skipping line {n}\n'
                )
                continue

            # Change region to country
            try:
                alpha_2 = pycountry.subdivisions.lookup(line[1]).country_code
                country = pycountry.countries.get(alpha_2=alpha_2).alpha_3
            except LookupError:
                sys.stderr.write(
                    f'Wrong state name in line {n}.Country code set to "XXX"\n'
                )
                country = 'XXX'

            try:
                impressions = int(line[2])
            # If number of impressions is invalid, skip iteration
            except ValueError:
                sys.stderr.write(
                    f'Number of impressions is invalid. Skipping line {n}\n'
                )
                continue

            try:
                clicks = round(float(line[3].strip('%')) * impressions / 100)
            except ValueError:
                sys.stderr.write(
                    f'CTR number is invalid. Skipping line {n}\n'
                )
                continue

            # Add valid data to dictionary
            # If object exist update values
            if (date, country) in data_dict.keys():
                data_dict[(date, country)]['impressions'] += impressions
                data_dict[(date, country)]['clicks'] += clicks
            # If object does not exist create new
            else:
                data_dict[(date, country)] = {
                    'date': date,
                    'country': country,
                    'impressions': impressions,
                    'clicks': clicks
                }
        else:
            sys.stderr.write(
                f'Line {n} has wrong number of elements. Skipping line'
            )
    # Create list of tupples from dictionary
    for key in data_dict:
        data_tupple = (
            data_dict[key]['date'],
            data_dict[key]['country'],
            data_dict[key]['impressions'],
            data_dict[key]['clicks'],
        )
        output.append(data_tupple)
    # Sort objects by date, then by country
    sorted_output = sorted(output, key=lambda x: (x[0], x[1]))
    return sorted_output
