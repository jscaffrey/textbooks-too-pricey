# eds-bulk-search-via-csv

This repo is created for running searches within EBSCO Discovery Service (EDS) API and returning results as additional columns appended on a CSV. It was created to search by ISBN for each row of a CSV, returning the top 5 results and omiting Book Reviews and Journal Articles. The query is easily modified.

## Our use case
To support textbook affordability, our library created a Course Books in the Library page. Our library wanted to use an export of bookstore system data and search by ISBNs for each row. EDS could support bulk searching in its out-of-the-box user interface, but for our purposes, we needed results to be associated with each row of the CSV.

## Dependencies
- Python3
- pandas

