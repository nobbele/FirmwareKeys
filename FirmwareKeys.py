from bs4 import BeautifulSoup
from urllib import request
import re
import math
from datetime import datetime
import pickle
import sys
import json
import os
sys.setrecursionlimit(10000) # 10000 is an example, try with different values

class lnk:
    def __init__(self, device, href):
        self.device = device
        self.href = "https://www.theiphonewiki.com" + href
    def __str__(self):
        return self.device + "\n" + self.href
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
class CDict(dict):
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
class CList(list):
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
class site:
    def __init__(self, arr):
        self.arr = arr
    def __getitem__(self, i):
        return self.arr[i]
    def __len__(self):
        return len(self.arr)
    def __str__(self):
        return "site object"
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
class db:
    def __init__(self, db):
        self.db = db
    def save(self, filename):
        dbfile = open(filename, 'wb')
        pickle.dump(self.db, dbfile)
    def load(self, filename):
        filehand = open(filename, 'rb')
        self.db = pickle.load(filehand)
class key:
    def __init__(self, iv, key):
        self.key = key
        self.iv = iv
    def __init__(self):
        t = 1 + 1
    def __init__(self, iv):
        self.iv = iv
    def __str__(self):
        return "key: " + self.key + "\niv: " + self.iv
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
class keycoll:
    def __init__(self, keys):
        self.keys = keys
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

def parse(url):
    response = request.urlopen(url)
    webContent = response.read()

    soup = BeautifulSoup(webContent, 'html.parser')
    arr = []
    tables = soup.find_all("table")
    for table in tables:
        if (table['class'] == ['wikitable']):
            no_formatlinks = []
            for data in table.find_all('td'):
                if (data.span == None):
                    no_formatlinks.append(data)
            links = []
            for k in no_formatlinks:
                s = k.get_text()
                s = s.replace("\n", "")
                if "beta" not in s:
                    if (k.a != None):
                        if "redlink=1" not in k.a['href']:
                            links.append(k.a)
            for t in links:
                link = t['href']
                reg = re.search('\(([A-z0-9,]*)\)', link)
                device = reg.group(0)
                device = device.replace("(", "").replace(")", "")
                t = lnk(device, link)
                arr.append(t)
    return site(arr)
def download():
    maxios = 11
    minios = 1
    versions = range(minios, maxios + 1)
    links = CList()
    procentage = 0
    proadd = 100 / len(versions)
    print("Welcome to the theiphonewiki key parser!")
    print("The time it takes for each step will probably increase by every step")
    totaltime = datetime.now()
    for v in versions:
        time = datetime.now()
        link = 'https://www.theiphonewiki.com/wiki/Firmware_Keys/' + str(v) + ".x"
        parsed = parse(link)
        links.append(parsed)
        procentage = procentage + proadd
        nowtime = datetime.now()
        diff = (nowtime - time).total_seconds()
        print(str(math.floor(procentage)) + "%" + " took " + str(diff) + " seconds")
    diff = (datetime.now() - totaltime).total_seconds()
    print("collected " + str(len(links)) + " versions")
    print("took a total of " + str(diff) + " seconds")
    datab = db(links)
    datab.save("links.db")
    return links
def load():
    datab = db([])
    datab.load("links.db")
    return datab.db
def parsekeys(url):
    response = request.urlopen(url)
    webContent = response.read()
    soup = BeautifulSoup(webContent, 'html.parser')
    cont = soup.find(id="mw-content-text")
    keys = cont.find_all('code')
    keydict = {}
    for keydata in keys:
        keyid = keydata['id']
        keyid = keyid.replace("keypage-", "")
        code = keydata.get_text()
        if (keyid == "rootfs-key" or keyid == "gmrootfs-key"):
            keydict['rootfs'] = key(code)
        else:
            arr = keyid.split('-')
            if (arr[1] == 'iv'):
                keydict[arr[0]] = key(code)
            if (arr[1] == 'key'):
                if (keydict[arr[0]].iv != None):
                    keydict[arr[0]].key = code
                else:
                    print("key did not exist")
                    keydict[arr[0]] = key()
                    keydict[arr[0]].key = code
            if (arr[1] == "kbag"):
                if (keydict[arr[0]].iv != None):
                    keydict[arr[0]].kbag = code
                else:
                    print("key did not exist")
                    keydict[arr[0]] = key()
                    keydict[arr[0]].kbag = code
                
    return [keydict, soup.find(id='keypage-build'), soup.find(id='keypage-device'), url]
def mthread(link):
    parsed = parsekeys(link.href)
    v = parsed[1].string
    d = parsed[2].a.string
    coll = keycoll(parsed[0])
    coll.version = v
    coll.device = d
    coll.link = parsed[3]
    return [coll]

def getkeys(links, threads):
    from multiprocessing import Pool
    start = datetime.now()
    p = Pool(threads)
    for dsite in links:
        old = datetime.now()
        keys = CList()
        ##for link in dsite:
        ##    keys.append(mthread(link))
        
        toadd = p.map(mthread, dsite)
        for c in toadd:
            keys.append(c[0])
        
        dsite.keys = keys
        diff = (datetime.now() - old).total_seconds()
        k = dsite[0].href
        if "Heavenly" in k:
            print("ios 1", end=' ')
        elif "Big_Bear" in k:
            print("ios 2", end=' ')
        elif "Wildcat" in k:
            print("ios 3", end=' ')
        elif "Mojave" in k:
            print("ios 4", end=' ')
        elif "Hoodoo" in k:
            print("ios 5", end=' ')
        elif "Innsbruck" in k:
            print("ios 6", end=' ')
        elif "Okemo_12A365b" in k:
            print("ios 7", end=' ')
        elif "Okemo_12A365" in k:
            print("ios 8", end=' ')
        elif "Monarch" in k:
            print("ios 9", end=' ')
        elif "Whitetail" in k:
            print("ios 10", end=' ')
        else:
            print("ios 11")
        print("took " + str(diff) + " seconds")
        print("Got " + str(len(dsite.keys)) + " keys")
    print("Finished!")
    try:
        datab = db(links)
        datab.save("keys.db")
    except MemoryError:
        print("Memory Error, not saving")
    diff = (datetime.now() - start).total_seconds()
    print("key grabbing took " + str(diff) + " seconds")
    return links


def downloadparse(threads):
    return getkeys(download(), threads)
def loadparse(threads):
    return getkeys(load(), threads)
def loadkeys():
    datab = db('')
    datab.load('keys.db')
keys = []

if __name__ == '__main__':
    def start(dlorparse):
        threads = 70
        keys = CList()
        if dlorparse == "dl":
            print("Downloading keys")
            keys = downloadparse(threads)
        else:
            print("Loading keys")
            keys = loadparse(threads)
        dic = CDict()
        for k in keys:
            if (k != None):
                for b in k.keys:
                    if (b != None and b.device != None and b.version != None):
                        regex = re.search('([A-z0-9]*,[0-9])', b.link)
                        ##\(([A-z0-9,]*)\)
                        ## ([A-z0-9]*,[0-9]) Improved regex?
                        v = ""
                        if (regex != None):
                            v = regex.group(0)
                        else:
                            if (b.device == "iPhone"):
                                v = "iPhone1,1"
                            elif (b.device == "iPod touch"):
                                v = "iPod1,1"
                            elif (b.device == "iPad"):
                                v = "iPad1,1"
                            else:
                                print(b.link)
                                v = "Unknown device"
                        tag = v + " " + b.version
                        
                        dic[tag] = keycoll(b.keys)
        count = len(dic)
        print("Grabbed a total of " + str(count) + " keys!")
        stringdata = dic.toJSON()
        
        with open('keys.json', 'w') as fp:
            fp.write(stringdata)
        print("JSON formatted list of keys are stored in keys.json")
        return dic
    def lload():
        s = ""
        with open('keys.json', 'r') as fp:
            s = json.load(fp)
        return s
            
