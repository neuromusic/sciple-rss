#!/usr/local/bin/python2.7
# -*- coding: UTF8 -*-
# from http://sciple.org/code/rss-management/

from string import Template
from xml.etree.ElementTree import ElementTree
from urllib import urlopen
import time
import random as rn # used for testing the rank (to remove)
import numpy as np

class Feed(object):
    """
    Version 2 [28 May 2012] by Leonardo Restivo

    Example usage:
    -------------------------------
    newFeeds = {'Hippocampus':'http://onlinelibrary.wiley.com/rss/journal/10.1002/%28ISSN%291098-1063',\
             'JN':'http://www.jneurosci.org/rss/current.xml',\
             'PlosOne':'http://feeds.plos.org/plosone/PLoSONE?format=xml',\
             'Science':'http://www.sciencemag.org/rss/current.xml',\
             'Nature':'http://feeds.nature.com/nature/rss/current?format=xml',\
             'L&M':'http://learnmem.cshlp.org/rss/current.xml',\
             'Neuron':'http://www.cell.com/rssFeed/neuron/rss.NewIssueAndArticles.xml',\
             'Plos.Comp':'http://feeds.plos.org/ploscompbiol/NewArticles?format=xml',\
             'Neurobiol Learn&Mem':'http://feeds.sciencedirect.com/publication/science/10747427',\
             'EJN':'http://onlinelibrary.wiley.com/rss/journal/10.1111/(ISSN)1460-9568',\
             'PNAS':'http://www.pnas.org/rss/current.xml',\
             'FiN':'http://feedity.com/frontiersin-org/UFZXVVdQ.rss',\
             'Cell':'http://www.cell.com/rssFeed/Cell/rss.NewIssueAndArticles.xml',\
             'Nat.Neurosci':'http://feeds.nature.com/neuro/rss/current?format=xml',\
             'Nat.Neurosci-AOP':'http://feeds.nature.com/neuro/rss/aop?format=xml'}

    myProfile= {'spine': 0.010551948051948052, 'neuron': 0.012987012987012988, 'consolidation': 0.008116883116883116, 'brain': 0.007305194805194805, 'neurogenesi': 0.016233766233766232, 'learning': 0.012987012987012988, 'memory': 0.030032467532467532, 'hippocampu': 0.007305194805194805, 'adult': 0.01461038961038961}
    feeds = Feed(newFeeds,myProfile)
    feeds.parse_rss()
    feeds.fillFeedList()
    feeds.writeJSON('database.js')
    -------------------------------
    """
    def __init__(self,feed_url,myId):
        self.feed_url = feed_url
        self.myId = myId
        self.rsslist = []
        self.localtime = time.asctime( time.localtime(time.time()) )
        self.output=[]

    def parse_rss(self):
        print """'
        \033[91m
        *----------------------------------------------------*
        |                                                    |
        |              Retrieve and Rank feeds               |
        |                                                    |
        *----------------------------------------------------*
        \033[0m
        """
        print self.localtime,'\n'
        for f in self.feed_url:
            rss = ElementTree(file = urlopen(self.feed_url[f]))
            print 'retrieving feeds from:',f
            root = rss.getroot()
            for item in[ x for x in root.getiterator() if "item" in x.tag or "entry"in x.tag]:
                rssdict = {}
                for elem in item.getiterator():
                    for k in [ 'link', 'title', 'description', 'creator','date' ]:
                        if k in elem.tag:
                            rssdict[k] = elem.text
                            rssdict['journal'] = f
                        else:
                            rssdict[k] = rssdict.get(k, "N/A")
                self.rsslist.append(rssdict)

    def rankRSS(self,singleFeed):
        """
        myID must be a list
        """
        count=0
        for i in self.myId:
            if i in singleFeed:
                count+=1*self.myId[i]
        # return the ASCII code for star ('&#9733'):
#        return ((np.floor(count*100))*'&#9733')
        return(str(count)[:5])

    def fillFeedList(self):    
        a = Template(""""item$counter":{"title":"$title","content":"$content","journal":"$journal","link":"$link","creator":"$creator","date":"$date","rank":"$rank"},
                     """)
        counter=-1
        print 'ranking articles...'
        for i in self.rsslist:
            if  i['title'].encode('ascii', 'ignore')!= 'N/A':
                description_raw=str(i['description'].encode('ascii', 'ignore')if i['description'] else i['description']).strip().lstrip('<p>').rstrip('</p>').rstrip('\r\n')
                description = description_raw.replace('\"','')

                title_raw = str(i['title'].encode('ascii', 'ignore') if i['title'] else i['title'])
                title = title_raw.replace('\"','')

                journal = str(i['journal'])

                creator_raw = str(i['creator'].encode('ascii', 'ignore') if i['creator'] else i['creator'])
                creator = creator_raw.replace('\"','')

                date_raw = str(i['date'].encode('ascii', 'ignore') if i['date'] else i['date'])
                date = date_raw.replace('\"','')

                rank = self.rankRSS(description)

                counter+=1        
                self.output.append(a.substitute(counter=counter,title=title,content=description,journal=journal,link=i['link'],creator=creator,date=date,rank=rank))

    def writeJSON(self,fileName):
        outfileX = open('Output/'+fileName,"w")
        outfileX.write('var update_date ="<i style=color:#5C5C5C;>Last update: '+str(self.localtime)+'";\n')
        outfileX.write('var journals = {')
        print '\n  writing feeds to file: Output/\033[94m',fileName+'\033[0m'
        for i in self.output:
            outfileX.write(str(i))
        outfileX.write('};')
        outfileX.close()
        print '..DONE\n'
        print'-'*15,'\n'

    def outputRSS(self,field):
        for i in self.rsslist:
            try:
                print i[field]
            except KeyError:
                pass