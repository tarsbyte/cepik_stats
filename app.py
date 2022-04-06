
from flask import Flask, render_template, request, flash
import json
from datetime import datetime
from werkzeug.exceptions import HTTPException
import grequests

app = Flask(__name__)
app.secret_key = "key"

dict = {"02":"DOLNOŚLĄSKIE","04":"KUJAWSKO-POMORSKIE","06":"LUBELSKIE","08":"LUBUSKIE",
            "10":"ŁÓDZKIE","12":"MAŁOPOLSKIE","14":"MAZOWIECKIE","16":"OPOLSKIE","18":"PODKARPACKIE","20":"PODLASKIE",
            "22":"POMORSKIE","24":"ŚLĄSKIE","26":"ŚWIĘTOKRZYSKIE","28":"WARMIŃSKO-MAZURSKIE","30":"WIELKOPOLSKIE",
            "32":"ZACHODNIOPOMORSKIE"}

short_vers = {"DOLNOŚ.":"DOLNOŚLĄSKIE","KUJAW-POM.":"KUJAWSKO-POMORSKIE","LUBEL":"LUBELSKIE","LUBUS.":"LUBUSKIE",
            "MAŁOPOL.":"MAŁOPOLSKIE","MAZOW.":"MAZOWIECKIE","OPOL.":"OPOLSKIE","PODKARP.":"PODKARPACKIE","PODLAS.":"PODLASKIE",
            "POMORS.":"POMORSKIE","ŚLĄSK.":"ŚLĄSKIE","ŚWIĘTOK.":"ŚWIĘTOKRZYSKIE","WARMIŃ-MAZ.":"WARMIŃSKO-MAZURSKIE","WIELKOPOL.":"WIELKOPOLSKIE",
            "ZACH-POM.":"ZACHODNIOPOMORSKIE"}


reverse_dict = {}

for key, val in dict.items():
    reverse_dict[val] = key

#Sources:
#https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true#run-the-app-locally
#https://stackoverflow.com/questions/24898312/urllib-error-urlerror-urlopen-error-no-host-given-python-3
#https://api.coingecko.com/api/v3/exchange_rates
#https://www.youtube.com/watch?v=ojPw5Bvvrnk
#https://api.cepik.gov.pl/pojazdy?wojewodztwo=14&data-od=20191201&data-do=20191231&filter[marka]=TOYOTA&filter[model]=AURIS
#https://www.youtube.com/watch?v=ojPw5Bvvrnk
#https://translate.google.pl/?hl=pl&sl=pl&tl=en&text=wprowad%C5%BA&op=translate
#https://api.cepik.gov.pl/slowniki/wojewodztwa
#https://stackoverflow.com/questions/3294889/iterating-over-dictionaries-using-for-loops
#https://www.freecodecamp.org/news/html-tables-table-tutorial-with-css-example-code/
#https://www.w3schools.com/colors/colors_rgb.asp
#https://www.tutorialspoint.com/html/html_backgrounds.htm
#https://stackoverflow.com/questions/61996861/how-to-send-data-to-webpage-using-python-flask
#https://bdl.stat.gov.pl/api/v1/data/by-variable/60620?format=json&year=2004&year=2005&year=2006&unit-parent-id=011200000000 !!!!!!!!!!!!!!!!!!!!!!!!!
#https://stackoverflow.com/questions/8113782/split-string-on-whitespace-in-python
#https://www.digitalocean.com/community/tutorials/how-to-use-web-forms-in-a-flask-application
#https://stackoverflow.com/questions/1602934/check-if-a-given-key-already-exists-in-a-dictionary
#https://flask.palletsprojects.com/en/1.1.x/errorhandling/
#https://stackoverflow.com/questions/44445376/how-to-send-multiple-requests-async-from-flask-server
#https://geekyhumans.com/create-asynchronous-api-in-python-and-flask/
#http://www.cepik.gov.pl/interfejs-dla-cepik
#https://stackoverflow.com/questions/642154/how-to-convert-strings-into-integers
#https://docs.python.org/3/tutorial/errors.html
#https://stackoverflow.com/questions/18810777/how-do-i-read-a-response-from-python-requests
#https://pypi.org/project/grequests/
#https://stackoverflow.com/questions/6130768/return-a-default-value-if-a-dictionary-key-is-not-available
#https://stackoverflow.com/questions/9257094/how-to-change-a-string-into-uppercase
#https://www.section.io/engineering-education/integrating-external-apis-with-flask/
def check_correct_date(date_1, date_2):

    date_1 = date_1.split('-')
    date_2 = date_2.split('-')

    if(len(date_1) != 3 or len(date_2) != 3):
        flash("You have enetered date in incorrect form")
        return False

    for word in date_1:
        for i in word:
            if(ord(i) < ord("0") or ord(i) > ord("9")):
                flash("You have enetered date in incorrect form")
                return False

    try:
        if (datetime(int(date_1[0]), int(date_1[1]), int(date_1[2])) > datetime(int(date_2[0]), int(date_2[1]), int(date_2[2]))):
            flash("You have enetered first date, as later than second")
            return False
    except ValueError as ve:
        flash(ve.__str__())
        return False
    return True

@app.route("/")
def main():
    flash("Welcome")
    return render_template("Cars.html")


@app.route("/model_info", methods=['POST', 'GET'])
def model_info():

    brand_input = str(request.form['brand_input'])
    model_input = str(request.form['model_input'])
    date1_input = str(request.form['dat1_input'])
    date2_input = str(request.form['dat2_input'])

    if (date1_input == "" or date2_input == ""):
        flash("You haven't enetered one of the dates")
        return render_template("Cars.html")

    if(not check_correct_date(date1_input,date2_input)):
        return render_template("Cars.html")

    brand_input = brand_input.upper()
    model_input = model_input.upper()
    max_val, min_val, max_voiv, min_voiv, avg, sum, results_dict = get_car_info(brand_input,model_input,date1_input,date2_input)

    flash("Enter the brand, model and time period")

    return render_template("Cars.html", max_voiv=max_voiv, min_voiv=min_voiv, avg=avg, data = 1, max_val = max_val, min_val = min_val, sum = sum,
                           maz = results_dict.get(reverse_dict["MAZOWIECKIE"],0), dol = results_dict.get(reverse_dict["DOLNOŚLĄSKIE"],0), sla = results_dict.get(reverse_dict["ŚLĄSKIE"],0),
                           pod = results_dict.get(reverse_dict["PODKARPACKIE"],0), mal = results_dict.get(reverse_dict["MAŁOPOLSKIE"],0), swi = results_dict.get(reverse_dict["ŚWIĘTOKRZYSKIE"],0),
                           pom = results_dict.get(reverse_dict["POMORSKIE"],0), zac = results_dict.get(reverse_dict["ZACHODNIOPOMORSKIE"],0), pol = results_dict.get(reverse_dict["PODLASKIE"],0),
                           lod = results_dict.get(reverse_dict["ŁÓDZKIE"],0), wie = results_dict.get(reverse_dict["WIELKOPOLSKIE"],0), lub = results_dict.get(reverse_dict["LUBUSKIE"],0),
                           lul = results_dict.get(reverse_dict["LUBELSKIE"],0), opo = results_dict.get(reverse_dict["OPOLSKIE"],0), war = results_dict.get(reverse_dict["WARMIŃSKO-MAZURSKIE"],0), kuj = results_dict.get(reverse_dict["KUJAWSKO-POMORSKIE"],0))

@app.errorhandler(HTTPException)
def handle_except(e):

    flash("Nie udało się zrealizować zadania - sprawdź czy wprowadziłeś poprawne dane. Błąd: " + str(e.code) + " " + str(e.name) + " " + str(e.description))
    return render_template("Cars.html")

def brand_info_max_min(brand):
    main_set = "AUDI	TOYOTA	VOLKSWAGEN	HYUNDAI	MERCEDES-BENZ	VOLVO	RENAULT	BMW	OPEL	CITROEN	HONDA	SKODA	FORD	KIA	FIAT	NISSAN	SEAT"

    others = 0
    most_br = ""
    least_br = ""
    most_val = 0
    least_val = 10000
    other_brands = {}

    for key, val in brand.items():

        if (most_val < val):
            most_val = val
            most_br = key

        if (least_val > val):
            least_val = val
            least_br = key

        if (key == None or key not in main_set):
            others += val
            other_brands[key] = val

    return others, other_brands, most_br, most_val, least_br, least_val


@app.route("/brands_info", methods=['POST', 'GET'])
def brands_info():

    voiv_1 = str(request.form['voiv_1'])
    date1 = str(request.form['date1_input'])
    date2 = str(request.form['date2_input'])
    voiv_2 = str(request.form['voiv_2'])

    if (date2 == "" or date1 == ""):
        flash("You haven't enetered one of the dates")
        return render_template("Cars.html")

    if (not check_correct_date(date1, date2)):
        return render_template("Cars.html")

    voiv_1 = voiv_1.upper()
    voiv_2 = voiv_2.upper()

    if(voiv_1 in short_vers.keys()):
        voiv_1 = short_vers[voiv_1]
    if (voiv_2 in short_vers.keys()):
        voiv_2 = short_vers[voiv_2]


    brand, brand2 = get_brands_info(voiv_1,voiv_2,date1,date2)

    others, other_brands, most_br, most_val, least_br, least_val = brand_info_max_min(brand)
    others2, other_brands2, most_br2, most_val2, least_br2, least_val2 = brand_info_max_min(brand2)

    return render_template("Cars.html", most_val = most_val,most_br = most_br, least_val=least_val,least_br = least_br,
    other_brands = other_brands,audi = brand["AUDI"],toyota=brand["TOYOTA"],volk=brand["VOLKSWAGEN"],hyu=brand["HYUNDAI"],
    merc=brand["MERCEDES-BENZ"],volv=brand["VOLVO"],ren=brand.get("RENAULT",0),bmw=brand["BMW"],ope=brand["OPEL"],citr=brand["CITROEN"],
    hond=brand["HONDA"],sko=brand["SKODA"],ford=brand["FORD"],kia=brand["KIA"],fiat=brand["FIAT"],opel=brand["OPEL"],niss=brand["NISSAN"],
    sea=brand["SEAT"], inne = others,most_val2 = most_val2,most_br2 = most_br2, least_val2=least_val2,least_br2 = least_br2,
    other_brands2 = other_brands2,audi2 = brand2["AUDI"],toyota2=brand2["TOYOTA"],volk2=brand2["VOLKSWAGEN"],hyu2=brand2["HYUNDAI"],
    merc2=brand2["MERCEDES-BENZ"],volv2=brand2["VOLVO"],ren2=brand2.get("RENAULT",0),bmw2=brand2["BMW"],ope2=brand2["OPEL"],citr2=brand2.get("CITROEN",0),
    hond2=brand2["HONDA"],sko2=brand2["SKODA"],ford2=brand2["FORD"],kia2=brand2["KIA"],fiat2=brand2["FIAT"],opel2=brand2["OPEL"],niss2=brand2["NISSAN"],sea2=brand2["SEAT"], inne2 = others2)


def find_max_min(voiv_map, average, max_val, max_id, min_val, min_id):

    for key, res in voiv_map.items():

        if (res > max_val):
            max_val = res
            max_id = key

        if (res < min_val):
            min_val = res
            min_id = key

        average += res


    return average, max_val, max_id, min_val, min_id


def url_look_marks(pre_urls, voiv_count_map):

    counter = 0

    for url in pre_urls:

        while (True):

            urls = []

            stop = False

            for i in range(counter + 1, counter + 2):
                temp_url = url + "&page=" + str(i) + "&limit = 490"
                urls.append(temp_url)

            counter += 1
            shells = (grequests.get(u) for u in urls)
            responses = grequests.map(shells)

            for r in responses:
                temp_dict = json.loads(r.content)
                temp_list = temp_dict["data"]

                if (len(temp_list) == 0):
                    stop = True
                    continue

                if (temp_list[0]["attributes"]["wojewodztwo-kod"] in voiv_count_map):
                    voiv_count_map[temp_list[0]["attributes"]["wojewodztwo-kod"]] += len(temp_list)
                else:
                    voiv_count_map[temp_list[0]["attributes"]["wojewodztwo-kod"]] = len(temp_list)
            if(stop == True):
                break



def get_car_info(brand,model,date1,date2):

    date_1_list = date1.split('-')
    date_2_list = date2.split('-')
    date_1 = ""
    date_2 = ""

    for i in date_1_list:
        if (len(i) == 1 and ord(i) >= ord("0") and ord(i) <= ord("9")):
            i = "0" + i
        date_1 += i

    for i in date_2_list:
        date_2 += i

    rest_url = "&data-od=" + date_1 + "&data-do=" + date_2 + "&filter[marka]=" + \
               str(brand)

    if(model != ""):
        rest_url += "&filter[model]=" + str(model)


    url_prefix = "https://api.cepik.gov.pl/pojazdy?wojewodztwo="
    urls = []

    count = 0
    for key, value in dict.items():
        temp_url = url_prefix + key + "" + rest_url
        urls.append(temp_url)
        count += 1


    voiv_count_map = {}

    for u in urls:
        ur = [u]
        url_look_marks(ur,voiv_count_map)

    max_val = -1
    max_id = -1

    min_val = 10000000000
    min_id = -1

    average = 0

    average, max_val, max_id, min_val, min_id = find_max_min(voiv_count_map,average,max_val,max_id,min_val,min_id)

    sum = average
    average /= 16

    return max_val, min_val, dict[max_id], dict[min_id], average, sum, voiv_count_map

def url_look_brands(url):

    counter = 0
    brand_count_map = {}

    while(True):

        stop = False

        urls = []

        for i in range(counter + 1, counter + 6):
            temp_url = url + "&page="+str(i)+"&limit = 490"

            urls.append(temp_url)
        counter += 5
        shells = (grequests.get(u) for u in urls)
        responses = grequests.map(shells)

        for r in responses:
            temp_dict = json.loads(r.content)
            temp_list = temp_dict["data"]

            if(len(temp_list) == 0):
                stop = True
                continue

            for i in temp_list:

                if (i["attributes"]["marka"] in brand_count_map):
                    brand_count_map[i["attributes"]["marka"]] += 1
                else:
                    brand_count_map[i["attributes"]["marka"]] = 1

        if(stop):
            return brand_count_map



def get_brands_info(input1,input4,input2,input3):

    date_1_list = input2.split('-')
    date_2_list = input3.split('-')
    date_1 = ""
    date_2 = ""

    for i in date_1_list:
        if (len(i) == 1 and ord(i) >= ord("0") and ord(i) <= ord("9")):
            i = "0" + i
        date_1 += i

    for i in date_2_list:
        date_2 += i

    index1 = reverse_dict[input1]
    index2 = reverse_dict[input4]

    url1 = "https://api.cepik.gov.pl/pojazdy?wojewodztwo="+index1+"&data-od="+date_1+"&data-do="+date_2
    url2 = "https://api.cepik.gov.pl/pojazdy?wojewodztwo=" + index2 + "&data-od=" + date_1 + "&data-do=" + date_2

    map1 = url_look_brands(url1)
    map2 = url_look_brands(url2)

    return map1, map2
