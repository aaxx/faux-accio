===== faux-accio =====

Labeling data for text classification can be a huge pain. In 2004, Davidov et al documented a method for creating "labeled" data sets using the Open Directory Project. They created a software package called Accio to automate this process. Unfortunately, I can find no record of them making the software public.

This project recreates an Accio-like framework in python. The goal is to automate the acquisition of "labeled" data for text classifiers.

===== Setup =====

1. Go to the Open Directory Project and download the content dump file (http://rdf.dmoz.org/rdf/content.rdf.u8.gz).  This file contains the contents of the ODP.  Unzip it to the project directory.

2. Run convert.py.  You only need to do this once to create the reduced xml file content_tree.xml.

===== Usage =====