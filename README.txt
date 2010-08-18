===== faux-accio =====

Labeling data for text classification can be a huge pain. In 2004, Davidov et al documented a method for creating "labeled" data sets using the Open Directory Project. They created a software package called Accio to automate this process. Unfortunately, I can find no record of them making the software public.

This project recreates an Accio-like framework in python. The goal is to automate the acquisition of "labeled" data for text classifiers.

===== Mainfest =====

* faux_accio.py
* fa_grabber.py
* convert.py
* content_tree.xml.bz2


===== Setup =====

1a. Go to the Open Directory Project and download the content dump file (http://rdf.dmoz.org/rdf/content.rdf.u8.gz).  This file contains the contents of the ODP.  Unzip it to the project directory.

2a. Run convert.py.  You only need to do this once to create the reduced xml file content_tree.xml.

  --- OR ---

1b. Just unpack content_tree.xml.bz2.  It may be out of date, but will spare you the download and conversion.

===== Command Line Usage =====
faux-accio.py [n] [topic_A] [topic_B] [path] [suffix]

The script runs in one of two modes, depending on how many arguments you pass.

Display Mode:
For zero, one, or two arguments, faux_accio traverses the tree under [topic_A] and displays nodes with at least [n] total sublinks.  That is, the node and its children must have at least [n] nodes together in order to be shown.  This is an easy way to explore the ODP topictree.

If [topic_A] is not given, the search starts at the tree's root.  If [n] is not given it defaults to 50,000.  [n] must be given in order to specify [topic_A].

Ex:
	faux_accio.py
	faux_accio.py 10000
	faux_accio.py 10000 Top/Regional/North_America/United_States/


Download Mode:
If [topic_B] is given, then faux_accio acquires all of the sublinks under [topic_A] and [topic_B] and randomly samples up to [n] from each.  Files are stored to the directory [path]/raw[suffix].  A download manifest is stored to directory [path]/fa_download[suffix].

[path] defaults to the current directory.  If [path] or [path]/raw[suffix] does not exist, it is created. [suffix] defaults to ''.

===== Library Usage =====
faux_accio can also be used as a library.  See fa_grabber.py for an example.

===== Notes =====
* According to the authors' notes, the original Accio randomly selected nodes in the ODP tree for download.  I'm not that nice -- you have to choose your own nodes.  You can use the 

* Downloading runs fast, with support for multiprocessing.

* faux_accio.py uses the lxml library.  If it isn't available, it looks for the (much slower, but easier to install) elementtree library.


