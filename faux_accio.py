import random, re, datetime, pickle, time, csv, urllib2, sys, os
import multiprocessing as mp
try:
    from lxml import etree
except:
    print 'WARNING: lxml not found.  Attempting to from elementtree.  This may be *really* slow.'
    import elementtree.ElementTree as etree
    
########################################################################

source_file ='content_tree.xml'
pool_size = 100
time_inc = 1
time_limit = 5

########################################################################

# This function modified from source at http://code.activestate.com/recipes/473878/ (r1)
# It limits the length of time a given page can take to download -- pages that take longer are ignored
import threading

class InterruptableThread(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.result = None
        self.url = url

    def run(self):
        try:
            text = urllib2.urlopen( self.url ).read()
            length = len(text)
            self.result = ( text, 1 )
        except:
            self.result = ( '', 0 )


def get_page_with_time_limit( url ):
#Returns a tuple: (text, downloadSuceeded)
    global time_limit
    start_time = time.time()

    it = InterruptableThread(url)
    it.start()
    it.join( time_limit )

    end_time = time.time()
    if it.isAlive():
        return ( '', 0 )
    else:
        return it.result

## End of code from http://code.activestate.com/recipes/473878/


def process_page( (classname, classval, classid, url) ):
#This is the workhorse function for this script.
#It downloads a page and saves it, then returns a list with information
    start_time = time.time()
    filename = path+'raw'+suffix+'/c'+str(classval)+'d'+str(classid)+'.html'

    #Attempt to download the site
    try:
            (text, downloadSucceeded) = get_page_with_time_limit( url )
    except:
            downloadSucceeded = 0
    
    download_time = time.time()
    length = len(text)

    #Save the site
    outfile = file(filename,'w')
    outfile.write(text)
    outfile.close()

    end_time = time.time()

    #Create the return array
    download_result = [ classname, classval, classid, url, filename, start_time, download_time, end_time, downloadSucceeded, length ]
#        print '\t', download_result

    return download_result



def recursive_printer( node, min_count ):
#Print out the number of own children, own links, and total links
#for node and all its children with at least min_count total links
    if int(node.attrib['sublink_count']) >= min_count:
        subtopics = 0
        for c in node:
            if c.tag=='Topic': subtopics+=1
        print subtopics, '\t', node.attrib['link_count'], '\t', node.attrib['sublink_count'], '\t', node.attrib['id']
        
        for c in node:
            if c.tag=='Topic': recursive_printer( c, min_count )

def find_topic( topic, root ):
#Locate a Topic node within the tree.  Returns None if the 
    root_id = root.attrib['id']
#	print topic, '\t', root_id
    if not re.match( root_id, topic ): return None

    child_path = re.sub( root_id, '', topic )
    if child_path == '': return root

    #Isolate the next step down the path
    t = child_path.split('/')[1]

    for n in root:
        if n.tag == 'Topic':
#			print '\t', n.attrib['id'], '\t', root_id+'/'+t
            if n.attrib['id'] == root_id+'/'+t:
                return find_topic( topic, n )

    print 'WARNING: Topic node', topic, 'not found!'
    return None

def get_all_child_links( node, exclude=[] ):
#Get a list of all links under a Topic node and all of its children
#The exclude list allows you to exclude subtopics
    links = []
    for n in node:
        if n.tag == 'Topic' and (not n in exclude):
            links = links + get_all_child_links( n )
        if n.tag == 'link': links.append( n.attrib['resource'] )
        if n.tag == 'link1': links.append( n.attrib['resource'] )

    return links


########################################################################


def main( n=50000, topic_A=None, topic_B=None, _path='./', _suffix='' ):
    global path
    global suffix
    path = _path
    suffix = _suffix

    if topic_B == None:   #Display mode
        print 'subtpcs\tlinks\tsublnks\tTopic'
        if topic_A==None:
            recursive_printer( root, n )
        else:
            node_A = find_topic( topic_A, root )
            recursive_printer( node_A, n )

    else:   #Download mode
        print 'Finding nodes in tree...'
        print '\tTopic A:', topic_A
        node_A = find_topic( topic_A, root )
        print '\tTopic B:', topic_B
        node_B = find_topic( topic_B, root )

        #Identify all pages under those nodes
        print 'Identifying pages to crawl...'
        list_A = get_all_child_links( node_A, exclude=[node_B] )
        list_B = get_all_child_links( node_B, exclude=[node_A] )
        print '\tTopic A had', len(list_A), 'sublinks'
        print '\tTopic B had', len(list_B), 'sublinks'

        #sample pages
        print 'Sampling', n, 'pages from each list...'
        random.shuffle( list_A )
        random.shuffle( list_B )

        list_A = list_A[:n]
        list_B = list_B[:n]

#        pickle.dump( (l1, l2), file('lists.pkl', 'w') )
#        (l1, l2) = pickle.load( file('lists.pkl', 'r') )

        print 'Setting up directories...'
        try: os.mkdir( path )
        except: pass
        try: os.mkdir( path+'raw'+suffix+'/' )
        except: pass

        #crawl
        print 'Downloading pages...'
        start_time = datetime.datetime.now()

        my_pool = mp.Pool(pool_size)		#Use pool size to gracefully handle latency
        download_results = my_pool.map_async( process_page, [(topic_A,1,a,list_A[a]) for a in range(len(list_A))] + [(topic_B,2,a,list_B[a]) for a in range(len(list_B))], chunksize=1 )

        k = len(list_A)+len(list_B)
        while not download_results.ready():
            download_results.wait(time_inc)

            percent_complete = 1 - (float(download_results._number_left)/k)
            if percent_complete > 0:
                completion_duration = (datetime.datetime.now() - start_time)*10000/int(10000*percent_complete)
                remaining_time = completion_duration*int(10000*(1-percent_complete))/10000
                completion_time = (start_time+completion_duration).ctime()
            else:
                completion_duration = 'Estimate not available'
                remaining_time = 'Estimate not available'
                completion_time = 'Estimate not available'
            print '\t', round( percent_complete*100, 1 ), '%\t\t', completion_duration, '\t\t', remaining_time, '\t\t', completion_time
        download_results = download_results.get()

        print 'Saving results to csv...'
        csv_file = file(path+'download_info'+suffix+'.csv', 'wb')
        csv_writer = csv.writer( csv_file )
        csv_writer.writerow( [ 'classname', 'classval', 'classid', 'url', 'filename', 'start_time', 'download_time', 'end_time', 'downloadSucceeded', 'length' ] )
        for d in download_results:
            csv_writer.writerow( d )
        csv_file.close()


#load rdf file
print 'Loading rdf file...'
tree = etree.parse(file(source_file, 'r'))
root = tree.getroot()


if __name__ == "__main__":
    try: n=int(sys.argv[1])
    except: n=50000
    try: topic_A=sys.argv[2]
    except: topic_A=None
    try: topic_B=sys.argv[3]
    except: topic_B=None
    try: path=sys.argv[4]
    except: path='./'
    try: suffix=sys.argv[5]
    except: suffix=''

    main( n, topic_A, topic_B, path, suffix )

