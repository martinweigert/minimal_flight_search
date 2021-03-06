import requests
import json
import sys
import time
import datetime



key = "ENTER YOUR KEY HERE" # See readme file for instructions. https://github.com/martinweigert/minimal_flight_search/blob/master/README

headers = {'content-type': 'application/json'}

number_results = 10 # adjust if you like: Number of alternatives shown.
alliance = "" # adjust if you like. Options: "STAR ALLIANCE", "ONEWORLD", "SKYTEAM" or "" for any.
cabin = "" # adjust if you like. Options: "COACH", "PREMIUM_COACH", "BUSINESS" or "" for any.
country = "DE" # adjust if you like. Depending on the sale country, the currency (and possibly even the price) will change.

def start():
    if key == "ENTER YOUR KEY HERE":
        print("You cannot use this flight search engine without getting your own API Key. \nSee readme file for instructions. https://github.com/martinweigert/minimal_flight_search/blob/master/README")
        sys.exit()
    print("")
    print("### MINIMAL FLIGHT SEARCH ENGINE ###")
    print("Welcome, travel hacker.")
    print("")
    print("When using the search, it is important that you make your entries following the suggested form. \nIf you get repeated error messages, you might have exceeded the daily query limit for the API. Try again tomorrow.")
    print("")
    enter_flight1()

def enter_flight1():
    while True:
        flight1 = input("For the outbound flight, enter airport codes for origin and destination, \nseparated by '-', e.g. TXL-SFO: ")
        if flight1[0:3].isalpha() and flight1[4:].isalpha() and flight1[3] == "-" and len(flight1) == 7:
            enter_flight2(flight1)
        else:
            print("ERROR")
            print("Please type according to the form 'TXL-ARN'. Try again.")

def enter_flight2(flight1):
    while True:
        flight2 = input("For the return flight, enter airport codes for origin and destination, \nseparated by '-', e.g. SFO-TXL. For one-way, press enter: ")
        if len(flight2) == 0:
            flight2 = "ow"
            print("One-way flight chosen.")
            enter_dept_date(flight1,flight2)
        elif len(flight2) > 0:
            if flight2[0:3].isalpha() and flight2[4:].isalpha() and flight2[3] == "-" and len(flight2) == 7:
                enter_dept_date(flight1,flight2)
            else:
                print("ERROR")
                print("Please type according to the form 'TXL-ARN'. Try again.")
                enter_flight2(flight1)

def enter_dept_date(flight1,flight2):
    dept_date = input("Enter departure date, following this form: 2017-12-24: ")
    try:
        datetime.datetime.strptime(dept_date, "%Y-%m-%d")
    except ValueError:
        print("ERROR")
        print("This is not a valid format. Please try again.")
        enter_dept_date(flight1,flight2)
    dept_date_unix = time.mktime(datetime.datetime.strptime(dept_date, "%Y-%m-%d").timetuple())
    now_time = int(time.time())
    if now_time > int(dept_date_unix):
        print("ERROR")
        print("The date you entered is in the past. Please try again.")
        enter_dept_date(flight1,flight2)
    else:
        if flight2 == "ow":
            return_date = "ow"
            get_flight_data(flight1,flight2,dept_date,return_date)
        else:
            enter_return_date(flight1,flight2,dept_date)

def enter_return_date(flight1,flight2,dept_date):
    return_date = input("Enter return date, following this form: 2017-12-31: ")
    try:
        datetime.datetime.strptime(return_date, "%Y-%m-%d")
    except ValueError:
        print("ERROR")
        print("This is not a valid format. Please try again.")
        enter_return_date(flight1,flight2,dept_date)
    return_date_unix = time.mktime(datetime.datetime.strptime(return_date, "%Y-%m-%d").timetuple())
    dept_date_unix = time.mktime(datetime.datetime.strptime(dept_date, "%Y-%m-%d").timetuple())
    if return_date < dept_date:
        print("ERROR")
        print("The date you entered is before the date of the first flight. Please try again.")
        enter_return_date(flight1,flight2,dept_date)
    else:
        get_flight_data(flight1,flight2,dept_date,return_date)


def get_flight_data(outbound_flight,return_flight,date1,date2):
    origin_outbound = outbound_flight[0:3]
    destination_outbound = outbound_flight[4:]
    print("Searching for the best fares...")
    if return_flight == "ow": # "ow" indicates one-way.
        url = ("https://www.googleapis.com/qpxExpress/v1/trips/search?key=%s" % key)
        code = {
        "request": {
        "slice": [
            {
                "origin": origin_outbound,
                "destination": destination_outbound,
                "date": date1,
                "preferredCabin": cabin,
                "alliance": alliance
            },
            ],
            "passengers": {
            "adultCount": 1,
            "infantInLapCount": 0,
            "infantInSeatCount": 0,
            "childCount": 0,
            "seniorCount": 0
            },
            "solutions": number_results,
            "saleCountry": country,
            "refundable": "false"
            }
            }
    else:
        origin_return = return_flight[0:3]
        destination_return = return_flight[4:]

        url = ("https://www.googleapis.com/qpxExpress/v1/trips/search?key=%s" % key)
        code = {
        "request": {
        "slice": [
            {
                "origin": origin_outbound,
                "destination": destination_outbound,
                "date": date1,
                "preferredCabin": cabin,
                "alliance": alliance
            },
            {
                "origin": origin_return,
                "destination": destination_return,
                "date": date2,
                "preferredCabin": cabin,
                "alliance": alliance
            }
            ],
            "passengers": {
            "adultCount": 1,
            "infantInLapCount": 0,
            "infantInSeatCount": 0,
            "childCount": 0,
            "seniorCount": 0
            },
            "solutions": number_results,
            "saleCountry": country,
            "refundable": "false"
            }
            }

    response = requests.post(url, data=json.dumps(code), headers=headers)
    global data
    data = response.json()





    count = 0
    if len(alliance) == 0:
        print("### The cheapest fares ###")
    else:
        print(("### The cheapest fares with %s airlines ###") % alliance)
    if date2 == "ow":
        for i in range(number_results):
            list = [show_flights(i,0)]
            count += 1
            print("Alternative #%s" % count)
            print("Fare price: %s" % data['trips']['tripOption'][i]['saleTotal'])
            for x in list:
                for innerlist in x:
                    print(innerlist)
            print("")

    else:
        for i in range(number_results):
            list = [show_flights(i,0),show_flights(i,1)]
            count += 1
            print("Alternative #%s" % count)
            print("Fare price: %s" % data['trips']['tripOption'][i]['saleTotal'])
            for x in list:
                for innerlist in x:
                    print(innerlist)
            print("")
    new_search = input("Want to do another search? Press enter. Any other key will exit: ")
    if len(new_search) == 0:
        start()
    else:
        print("Thanks for using Minimal Flight Search Engine. Question or ideas? You find my contact details at the bottom of martinweigert.com.")
        sys.exit()


def show_flights(i,t):
    # i = flight alternative (0-19)
    # t = outbound or return (0 or 1)

    count = 0
    try:
        for key in data['trips']['tripOption'][i]['slice'][t]['segment']:
            count += 1
    except:
        print("Error! You probably typed something wrong. Please try again and ensure that you type following the suggested form.")
        print("Restarting the engine...")
        print("")
        time.sleep(2)
        start()
    l = []
    for leg in range(count):
        l.append([])
        timedata = data['trips']['tripOption'][i]['slice'][t]['segment'][leg]['leg'][0]['departureTime']
        day = timedata[0:10]
        hours = timedata[11:16]
        departure_time = ("%s %s" % (day,hours))
        l[leg].append(departure_time)
        origin = data['trips']['tripOption'][i]['slice'][t]['segment'][leg]['leg'][0]['origin']
        l[leg].append(origin)
        destination = data['trips']['tripOption'][i]['slice'][t]['segment'][leg]['leg'][0]['destination']
        l[leg].append(destination)
        carrier = data['trips']['tripOption'][i]['slice'][t]['segment'][leg]['flight']['carrier']
        l[leg].append(carrier)
        bookingcode = data['trips']['tripOption'][i]['slice'][t]['segment'][leg]['bookingCode']
        l[leg].append(bookingcode)
        operating = 0
        for key in data['trips']['tripOption'][i]['slice'][t]['segment'][leg]['leg'][0]:
            if 'operatingDisclosure' in key:
                operating = data['trips']['tripOption'][i]['slice'][t]['segment'][leg]['leg'][0]['operatingDisclosure']
                l[leg].append(operating)
    return l


start()




# if data is accessed locally and not directly from the API, use the following code:
#with open('data.txt') as data_file:
#    data = json.load(data_file)

# if data is pulled from the API for storing in an offline file, use the following code:
#with open('data.txt', 'w') as outfile:
#    json.dump(data, outfile)


# created by Martin Weigert as a part of an ongoing "learning to code" project, in 2017.
# Questions or ideas? Question or ideas? You find my contact details at the bottom of martinweigert.com.
