
"""data connection establishment"""

import sqlite3
db_filename = 'Search_engine.db'

with sqlite3.connect(db_filename) as conn:
    cursor = conn.cursor()

#Finishing the page ranking algorithm.
def compute_ranks(graph):
    d = 0.8 # damping factor
    numloops = 10
    print "caluculating ranks......."
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            
            #Insert Code Here
            for r in graph:
                if page in graph[r]:
                    newrank = newrank + d * (ranks[r] / len(graph[r]))
            newranks[page] = newrank
        ranks = newranks
    return ranks

def striphtml(data):
    import re
    p = re.compile(r'<.*?>')
    return p.sub('', data)


def crawl_web(seed,max_depth): # returns index, graph of inlinks
    tocrawl = [seed]
    print "crawling "+seed+".........."
    crawled = []
    graph = {}  # <url>, [list of pages it links to]
    index = {}
    next_depth=[]
    depth=0
    while tocrawl and depth<=max_depth: 
        page = tocrawl.pop()
        if page not in crawled:
            content = get_page(page)
            add_page_to_index(index, page, content)
            outlinks = get_all_links(content)
            graph[page] = outlinks
            union(next_depth, outlinks)
            crawled.append(page)
        if not tocrawl:
            tocrawl,next_depth=next_depth,[]
            depth=depth+1
            store_index_in_database(index)
            ranks = compute_ranks(graph)
            store_ranks_in_database(ranks)
            index={}
    return index, graph


def get_page(url):
    import urllib
    try:
        return urllib.urlopen(url).read()
    except:
        return ""
        
    
    
def get_next_target(page):
    start_link = page.find('<a href=')
    if start_link == -1:
        start_link = page.find('href=')
    if start_link == -1: 
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1:end_quote]
    return url, end_quote

def get_all_links(page):
    links = []
    while True:
        url, endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links


def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)

def add_page_to_index(index, url, content):
    #words = content.split()
    import re
    words_l = striphtml(content)
    words = re.findall(r"[\w]+",words_l)
    for word in words:
        word=word.lower()
        print word
        add_to_index(index, word, url)
        
def add_to_index(index, keyword, url):
    if keyword in index:
        if url not in index[keyword]:
            index[keyword].append(url)
    else:
        index[keyword] = [url]

def lookup(index, keyword):
    if keyword in index:
        return index[keyword]
    else:
        return None


"""index storing in database """

def store_index_in_database(ind):

    print "storing kewords and corresponding url's in database"
   
    for indi in ind:
        cursor.execute("""select Url_list from Search_Engine where keyword = '"""+indi+"""'""")
        url_ind=cursor.fetchone()
        if not url_ind:
            #print "hi"
            stt=""
            for i in ind[indi]:
            
                stt=stt+" "+i
            cursor.execute("INSERT INTO Search_Engine (keyword,Url_list) VALUES (?, ?)",
                  (indi,stt))
        else:
                        
            get_str=str(url_ind)#cursor.fetchone())
            db_l=get_str[3:len(get_str)-3].split()
            #print db_l
            union(db_l,ind[indi])
            stt=""
            for i in db_l:
                stt=stt+" "+i
            #print stt
            cursor.execute("UPDATE Search_Engine SET Url_list = '"+stt+"' where keyword='"+indi+"'")
    conn.commit()
    


""" ranks storing in database"""

def store_ranks_in_database(ranks):
    
    for u in ranks:
        cursor.execute("""select rank from Rank_Table where url = '"""+u+"""'""")
        get_r=cursor.fetchone()
        if not get_r:
            #print "hi"
            cursor.execute("INSERT INTO Rank_Table (url,rank) VALUES (?, ?)",
                  (u,ranks[u]))
        else:
            
            get_r=(get_r[0]+ranks[u])/2
            stt=str(get_r)
            cursor.execute("UPDATE Rank_Table SET rank = "+stt+" where url='"+u+"'")
    conn.commit()
    


crawl_web('http://www.google.com',1)# providing url and depth to search


print "process completed"

conn.commit()
conn.close()
    
