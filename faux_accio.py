import random, re, datetime, pickle, time, csv, urllib2
import multiprocessing as mp
try:
    from lxml import etree
except:
    import elementtree.ElementTree as etree
    
########################################################################

pool_size = 100
time_inc = 5
time_limit = 20
path = '/scratch/scratch1/agong/faux_accio/task1/'
class_1 = 'Top/Health'
class_2 = 'Top/Business'


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
    filename = path+'c'+str(classval)+'d'+str(classid)+'.html'

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

def get_all_child_links( node ):
#Get a list of all links under a Topic node and all of its children
    links = []
    for n in node:
        if n.tag == 'Topic': links = links + get_all_child_links( n )
        if n.tag == 'link': links.append( n.attrib['resource'] )
        if n.tag == 'link1': links.append( n.attrib['resource'] )

    return links


########################################################################


def main():
    #load rdf file
    print 'Loading rdf file...'
    tree = etree.parse(file('content_tree.xml', 'r'))
    root = tree.getroot()

    if 1:   #Display mode
        pass
    else:   #Download mode
        print 'FInding nodes in tree...'
        n1 = find_topic( class_1, root )
        n2 = find_topic( class_2, root )

        #Identify all pages under those nodes
        print 'Identifying pages to crawl...'
        l1 = get_all_child_links( n1 )
        l2 = get_all_child_links( n2 )

        #sample pages
        print 'Sampling pages...'
        random.shuffle( l1 )
        random.shuffle( l2 )

        l1 = l1[:2000]
        l2 = l2[:2000]

        print l1[:50]
        print len(l1)
        print len(l2)

        pickle.dump( (l1, l2), file('lists.pkl', 'w') )

        (l1, l2) = pickle.load( file('lists.pkl', 'r') )

        #crawl
        print 'Downloading pages...'

        start_time = datetime.datetime.now()
        my_pool = mp.Pool(pool_size)		#Use pool size to gracefully handle latency
        download_results = my_pool.map_async( process_page, [(class_1,1,a,l1[a]) for a in range(len(l1))] + [(class_2,2,a,l2[a]) for a in range(len(l2))], chunksize=1 )
        n = len(l1)+len(l2)
        while not download_results.ready():
            download_results.wait(time_inc)

            percent_complete = 1 - (float(download_results._number_left)/n)
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
        csv_file = file(path+'master_list.csv', 'wb')
        csv_writer = csv.writer( csv_file )
        csv_writer.writerow( [ 'classname', 'classval', 'classid', 'url', 'filename', 'start_time', 'download_time', 'end_time', 'downloadSucceeded', 'length' ] )
        for d in download_results:
            csv_writer.writerow( d )
        csv_file.close()



if __name__ == "__main__":
    main()

