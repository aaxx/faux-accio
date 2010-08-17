#This script converts content.rdf.u8 to an xml file usable by faux_accio.py

import random, re
from lxml import etree
from copy import deepcopy

def recursive_link_counter( node ):
	links = 0
	for c in node:
		if c.tag=='link' or c.tag=='link1': links += 1
		if c.tag=='Topic': recursive_link_counter( c )
	node.attrib['link_count'] = str(links)

def recursive_sub_link_counter( node ):
	links = 0
	for c in node:
		if c.tag=='link' or c.tag=='link1': links += 1
		if c.tag=='Topic': links += recursive_sub_link_counter( c )
	node.attrib['sublink_count'] = str(links)
	return links

print 'Stripping content.rdf to essential xml...'
infile = file('content.rdf.u8', 'r')
outfile = file('content.xml', 'w' )

outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
outfile.write('<RDF>\n')

count = 0
on = False
while 1:
        l = infile.readline()

	l = re.sub( 'Topic r:id=', 'Topic id=', l )
	l = re.sub( 'link r:resource=', 'link resource=', l )
	l = re.sub( 'link1 r:resource=', 'link1 resource=', l )

	if not l: break
	if re.search( '<Topic', l ): on = True
	if re.search( '</Topic', l ):
		outfile.write( l )
		on = False
	if on: outfile.write( l )

	count += 1
	if not count % 100000: print '\t', count, 'lines processed...'

outfile.write('</RDF>\n')
outfile.close()


print 'Restructuring xml as tree...'
T = {}
tree = etree.parse(file('content.xml', 'r'))
root = tree.getroot()
#All topics are listed as nodes under root.
#We want to restructure as a proper tree

newroot = etree.Element('Topic')
T['Top'] = newroot
newroot.attrib['id'] = 'Top'

count = 0
for n in root:
	name = n.get('id')
	parent = '/'.join( name.split('/')[:-1] )
	T[name] = n
	T[parent].append( n ) 
#	print name + '\t' + parent + '\t' + str( parent in T )

	count += 1
	if not count % 50000: print '\t', count, 'lines processed...'

print 'Counting links by node...'
recursive_link_counter( newroot )
recursive_sub_link_counter( newroot )

print 'Saving xml tree... '
outfile = file( 'content_tree.xml', 'w' )
outfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
outfile.write( etree.tostring( newroot, pretty_print=True ) )
outfile.close()


print 'Printing info for major nodes...'
newroot = etree.parse(file('content_tree.xml', 'r')).getroot()
recursive_printer( newroot, 10000 )
