#from sys import argv
from os.path import exists
import time
import argparse
import csv
import pandas

def process(from_file, semester_year):
    from_file_exists = exists(from_file)
    if from_file_exists != True:
        print("Sorry, I couldn't find that file.")
        print("Please specify which file to load: ")
        from_file = input()

    print(f"Opening {from_file}")

    indata = pandas.read_csv(from_file,
        index_col = False,
        names = ["HEGIS_Code","Course_No","field_section",\
            "Unknown","field_instructor","title",\
            "field_author","Edition","ISBN","Req_Code", "Semester_Year"],
        converters={'Course_No': str.strip,
            'Edition': str.strip,
            'title': str.lstrip,
            'ISBN': int()
            }
        )
    pandas.options.display.float_format = '{:,.0f}'.format

    #Remove invalid HEGIS codes
    indata = indata[indata.HEGIS_Code != 'XTRA']

    #Filter to only rows for the given semester
    indata = indata[indata.Semester_Year == semester_year]

    unique_isbn = indata['ISBN'].unique().tolist()
    print(len(unique_isbn))
    return unique_isbn, indata

def close(indata):

    indata['field_course'] = indata['HEGIS_Code'].str.cat(indata['Course_No'],sep=" ")
    first_column = indata.pop('field_course')
    indata.insert(0, 'field_course', first_column)
    indata = indata.drop(columns=['HEGIS_Code', 'Course_No'])
    indata = indata.drop(columns=['Unknown'])

    #Set output file name
    timestr = time.strftime("%Y%m%d-%H%M%S")
    to_file = "data/output-" + timestr + ".csv"

    #Sort by total results
    sorteddata = indata.sort_values(by=['EDS_Total_Results'], ascending=False)
    sorteddata.to_csv(to_file)
    return
