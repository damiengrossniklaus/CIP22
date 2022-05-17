import time
import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

start = time.time()

urls_BE = ['https://flatfox.ch/de/search/?east=8.528568&north=47.497424&object_category=APARTMENT&object_category=HOUSE&offer_type=RENT&query=Kanton%20Bern&south=46.038148&west=6.957679']

def get_coords(url):
    """Function to get coordinates out of flatfox-url."""
    coords = {}
    elm_link = url.split('search/?')  # only consider part after base url
    cardinal_points = ['north', 'west', 'south', 'east']
    elm_link1 = elm_link[1].split('&')  # elements are connected with '&'
    for el in elm_link1:
        els = el.split('=')
        key, value = els[0], els[1]
        coords[key] = value

    coords2 = {key: float(coords[key]) for key in
               cardinal_points}  # dict comprehension to keep only coordinates and exclude other query elements.
    return coords2


def transform_coords(url):
    """Split map in 4 quadrants part 1; return resulting list of coordinates for subsections."""
    co_old = get_coords(url)
    nor = co_old['north']
    wes = co_old['west']
    sou = co_old['south']
    eas = co_old['east']
    nor_t = sou + (nor - sou) / 2
    wes_t = eas + (wes - eas) / 2
    sou_t = nor + (sou - nor) / 2
    eas_t = wes + (eas - wes) / 2
    # define new coordinates for quadrants (e.g. first is upper-left, northwestern quadrant)
    q_nw = {'north': nor,
            'west': wes,
            'south': sou_t,
            'east': eas_t}
    q_ne = {'north': nor,
            'west': wes_t,
            'south': sou_t,
            'east': eas}
    q_sw = {'north': nor_t,
            'west': wes,
            'south': sou,
            'east': eas_t}
    q_se = {'north': nor_t,
            'west': wes_t,
            'south': sou,
            'east': eas}
    coords_quads = [q_nw, q_ne, q_sw, q_se]
    return coords_quads


def split_map(url):
    """Split map into 4 quadrants part 2; automatically generate links for the new quadrants.
    Rturn list of 4 new links."""
    coords_url = transform_coords(url)

    card_dir = ['north', 'west', 'south', 'east']

    links_quad = []
    for j in range(4):
        url2 = url
        for i in card_dir:
            pattern = f'{i}=\d+.\d+'  # regex pattern to find the coordinates in link,
                                    # e.g. '...north=47.315...' for north, west, south & east
            url2 = re.sub(pattern, f'{i}={str(coords_url[j][i])}', url2) # replace with new coordinates
        links_quad.append(url2)
    return links_quad


# set warning count:
count_warn = 1

def check_links(map_links):
    """Evaluate for a list of links if the map of the respective link displays more than 400 elements (warning)"""
    global count_warn
    count_warn = 0
    links_res = []
    for link in map_links:
        driver.get(link)
        time.sleep(4)
        try:
            warn = driver.find_element(by=By.XPATH,
                                       value='//*[@id="flat-search-widget"]/div/div[2]/div[1]/div/span/div').text
            count_warn += 1

            new_links = split_map(link)
            for i in new_links:
                links_res.append(i)
        except:
            links_res.append(link)  # append the link if there is no warning
    return links_res


if __name__ == "__main__":

    # uncomment for headless selenium:
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1536,864")    # Window size is important for the shape of the map
    driver = webdriver.Chrome(options=chrome_options)

    while count_warn != 0:  # end loop as soon as no link returns a > 400 warning
        urls_BE = check_links(urls_BE)

    # get current date and time:
    now = datetime.datetime.now()
    now_string = now.strftime("%d_%m_%Y_%H%M")

    # write list to .txt file:
    with open(f'../Data/src/C_map_links_{now_string}.txt', 'w') as f:
        for s in urls_BE:
            f.write(s + '\n')

    time.sleep(4)
    driver.quit()

    end = time.time()
    print(f"Done. The links of the maps were generated. \nThey are written in the file 'map_links_{now_string}.txt'",
          f"\n elapsed time: ", round(((end - start) / 60), 2), "(min)")
