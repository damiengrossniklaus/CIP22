import pandas as pd
import datetime
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import os
from headers import header

start = time.time()
s = HTMLSession()
header = header()


# uncomment for headless selenium:
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1000,500")
driver = webdriver.Chrome(options=chrome_options)


# get information from tables function: 
def get_table_infos(url, which):
    """Function that extracts all information and converts to dict from tables on the object websites."""
    res_url = s.get(url, headers=header)
    sp = BeautifulSoup(res_url.text, "lxml")

    if which == 'rent':
        idx = 0
    elif which == 'details':
        idx = 1

    table = sp.findAll('table')[idx].findAll('td')
    table_str = [i.text.strip() for i in table]

    dict_tab = {}
    for x in range(0, len(table_str), 2):
        dict_tab[table_str[x]] = table_str[x + 1]

    return dict_tab


def get_attrs(url):
    """Function that gets attributes of objects and writes it in a dict."""
    res_url = s.get(url)
    sp = BeautifulSoup(res_url.text, "lxml")
    address = ""

    # get title:
    title = sp.find('h1').text.strip()

    # get street, plz, and city
    try:
        subtitle = sp.find('h2').text.strip()
        address = subtitle.split(" - ")[0]
    except:
        subtitle = 'No subtitle'
    # try to get street, plz and city:
    try:
        street = address.split(", ")[0].strip()
        city_and_code = address.split(", ")[1].strip()
        plz = re.findall(r"\d\d\d\d", city_and_code)[0]         # regex to find plz
        city = re.sub("\d\d\d\d", "", city_and_code).strip()    # regex to find city
    
    except:
        try:
            # if street is missing, still get plz and city:
            plz = re.findall(r"\d\d\d\d", address)[0]
            city = re.sub("\d\d\d\d", "", address).strip()
            street = None
        except:
            place = address
            plz = None
            street = None
            city = None
            address = None

    # get infos about rent
    try:
        rent_dic = get_table_infos(url, which='rent')
    except:
        rent_dic = {}

    # get infos about details of object:
    try:
        details_dic = get_table_infos(url, which='details')
    except:
        details_dic = {}

    # get description information
    # title:
    try:
        desc_title = sp.find('strong', class_='user-generated-content').text
    except:
        desc_title = " ##NoTitle## "    
    # description:
    try:
        desc = sp.find('div', class_='markdown').text.strip()
    except:
        desc = " ##NoDesc## "

    # combine them to have all information of description:
    description = desc_title + ' ##end_title## ' + desc  # add string between to be able to separate later

    # create dictionary with attributes:
    rent_object = {
        'title: ': title,
        'plz': plz,
        'street': street,
        'place': city,
        'description': description,
        'url': url
    }

    # update the dict with renting, infos and description information:
    rent_object.update(rent_dic)
    rent_object.update(details_dic)
    rent_object.update()

    return rent_object

base_url = 'https://flatfox.ch'

def get_object_links(url):
    """Function that gets the links of the single objects."""
    driver.get(url)
    time.sleep(6)

    btn_name = driver.find_element(by=By.XPATH,
                                   value='//*[@id="flat-search-widget"]/div/div[2]/div[2]/div[2]/button/span').text
    btn_more = driver.find_element(by=By.XPATH,
                                   value='// *[ @ id = "flat-search-widget"] / div / div[2] / div[2] / div[2] / button')

    # while loop that scrolls through the results until the end (button "Mehr anzeigen" not shown anymore):
    while btn_name == "Mehr anzeigen":
        driver.execute_script("window.scrollBy(0,1080)", "")    # scroll
        btn_more.click()                                        # click button to show more results
        btn_name = driver.find_element(by=By.XPATH,
                                       value='//*[@id="flat-search-widget"]/div/div[2]/div[2]/div[2]/button/span').text
        time.sleep(2)

    # uncomment to show number of objects:
    # leng = len(driver.find_elements(by=By.CLASS_NAME, value='listing-thumb'))
    # print(f"Total number of objects: {leng}")

    # get the url of all the objects displayed:
    my_page_source = driver.page_source

    # get soup:
    soup = BeautifulSoup(my_page_source, 'lxml')

    # find all
    obj_list = soup.find_all('div', class_='listing-thumb')

    # append all links of this page: 
    obj_links = []
    for obj in obj_list:
        for link in obj.find_all('a', href=True):
            obj_links.append(base_url + link['href'])

    return obj_links



def name_curr_file(file_string='C_map_links_', filetype = '.txt', src=''):
    """Get the filename of the most current file in the directory."""
    filelist = []
    for file in os.listdir("../Data/src"):
        if file.startswith(f'{file_string}'):
            filelist.append(re.sub(f"{src}{filetype}", "", file))

    filelist_dates = [re.sub(f'{file_string}', "", element) for element in filelist]

    list_date_objects = []
    for obj in filelist_dates:
        list_date_objects.append(datetime.datetime.strptime(obj, '%d_%m_%Y_%H%M'))

    curr_object = max(list_date_objects)
    curr_string = curr_object.strftime("%d_%m_%Y_%H%M")
    curr_file_str = f'{file_string}{curr_string}{src}{filetype}'
    return curr_file_str


def scrape_flatfox():
    """Scraping-Function, i.e. the function that takes all the links of the maps, then 
    gets all single objects links and iterates through them, retrieving all information."""

    # get filename of the most current file:
    curr_map_links = name_curr_file()
    # get map links and store them in list:
    with open(f'../Data/src/{curr_map_links}', 'r') as f:
        link_list = [line.rstrip('\n') for line in f]

    # get all single object links and store them in list:
    obj_list_links = []
    for link in link_list:
        temp_href_list = get_object_links(link)
        obj_list_links.append(temp_href_list) # result: list of lists

    all_single_links = list(
        set([item for sublist in obj_list_links for item in sublist]))  # make one list and remove duplicates
    counter = 0
    for i in all_single_links:
        counter += 1
        print(counter, " ", i)

    # get date and time
    now = datetime.datetime.now()
    now_string = now.strftime("%d_%m_%Y_%H%M")


    # uncomment below if a file with the single links should be written:
    # with open(f'single_object_links{now_string}.txt', 'w') as f:
    #    for s in all_single_links:
    #        f.write(s + '\n')
    #
    # with open("single_object_links29_04_2022_0927.txt", 'r') as f:
    #     single_obj_link_list = [line.rstrip('\n') for line in f]

    time.sleep(5)
    driver.quit()

    single_obj_link_list = all_single_links

    di_attrs = []
    counter_obj = 0
    for i in single_obj_link_list:
        counter_obj += 1
        di_attrs.append(get_attrs(i))
        print(f'{counter_obj} objects scraped!')

    df_out = pd.DataFrame(di_attrs)
    df_out.to_csv(f'../Data/src/C_flatfox_{now_string}_src.csv')

    end = time.time()

    print("Done. elapsed time: ", round(((end - start) / 60),2), "(min)")


if __name__ == "__main__":
    scrape_flatfox()



