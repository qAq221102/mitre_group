import requests
from bs4 import BeautifulSoup
import csv
import time

'''here set your interested version and number of groups'''
version = 16  # set version
start_point = 0  # set start point of index
num_interval = 10  # set number of groups
ALL_FLAG = False  # want all data then set True


groups_url = f"https://attack.mitre.org/versions/v{version}/groups/"
result_file = f'result_v{version}_{start_point+1}to{start_point+num_interval}.csv'

groups_html = None
groups_soup = None
groups_tboby = None
groups_tr = None

target_html = None
target_soup = None

start_time = 0
end_time = 0


def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"{url} fetch html failed: {e}")
        return None


def get_soup(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup


def find_tbody(soup):
    tbody = soup.find("tbody")
    return tbody


def find_tr(tbody):
    tr = tbody.find_all("tr")
    return tr


def get_target_info(tr):
    global num_interval, start_point

    def create_csv(filename):
        # write haeder
        with open(filename, 'w', newline='', encoding='utf-8') as rst_csv:
            writer = csv.writer(rst_csv)
            header = ['Index', 'ID', 'Group',
                               'URL', 'References', 'Time', 'PDF']
            writer.writerow(header)

    def write_result(data_list, filename):
        # append data
        with open(filename, 'a', newline='', encoding='utf-8') as rst_csv:
            writer = csv.writer(rst_csv)
            data_list[3] = f'=HYPERLINK("{data_list[3]}", "{data_list[3]}")'
            writer.writerow(data_list)

    def go_target_web(index):  # append info to list for write csv
        target_url = groups_url+id
        target_html = fetch_html(target_url)
        target_soup = get_soup(target_html)
        target_a = target_soup.find_all("a", class_="external text")
        for a in target_a:
            src_url = a['href']
            target_text = a.text.strip()
            src_pdf = ''
            if '.pdf' in src_url.lower():
                src_pdf = 'O'
            list = [index, id, name, src_url, target_text,
                    target_text.split("Retrieved")[1], src_pdf]
            write_result(list, result_file)
            index += 1
        print(f'{target_url} - fetch success')
        return index

    if ALL_FLAG:
        start_point = 0
        num_interval = len(tr)
    # check requirement
    if num_interval-start_point <= len(tr):
        total_index = 0
        create_csv(result_file)
        for row_index, r in enumerate(tr):
            if start_point <= row_index < num_interval:
                td = r.find_all("td")
                id = ''
                name = ''
                for j, d in enumerate(td):
                    str = d.text.strip()
                    if j == 0:
                        id = str
                    elif j == 1:
                        name = str
                    else:
                        break
                total_index = go_target_web(total_index)
            elif row_index > start_point+num_interval:
                print('---------------------------------')
                print(f"wrote {total_index} rows of data")
                break
    else:
        print('interested num of groups are out of range')


def main():
    print(f'start crawler, target: MITRE ATT&CK groups')
    print(f'version: {version}')
    print(f'start index: {start_point}')
    print(f'interval: {num_interval}')
    print('-------------------------------------------')
    start_time = time.time()
    groups_html = fetch_html(groups_url)
    groups_soup = get_soup(groups_html)
    groups_tboby = find_tbody(groups_soup)
    groups_tr = find_tr(groups_tboby)
    get_target_info(groups_tr)
    end_time = time.time()
    print(f'All Done, it takes {end_time-start_time:.2f}s')


if __name__ == "__main__":
    main()
