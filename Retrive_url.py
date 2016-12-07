def lucky_search(urls,ranks):
            
    rank_st=ranks
    page_st=urls
    for cand in range(len(rank_st)): 
        
        for candidate in range(cand+1,len(rank_st)):
            if rank_st[candidate]> rank_st[cand]:
                rank_st[candidate],rank_st[cand]=rank_st[cand],rank_st[candidate]
                page_st[candidate],page_st[cand]=page_st[cand],page_st[candidate]
        
    return page_st,rank_st




key1 = raw_input("Enter keyword to search:")
import re
keys=key1.lower().split()
keys = re.findall(r"[\w]+",key1)
print keys
import sqlite3

db_filename = 'Search_engine.db'

with sqlite3.connect(db_filename) as conn:
    cursor = conn.cursor()
url_list=[]
for key in keys:
    #print "\n\nurls for"+key+"is\n"
    cursor.execute("""
        select Url_list from Search_Engine where keyword = '"""+key+"""'""")

    u_list = cursor.fetchone()
    if u_list:
        res=str(u_list)
        res=res[3:len(res)-3]
        res_list=res.split()
        rank_list=[]
        for i in res_list:
            url_list.append(i)

url_dic={}
for word in url_list:
    if word in url_dic:
        url_dic[word] += 1
    else:
        url_dic[word] = 1

import collections        
url_dic_sort=collections.OrderedDict()
for w in sorted(url_dic, key=url_dic.get, reverse=True):
    #print w+":",url_dic[w]
    if url_dic[w] in url_dic_sort:
        url_dic_sort[url_dic[w]].append(w)
    else:
        url_dic_sort[url_dic[w]]=[w]
url_rank_frequent=[]
for i in url_dic_sort:
    #print i,url_dic_sort[i]
    rank_list=[]
    for j in url_dic_sort[i]:
        cursor.execute("""
            select rank from Rank_Table where url = '"""+j+"""'""")
        rank=cursor.fetchone()
        rank_list.append(float(str(rank)[1:len(str(rank))-3]))
            
    u_sorted,r_sorted=lucky_search(url_dic_sort[i],rank_list)
    #for j in range(len(u_sorted)):
    #    print u_sorted[j],r_sorted[j]
        
    for j in u_sorted:
        url_rank_frequent.append(j)

        
if url_rank_frequent:
    for i in url_rank_frequent:
        print i
else:
    print '"""did not match any document with the keyword---'+key+'"""'
conn.close()

