from pip._vendor import requests
import json as jsonhelper
import re
#insert your google maps api key here
googlemapskey = 'key=AIzaSyBpTLDTGsWw-WJky-vYqwR_10cAHWUi0Ew'
googlemapsapistart = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
#the google place details api: https://developers.google.com/places/web-service/details
googleplacedetails = 'https://maps.googleapis.com/maps/api/place/details/json?'
#location is in the form of latitude, longitude. you can grab this parameters from google maps. default is union square,
#san francisco
mylocation = 'location=37.7799504,-122.4174319'
#the search radius in meters
radius = 'radius=500'
#search for restaurants and bars
locationtype = 'types=restaurant|bar'
#the menu item for which to search. case sensitive
itemtofind = 'Chicken'

#takes in the unique placeid for a location and then performs the following actions:
# 1. gets the detailed information related to that location from the google place details api
# 2. tries to find a menu on the place's website, then searches that menu for an occurrence of 'itemtofind'
# 3. for each dish that matches 'itemtofind', prints the name of the restaurant and the dish that was found
def getDetails(placeid):
    placedetailresponse = requests.get(googleplacedetails+googlemapskey+"&placeid="+placeid)
    placedetails = jsonhelper.loads(placedetailresponse._content.decode('utf-8'))
    # get the restaurant's website from the place details json. if the restaurant has no website, return
    try: website = (placedetails["result"]["website"])
    except KeyError: return
    #get the name of the restaurant. this field will always exist in the json response
    placename = placedetails["result"]["name"]
    #get the html that corresponds to the restaurant's website and transform it into a string
    try: restaurantresponse = requests.get(website)._content.decode('utf-8')
    except UnicodeDecodeError: return
    #search the restaurant's main html page for an anchor that has a form of menu as its text
    menu = re.search('<a href=(.*?)>(.*?)(M|m)enu(.*?)</a>', restaurantresponse)
    if menu:
        found = menu.group(1)
        # if the href is relative (ie. no period)
        if found.find(".") < 0:
            found = website[0:website.rfind("/")] + found
        #the menu url comes in ", so we need to strip these out
        try: menuresponse = requests.get(found.replace("\"", ""))._content.decode('utf-8')
        except Exception: return
        menuregex = re.compile(">.*?"+itemtofind+".*?<", re.DOTALL)
        menuitems = re.findall(menuregex, menuresponse)
        #for each item that matches the description, print it out with the restaurant where it's found
        for menuitem in menuitems:
            print(placename+ " has " +menuitem[menuitem.rfind(">")+1:menuitem.rfind("<")])

mapsresponse = requests.get(googlemapsapistart + googlemapskey + "&"+radius+"&"+locationtype+"&"+mylocation)
values = jsonhelper.loads(mapsresponse._content.decode('utf-8'))
allrestaurants = (values['results'])
#iterate over each restaurant that was returned and see if it has any items that match 'itemtofind'
for restaurant in allrestaurants:
    getDetails(restaurant['place_id'])
