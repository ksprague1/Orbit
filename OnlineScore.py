import pygsheets
import six
from six.moves import urllib
from six.moves import BaseHTTPServer
#import gspread
#from oauth2client.service_account import ServiceAccountCredentials
def write_score(score,name,key=None):
    if key != "b3jd0d;]e9":
        return
    # use creds to create a client to interact with the Google Drive API
    #scope = ['https://spreadsheets.google.com/feeds']
    #creds = ServiceAccountCredentials.from_json_keyfile_name('HighScores17792.json', scope)
    try:
        client = pygsheets.authorize(service_file='HighScores17792.json',no_cache=True)
    except:
        return
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("High Scores").sheet1
     
    # Extract and print all of the values
    high_scores = sheet.get_all_values()
    #high score is 2nd and name is first
    for idx in range(len(high_scores)):
        if  score > int(high_scores[idx][1]):
            print idx
            sheet.insert_rows(idx, values=[name,str(score)])
            #sheet.insert_row([name,str(score)],idx+1)
            print "50%"
            sheet.delete_rows(11)
            print "done"
            return
def get_score():
    try:
        client = pygsheets.authorize(service_file='HighScores17792.json',no_cache=True)
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        sheet = client.open("High Scores").sheet1
         
        # Extract and print all of the values
        high_scores = sheet.get_all_values()
         
        # Extract and print all of the values
        high_scores = sheet.get_all_values()
    except:
        return [["_",'100']]*10
    return high_scores
#write_score(101,"billy",key="b3jd0d;]e9")
