import urllib,os
from bs4 import BeautifulSoup
import zipfile
def download(dl_link,file_name = "Orbit.exe"):
    url = "http://sites.google.com"+dl_link
    #/a/ocdsb.ca/orbit_/home/downloads/Latest.build?attredirects=0&d=1"
    #open download link
    u = urllib.urlopen(url)
    #wb is write bytes
    f = open(file_name, 'wb')
    meta = u.info()
    #get file size
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)
    file_size_dl = 0
    block_sz = 2**16
    while True:
        #download part of file (x amount of bytes)
        buffer = u.read(block_sz)
        #if file is done downloading
        if not buffer:
            break
        #add to total downloaded
        file_size_dl += len(buffer)
        f.write(buffer)
        #inform player of total downloaded vs file size
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        #status = status + chr(8)*(len(status)+1)
        os.system("cls")
        print file_name,status

    f.close()
def search(pre_version):
    print "searching. . ."
    site = "https://sites.google.com/a/ocdsb.ca/orbit_/home/downloads"
    #Make websites think you're not a bot
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    #open web page
    req = urllib.Request(site, headers=hdr)
    try:
        #download entire webpage to page. . .
        page = urllib.urlopen(req)
    except urllib.HTTPError, e:
        print e.fp.read()
    soup = BeautifulSoup(page.read(),"html.parser")
    #Locate table body
    a = soup.find_all("tbody")[1]
    #make a list of each element
    a = a.find_all("tr")
    version = pre_version
    for x in a:
        #make sure the table has a file link in it
        if x.find("td", class_="td-file") == None:
            continue
        #find the version number
        ver_num= x.find("td", class_ = "td-desc filecabinet-desc").contents[0]
        if float(ver_num) > version:
            #find file link
            dl_link= x.find("td", class_="td-file").a['href']
            version = float(ver_num)
    if float(version) > pre_version:
        download(dl_link)
        return float(version)
    raw_input("You have the latest Version")
    return pre_version
    #print content
try:
    open("drive_discovery.json","r").close()
    open("HighScores17792.json","r").close()
    open("sheets_discovery.json","r").close()
except:
    download("/a/ocdsb.ca/orbit_/home/downloads/z.b?attredirects=0&amp;d=1",file_name = "z.b")
    zip_ref = zipfile.ZipFile("z.b", 'r')
    zip_ref.extractall()
    zip_ref.close()
    os.remove("z.b")
filename = "settings.txt"
write = []
#make sure there's a settings file
try:
    for ln in open(filename,"r"):
        i = ln.split("=")
        i[0] = i[0].strip().lower()
        if i[0] =="version":
            write+=["version=%s\n"%search(float(i[1].strip()))]
        else:
            write+= [ln]
#if there's no settings file download the latest game build
except:
    write+=["version=%s\n"%search(0)]
#write changes to settings file
fil = open(filename,"w")
for ln in write:
    fil.write(ln)
