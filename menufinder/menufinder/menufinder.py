from pip._vendor import requests
import json as jsonhelper
import re
#insert your google maps api key here. get a key at this site: https://developers.google.com/maps/web-services/
googlemapskey = 'key=YOUR_KEY_HERE'

googlemapsgeocodeapi = 'http://maps.googleapis.com/maps/api/geocode/json?'
googlemapsapistart = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
#the google place details api: https://developers.google.com/places/web-service/details
googleplacedetails = 'https://maps.googleapis.com/maps/api/place/details/json?'
#input the zip code you want to use for your search. default is san francisco / fidi
zipcode = '94111'
#the search radius in meters
radius = 'radius=500'
#search for restaurants and bars
locationtype = 'types=restaurant|bar'
#the menu item for which to search. case sensitive
itemtofind = 'cheese'

#takes in the unique placeid for a geocodelocation and then performs the following actions:
# 1. gets the detailed information related to that geocodelocation from the google place details api
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
        #for the purposes of the matching, count successive lines as one and ignore the case of the item to find
        menuregex = re.compile(">.*?"+itemtofind+".*?<", re.DOTALL | re.IGNORECASE)
        menuitems = re.findall(menuregex, menuresponse)
        #for each item that matches the description, print it out with the restaurant where it's found
        for menuitem in menuitems:
            print(placename+ " has " +menuitem[menuitem.rfind(">")+1:menuitem.rfind("<")])
geocoderesponse = requests.get(googlemapsgeocodeapi + "address=" + zipcode)
geocodejson = jsonhelper.loads(geocoderesponse._content.decode('utf-8'))
#find the dict that has the latitude, longitude pair in the json response
geocodelocation = geocodejson["results"][0]["geometry"]["location"]
#the "{:.9f}" is needed in order to format the latitude and longitude, which are returned as floats, to string
# see http://stackoverflow.com/questions/15263597/convert-floating-point-number-to-certain-precision-then-copy-to-string
latitude = "{:.9f}".format(geocodelocation['lat'])
longitude = "{:.9f}".format(geocodelocation['lng'])
locationforapi = 'location='+latitude+','+longitude
mapsresponse = requests.get(googlemapsapistart + googlemapskey + "&"+radius+"&"+locationtype+"&"+locationforapi)
values = jsonhelper.loads(mapsresponse._content.decode('utf-8'))
while values:
    allrestaurants = (values['results'])
    #iterate over each restaurant that was returned and see if it has any items that match 'itemtofind'
    for restaurant in allrestaurants:
        getDetails(restaurant['place_id'])
    if 'next_page_token' in values:
        values = jsonhelper.loads(requests.get(googlemapsapistart+googlemapskey+"&"+values['next_page_token'])._content.decode('utf-8'))
    else:
        break