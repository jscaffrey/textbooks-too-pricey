#!/usr/bin/python
import credentials
import requests
from re import search
import sys
import os
import json
import datetime
import time

def authenticate():
#This section authenticates using our institutional API
    authData = {
            "UserId": credentials.userid,
            "Password": credentials.password,
            "InterfaceId": credentials.interfaceid,
            }
    headers = {
            "Accept": "application/json",
          }
    authUrl = "https://eds-api.ebscohost.com/AuthService/rest/UIDAuth"

    r=requests.post(authUrl, headers=headers, json=authData)
    #print(json.dumps(data))
    print(r.url)
    authResponse = r.json()
    authToken = authResponse.get('AuthToken')
    if authToken != None :
        print("Authenticated.")
    else :
        print("Error during authentication.")
    return authToken

def getXMLVal(response, tag):
    startTag = str("<" + tag + ">")
    endTag = str("</" + tag + ">")
    if search(startTag, response) and search(endTag, response):
        x = response.split(endTag)
        y = x[0].rsplit(startTag)
        token = y[1]
    else:
        print("Error - Tag " + tag + " not found")
        token == None;
    return token;

def createSession(authToken):
    headers = {
            "x-authenticationToken": authToken,
            "Accept": "application/json",
          }
    createSessUrl = "https://eds-api.ebscohost.com/edsapi/rest/createsession"
    createSessData = {
            "Profile":"edsapi",
            "Guest":"n",
          }
    r= requests.post(createSessUrl, headers=headers, json=createSessData)
    #print(r.url)
    createSessResponse = r.json()
    sessionID = createSessResponse.get('SessionToken')
    if sessionID != None :
        print("Session created successfully.")
    else :
        print("Error during session creation.")
    return sessionID

def infoRequest(authToken, sessionID):
    headers = {
            "x-authenticationToken": authToken,
            "x-sessionToken": sessionID,
            "Accept": "application/json",
          }
    infoUrl = "https://eds-api.ebscohost.com/edsapi/rest/info"
    r= requests.post(infoUrl, headers=headers)
    print(r)
    print(r.text)
    print(r.json)
    return

def search(authToken, sessionID, method, searchData):
    headers = {
            "x-authenticationToken": authToken,
            "x-sessionToken": sessionID,
            "Accept": "application/json",
          }
    infoUrl = "https://eds-api.ebscohost.com/edsapi/rest/Search"
    if method.upper() == "GET":
        #print("Sending search...")
        r= requests.get(infoUrl, headers=headers, params=searchData)
    elif method.upper() == "POST":
        #print(searchData)
        #print("Sending search...")
        r= requests.post(infoUrl, headers=headers, json=searchData)
    else:
        print("Method should be GET or POST")
        exit(0)
    #print(r)
    #print(r.text)
    #print(r.url)
    #print(r.json)
    result = json.loads(r.text)
    processed_results = processResults(result)
    return processed_results

def processResults(result):
    totalResults = result['SearchResult']['Statistics']['TotalHits']
    print("Total Results: " + str(totalResults))
    if totalResults <= 0 or totalResults == None:
        #print("No links to share")
        plinks = 0
        return totalResults, plinks
    #Prints the full result of the file
    #jsonToFile("test", result)
    plinks = []
    dbsource = []
    ptype = []
    for rank, record in enumerate(result['SearchResult']['Data']['Records']):
        plinks.append(record['PLink'])
        dbsource.append(record['Header']['DbLabel'])
        ptype.append(record['Header']['PubType'])
        #print ("DbLabel: " + record['Header']['DbLabel'])
        #print ("Ptype: " + record['Header']['PubType'])
        #print ("Hark, result #" + str(rank + 1) + ": " + record['PLink'])
        #if record['Header']['DbLabel'] == 'APA PsycInfo':
        #    jsonToFile(record['Header']['DbLabel'], result)
    #print (dbsource)
    #print (ptype)
    return totalResults, plinks, dbsource, ptype

def jsonToFile(fname, data):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    fullFname = fname + timestr + '.json'
    with open(fullFname, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return

def endSession(authToken, sessionID):
    #Log Out
    headers = {
                "x-authenticationToken": authToken,
            }
    endSessUrl = "https://eds-api.ebscohost.com/edsapi/rest/endsession"
    endSessData = {
            "SessionToken": sessionID,
            }
    r = requests.post(endSessUrl, headers=headers, json=endSessData)
    print(r.url)
    print(r.text)

    #print(r)
    #print(json.dumps(data))
    return

def initSession():
    authToken = authenticate()
    sessionID = createSession(authToken)
    return authToken, sessionID

def textbook_search_by_isbn_post(authToken, sessionID, isbn):
    searchData = """{
        "SearchCriteria":{
            "Queries":[{
                "FieldCode":"IB",
                "Term":"007"
                },
                {
                "BooleanOperator":"NOT",
                "FieldCode":"PT",
                "Term":"Reviews"
                },
                {
                "BooleanOperator":"NOT",
                "FieldCode":"PT",
                "Term":"Review"
                },
                {
                "BooleanOperator":"NOT",
                "FieldCode":"PT",
                "Term":"Academic Journals"
                },
                {
                "BooleanOperator":"NOT",
                "FieldCode":"PT",
                "Term":"Academic Journal"
                },
                {
                "BooleanOperator":"NOT",
                "FieldCode":"PT",
                "Term":"Article"
                }

            ],
            "SearchMode":"all",
            "IncludeFacets":"y",
            "Sort":"relevance",
            "AutoSuggest":"n",
            "AutoCorrect":"n"
        },
        "RetrievalCriteria":{
            "View":"brief",
            "ResultsPerPage":5,
            "PageNumber":1,
            "Highlight":"n",
            "IncludeImageQuickView":"n"
            },
        "Actions": ["AddLimiter(FT:y)"]
        }"""

    searchdata_json = json.loads(searchData)
    searchdata_json["SearchCriteria"]["Queries"][0]["Term"] = str(isbn)

    result = search(authToken, sessionID, "POST", searchdata_json)
    return result

#session = initSession()
#isbn = 9781597569897 #This will come from the CSV
#textbook_search_by_isbn_post(session[0], session[1], isbn)
