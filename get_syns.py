import urllib
import json
import MySQLdb as mdb

url = "http://maps.googleapis.com/maps/api/geocode/json?address=googleplex&sensor=false"

response = urllib.urlopen(url)
data = json.load("'" + response.read() + "'")
print data