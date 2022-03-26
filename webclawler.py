#lib
import os, codecs ,requests
from urllib.parse import urljoin,unquote
from requests.exceptions import HTTPError

#my req header
headers = {
    'User-Agent': 'ap-6110507903',
    'From': 'anucha.pi@ku.th'
}

#set paramiter https:xxx
variable_name = ""
seed_url = 'https://www.ezythaicooking.com/'
defaultlink = 'https://www.ezythaicooking.com/'
fixdomain = 'ezythaicooking' #only domain in ku
urlcount = 0 #start 0
current_url = ''

#set urlstate
errorpage = False
Therobot = False

#set q paramiter
frontier_q = [seed_url]
visited_q = []
Visit = []

#1.Basic Downloader
def get_page(url):
    text = ''
    global headers
    global urlcount
    global errorpage
    global Therobot
    global Thesitemap
    #opening web
    try:
        #send header req set time out 20 sec
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
    except HTTPError as http_err:
        if "robots.txt" in url:
            Therobot = True
        else:
            errorpage = True
            
        if "user-agent:" in url:
            if "sitemap:" in url:
                Thesitemap = True
            else:
                errorpage = True
        else:
            errorpage = True
        #print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        if "robots.txt" in url:
            Therobot = True
        else:
            errorpage = True
            
        if "user-agent:" in url:
            if "sitemap:" in url:
                Thesitemap = True
            else:
                errorpage = True
        else:
            errorpage = True
        #print(f'Other error occurred: {err}')  # Python 3.6
    else:
        #print('Success!')
        if 'robots.txt' not in url:
            urlcount += 1
        text = response.text
    return text.lower()

#Basic Analyzer
#Link Parser
def link_parser(raw_html):
    urls = []
    pattern_start = '<a href="';  pattern_end = '"'
    index = 0;  length = len(raw_html)
    while index < length:
        start = raw_html.find(pattern_start, index)
        if start > 0:
            start = start + len(pattern_start)
            end = raw_html.find(pattern_end, start)
            link = raw_html[start:end]
            if len(link) > 0:
                #if link not in urls:
                #    urls.append(unquote(link))
                #kill #
                if link not in urls and link is not ("#" or ""):
                    urls.append(link)
            index = end
        else:
            break
    return urls

#requirement filter
def filterOut(link):
    if (link.find(".pdf")!=-1 or link.find(".xls")!=-1 or link.find(".docx")!=-1 or link.find(".doc")!=-1 or link.find(".jpg")!=-1 or link.find(".gif")!=-1 or link.find(".png")!=-1 or link.find(".mpg")!=-1) :
        return True
    else:
        return False

#que
def enqueue(links):
    global frontier_q
    for link in links:
        if link not in frontier_q and link not in visited_q:
            frontier_q.append(link)
            
# FIFO queue
def dequeue():
    global frontier_q
    current_url = frontier_q[0]
    frontier_q = frontier_q[1:]
    return current_url

#loop url by que
while (urlcount < 12000):
    try:
        errorpage = False
        Therobot = False
        current_url = dequeue()
        #joinlink
        defaultlink = urljoin(seed_url,current_url)
        #requirement filter
        if filterOut(defaultlink) :
            continue
        #fix domain ku.ac.th
        if fixdomain not in defaultlink:
            continue
        #save true unique url
        if defaultlink not in Visit:
            Visit.append(defaultlink)
        else:
            continue
        #load new page
        raw_html = get_page(defaultlink)
        links = link_parser(raw_html)
        visited_q.append(current_url)
        extracted_links = links
        enqueue(extracted_links)
        if errorpage:
            continue
        
        #check robot.txt
        robot_link = defaultlink+ '/robots.txt'
        raw_robot = get_page(robot_link)
        
        #generate better url
        file_link = defaultlink
        file_link = file_link.replace('https://','')
        file_link = file_link.replace('http://','')
        file_link = file_link.replace('*','{star}')
        file_link = file_link.replace('?','{question}')
        path = 'html(ezyth)/' + file_link
        
        #hierarchial directory structure
        #begin html
        os.makedirs(path, 0o755, exist_ok=True)
        #dummy -> index.html
        abs_file = path + '/index.html'
        f = codecs.open(abs_file,'w','utf-8')
        f.write(raw_html)
        f.close()
        #robot
        if ('user-agent' in raw_robot) and (Therobot == False):
            robot_file = path + '/robots.txt'
            r = codecs.open(robot_file, 'w', 'utf-8')
            r.write(raw_robot)
            r.close()
            ro = codecs.open('html(ezyth)/list_robot.txt', 'a', 'utf-8')
            ro.write(defaultlink+ '\n')
            ro.close()
        print("Number:",urlcount," inque:",len(visited_q)," Link:",defaultlink)
    except :
        skip = dequeue()
