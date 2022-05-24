import eds
import parse_csv
import math
import argparse

parser = argparse.ArgumentParser(description='Process CSV input file')
parser.add_argument('input', metavar='I', \
        type=str, help='A CSV input file')
parser.add_argument('semester', metavar='S', \
        type=str, help='Semester and year, example S22')
args = parser.parse_args()

session = eds.initSession()

unique_isbn, indata = parse_csv.process(args.input, args.semester)

res_dict = {}

for item in unique_isbn:
    is_NaN = math.isnan(item)
    if is_NaN:
        unique_isbn.remove(item)
        continue
    item = round(item)
    print(item)
    results = eds.textbook_search_by_isbn_post(
            session[0],
            session[1],
            item
            )
    if results is None:
        print("Results is NoneType.")
        continue
    res_dict[item] = {
            'TotalResults': results[0],
            'PLinks': results[1],
            'DbLabel': results[2] if len(results)>2 else "None",
            'Ptype': results[3] if len(results)>2 else "None"
            }

#Map search result data back onto CSV

#Using a dict data comprehension
total_results = {isbn:results['TotalResults'] for (isbn, results) in res_dict.items()}
indata['EDS_Total_Results'] = indata['ISBN'].map(total_results)

for i in range(0,5):
    n = i + 1
    #Using another dict data comprehension with conditional
    plink = {isbn:(results['PLinks'][i] if isinstance(results['PLinks'], list) and len(results['PLinks'])>i else "None") for (isbn, results) in res_dict.items()}
    dbsource = {isbn:(results['DbLabel'][i] if isinstance(results['DbLabel'], list) and len(results['DbLabel'])>i else "None") for (isbn, results) in res_dict.items()}
    ptype = {isbn:(results['Ptype'][i] if isinstance(results['Ptype'], list) and len(results['Ptype'])>i else "None") for (isbn, results) in res_dict.items()}

    indata['Result_%s_URL' %n] = indata['ISBN'].map(plink)
    indata['Result_%s_DbLabel' %n] = indata['ISBN'].map(dbsource)
    indata['Result_%s_Ptype' %n] = indata['ISBN'].map(ptype)
    indata.sort_values(by=['EDS_Total_Results'], ascending=False)
#Output data to CSV
parse_csv.close(indata)
