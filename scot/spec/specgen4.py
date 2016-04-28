
#
# SpecGen code adapted to be independent of a particular vocabulary (e.g., FOAF)
# <http://sw.deri.org/svn/sw/2005/08/sioc/ontology/spec/specgen4.py>
# 
# This software is licensed under the terms of the MIT License.
#
# Copyright 2008 Uldis Bojars <captsolo@gmail.com>
# Copyright 2008 Christopher Schmidt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__all__ = [ 'main' ]
 
import sys, time, re, urllib, getopt
import RDF

foaf = RDF.NS("http://xmlns.com/foaf/0.1/")
dc = RDF.NS('http://purl.org/dc/elements/1.1/')
rdf = RDF.NS('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
rdfs = RDF.NS('http://www.w3.org/2000/01/rdf-schema#')
owl = RDF.NS('http://www.w3.org/2002/07/owl#')
vs = RDF.NS('http://www.w3.org/2003/06/sw-vocab-status/ns#')
xfoaf = RDF.NS('http://www.foafrealm.org/xfoaf/0.1/')
mont = RDF.NS('http://www.marcont.org/ontology/marcont.owl#')
# add your namespaces here

classranges = {}
classdomains = {}

termdir = './doc'

# namespace for which the spec is being generated. 
# spec_url = "http://xmlns.com/foaf/0.1/"
# spec_pre = "foaf"
spec_url = "http://rdfs.org/scot/ns#"
spec_pre = "scot"

spec_ns = RDF.NS(spec_url)

ns_list = { "http://xmlns.com/foaf/0.1/" : "foaf", 
            'http://purl.org/dc/elements/1.1/' : "dc",
            'http://purl.org/dc/terms/' : "dcterms",
            'http://usefulinc.com/ns/doap#' : 'doap',
	    'http://www.w3.org/1999/02/22-rdf-syntax-ns#' : "rdf",
	    'http://www.w3.org/2000/01/rdf-schema#' : "rdfs",
	    'http://www.w3.org/2002/07/owl#' : "owl",
            'http://www.w3.org/2001/XMLSchema#' : 'xsd',
  	    'http://www.w3.org/2003/06/sw-vocab-status/ns#' : "status",
	    'http://purl.org/rss/1.0/modules/content/' : "content",
	    'http://rdfs.org/scot/ns#' : "scot",
	    'http://rdfs.org/sioc/ns#' : "sioc" }

def niceName( uri = None ):
   if uri is None:
      return
   
   regexp = re.compile( "^(.*[/#])([^/#]+)$" )
   rez = regexp.search( uri )
   pref = rez.group(1)
   
   return ns_list.get(pref, pref) + ":" + rez.group(2)

def setTermDir(directory):
    global termdir
    termdir = directory

def termlink(string):
    """FOAF specific: function which replaces <code>foaf:*</code> with a 
    link to the term in the document."""
    return re.sub(r"<code>" + spec_pre + r":(\w+)</code>", r"""<code><a href="#term_\1">""" + spec_pre + r""":\1</a></code>""", string)    

def return_name(m, urinode):
    "Trims the FOAF namespace out of a term to give a name to the term."
    return str(urinode.uri).replace(spec_url, "")

def get_rdfs(m, urinode):
    "Returns label and comment given an RDF.Node with a URI in it"
    comment = ''
    label = ''
    l = m.find_statements(RDF.Statement(urinode, rdfs.label, None))
    if l.current():
        label = l.current().object.literal_value['string']
    c = m.find_statements(RDF.Statement(urinode, rdfs.comment, None))
    if c.current():
        comment = c.current().object.literal_value['string']
    return label, comment

def get_status(m, urinode):
    "Returns the status text for a term."
    status = ''
    s = m.find_statements(RDF.Statement(urinode, vs.term_status, None))
    if s.current():
        return s.current().object.literal_value['string']

def htmlDocInfo( t ):
    """Opens a file based on the term name (t) and termdir directory (global).
       Reads in the file, and returns a linkified version of it."""
    doc = ""
    try:
        f = open("%s/%s.en" % (termdir, t), "r")
        doc = f.read()
        doc = termlink(doc)
    except:
        return "" 	# "<p>No detailed documentation for this term.</p>"
    return doc

def owlVersionInfo(m):
    v = m.find_statements(RDF.Statement(None, owl.versionInfo, None))
    if v.current():
        return v.current().object.literal_value['string']
    else:
        return ""

def rdfsPropertyInfo(term,m):
    """Generate HTML for properties: Domain, range, status."""
    doc = ""
    range = ""
    domain = ""

    # Find subPropertyOf information

    o = m.find_statements( RDF.Statement(term, rdfs.subPropertyOf, None) )
    if o.current():
        doc += "\t<tr><th>sub-property-of:</th>"
	rlist = ''
	
        for st in o:
	    k = str( st.object.uri )
            if (spec_url in k):
                k = """<a href="#term_%s">%s</a>""" % (k.replace(spec_url, ""), niceName(k))
            else:
                k = """<a href="%s">%s</a>""" % (k, niceName(k))
	    rlist += "%s " % k
        doc += "\n\t<td>%s</td></tr>\n" % rlist

    # domain and range stuff (properties only)
    d = m.find_statements(RDF.Statement(term, rdfs.domain, None))
    if d.current():
        domain = d.current().object.uri
        domain = str(domain)
    else:
        domain = ""
    r = m.find_statements(RDF.Statement(term, rdfs.range, None))
    if r.current():
        range = r.current().object.uri
        range = str(range)
    if domain:
        # NOTE can add a warning of multiple rdfs domains / ranges
        if (spec_url in domain):
            domain = """<a href="#term_%s">%s</a>""" % (domain.replace(spec_url, ""), niceName(domain))
        else:
            domain = """<a href="%s">%s</a>""" % (domain, niceName(domain))
        doc += "\t<tr><th>Domain:</th>\n\t<td>%s</td></tr>\n" % domain
    
    if range:
        if (spec_url in range):
            range = """<a href="#term_%s">%s</a>""" % (range.replace(spec_url, ""), niceName(range))
        else:
            range = """<a href="%s">%s</a>""" % (range, niceName(range))
        doc += "\t<tr><th>Range:</th>\n\t<td>%s</td></tr>\n" % range
    return doc

def rdfsClassInfo(term,m):
    """Generate rdfs-type information for Classes: ranges, and domains."""
    global classranges
    global classdomains
    doc = ""

    # Find subClassOf information

    o = m.find_statements( RDF.Statement(term, rdfs.subClassOf, None) )
    if o.current():
        doc += "\t<tr><th>sub-class-of:</th>"
	rlist = ''
	
        for st in o:
	    k = str( st.object.uri )
            if (spec_url in k):
                k = """<a href="#term_%s">%s</a>""" % (k.replace(spec_url, ""), niceName(k))
            else:
                k = """<a href="%s">%s</a>""" % (k, niceName(k))
	    rlist += "%s " % k
        doc += "\n\t<td>%s</td></tr>\n" % rlist

    # Find out about properties which have rdfs:range of t
    r = classranges.get(str(term.uri), "")
    if r:
      rlist = ''
      for k in r:
        if (spec_url in k):
            k = """<a href="#term_%s">%s</a>""" % (k.replace(spec_url, ""), niceName(k))
        else:
            k = """<a href="%s">%s</a>""" % (k, niceName(k))
        rlist += "%s " % k
      doc += "<tr><th>in-range-of:</th><td>"+rlist+"</td></tr>"
    
    # Find out about properties which have rdfs:domain of t
    d = classdomains.get(str(term.uri), "")
    if d:
      dlist = ''
      for k in d:
        if (spec_url in k):
            k = """<a href="#term_%s">%s</a>""" % (k.replace(spec_url, ""), niceName(k))
        else:
            k = """<a href="%s">%s</a>""" % (k, niceName(k))
        dlist += "%s " % k
      doc += "<tr><th>in-domain-of:</th><td>"+dlist+"</td></tr>"

    return doc

def owlInfo(term,m):
    """Returns an extra information that is defined about a term (an RDF.Node()) using OWL."""
    res = ''
    
    # Inverse properties ( owl:inverseOf )
    o = m.find_statements( RDF.Statement(term, owl.inverseOf, None) )
    if o.current():
        res += "\t<tr><th>Inverse:</th>"
	rlist = ''
	
        for st in o:
	    k = str( st.object.uri )
            if (spec_url in k):
                k = """<a href="#term_%s">%s</a>""" % (k.replace(spec_url, ""), niceName(k))
            else:
                k = """<a href="%s">%s</a>""" % (k, niceName(k))
	    rlist += "%s " % k
        res += "\n\t<td>%s</td></tr>\n" % rlist
    
    # Datatype Property ( owl.DatatypeProperty )
    o = m.find_statements( RDF.Statement(term, rdf.type, owl.DatatypeProperty) )
    if o.current():
        res += "\t<tr><th>OWL Type:</th>\n\t<td>DatatypeProperty</td></tr>\n"
	
    # Object Property ( owl.ObjectProperty )
    o = m.find_statements( RDF.Statement(term, rdf.type, owl.ObjectProperty) )
    if o.current():
        res += "\t<tr><th>OWL Type:</th>\n\t<td>ObjectProperty</td></tr>\n"

    # IFPs ( owl.InverseFunctionalProperty )
    o = m.find_statements( RDF.Statement(term, rdf.type, owl.InverseFunctionalProperty) )
    if o.current():
        res += "\t<tr><th>OWL Type:</th>\n\t<td>InverseFunctionalProperty (uniquely identifying property)</td></tr>\n"

    # Symmetric Property ( owl.SymmetricProperty )
    o = m.find_statements( RDF.Statement(term, rdf.type, owl.SymmetricProperty) )
    if o.current():
        res += "\t<tr><th>OWL Type:</th>\n\t<td>SymmetricProperty</td></tr>\n"
	
    # Transitive Property ( owl.TransitiveProperty )
    o = m.find_statements( RDF.Statement(term, rdf.type, owl.TransitiveProperty) )
    if o.current():
        res += "\t<tr><th>OWL Type:</th>\n\t<td>TransitiveProperty</td></tr>\n"

    return res

def docTerms(category, list, m):
    """A wrapper class for listing all the terms in a specific class (either
    Properties, or Classes. Category is 'Property' or 'Class', list is a 
    list of term names (strings), return value is a chunk of HTML."""
    doc = ""
    nspre = spec_pre
    for t in list:
        term = spec_ns[t]
        doc += """<div class="specterm" id="term_%s">\n<h3>%s: %s:%s</h3>\n""" % (t, category, nspre, t)
        label, comment = get_rdfs(m, term)    
        status = get_status(m, term)
        doc += "<p><em>%s</em> - %s <br /></p>" % (label, comment)
#        doc += """<table style="th { float: top; }">\n\t<!--<tr><th>Status:</th>\n\t<td>%s</td></tr>-->\n""" % status
        doc += """<table style="th { float: top; }">\n"""
        doc += owlInfo(term,m)
        if category=='Property': doc += rdfsPropertyInfo(term,m)
        if category=='Class': doc += rdfsClassInfo(term,m)
        doc += "</table>\n"
        doc += htmlDocInfo(t)
        doc += "<p style=\"float: right; font-size: small;\">[<a href=\"#sec-glance\">back to top</a>]</p>\n\n"
        doc += "\n<br/>\n</div>\n\n"
    return doc

def buildazlist(classlist, proplist):
    """Builds the A-Z list of terms. Args are a list of classes (strings) and 
    a list of props (strings)"""
    azlist = """<div style="padding: 5px; border: dotted; background-color: #ddd;">"""
    azlist = """%s\n<p>Classes: |""" % azlist
    classlist.sort()
    for c in classlist:
        azlist = """%s <a href="#term_%s">%s</a> | """ % (azlist, c.replace(" ", ""), c)
    azlist = """%s\n</p>""" % azlist
    azlist = """%s\n<p>Properties: |""" % azlist
    proplist.sort()
    for p in proplist:
        azlist = """%s <a href="#term_%s">%s</a> | """ % (azlist, p.replace(" ", ""), p)
    azlist = """%s\n</p>""" % azlist
    azlist = """%s\n</div>""" % azlist
    return azlist

def build_simple_list(classlist, proplist):
    """Builds a simple <ul> A-Z list of terms. Args are a list of classes (strings) and 
    a list of props (strings)"""

    azlist = """<div style="padding: 5px; border: dotted; background-color: #ddd;">"""
    azlist = """%s\n<p>Classes:""" % azlist
    azlist += """\n<ul>"""

    classlist.sort()
    for c in classlist:
        azlist += """\n  <li><a href="#term_%s">%s</a></li>""" % (c.replace(" ", ""), c)
    azlist = """%s\n</ul></p>""" % azlist

    azlist = """%s\n<p>Properties:""" % azlist
    azlist += """\n<ul>"""
    proplist.sort()
    for p in proplist:
        azlist += """\n  <li><a href="#term_%s">%s</a></li>""" % (p.replace(" ", ""), p)
    azlist = """%s\n</ul></p>""" % azlist

    azlist = """%s\n</div>""" % azlist
    return azlist

def specInformation(m):
    """Read through the spec (provided as a Redland model) and return classlist
    and proplist. Global variables classranges and classdomains are also filled
    as appropriate."""
    global classranges
    global classdomains

    # Find the class information: Ranges, domains, and list of all names.
    classlist = []
    for classStatement in  m.find_statements(RDF.Statement(None, rdf.type, rdfs.Class)):
        if str(classStatement.subject.uri).startswith(spec_url) :
            for range in m.find_statements(RDF.Statement(None, rdfs.range, classStatement.subject)):
                if not m.contains_statement( RDF.Statement( range.subject, rdf.type, owl.DeprecatedProperty )):
                    classranges.setdefault(str(classStatement.subject.uri), []).append(str(range.subject.uri))
            for domain in m.find_statements(RDF.Statement(None, rdfs.domain, classStatement.subject)):
                if not m.contains_statement( RDF.Statement( domain.subject, rdf.type, owl.DeprecatedProperty )):
                    classdomains.setdefault(str(classStatement.subject.uri), []).append(str(domain.subject.uri))
            classlist.append(return_name(m, classStatement.subject))

    for classStatement in  m.find_statements(RDF.Statement(None, rdf.type, owl.Class)):
        if str(classStatement.subject.uri).startswith(spec_url) :
            for range in m.find_statements(RDF.Statement(None, rdfs.range, classStatement.subject)):
                if not m.contains_statement( RDF.Statement( range.subject, rdf.type, owl.DeprecatedProperty )):
                    if str(range.subject.uri) not in classranges.get( str(classStatement.subject.uri), [] ) :
                        classranges.setdefault(str(classStatement.subject.uri), []).append(str(range.subject.uri))
            for domain in m.find_statements(RDF.Statement(None, rdfs.domain, classStatement.subject)):
                if not m.contains_statement( RDF.Statement( domain.subject, rdf.type, owl.DeprecatedProperty )):
                    if str(domain.subject.uri) not in classdomains.get( str(classStatement.subject.uri), [] ) :
                        classdomains.setdefault(str(classStatement.subject.uri), []).append(str(domain.subject.uri))
            if return_name(m, classStatement.subject) not in classlist:
                classlist.append(return_name(m, classStatement.subject))

    # Create a list of properties in the schema.
    proplist = []
    for propertyStatement in  m.find_statements(RDF.Statement(None, rdf.type, rdf.Property)):
        if not m.contains_statement( RDF.Statement( propertyStatement.subject, rdf.type, owl.DeprecatedProperty )):
            if str(propertyStatement.subject.uri).startswith(spec_url) :
                proplist.append(return_name(m, propertyStatement.subject))
    for propertyStatement in  m.find_statements(RDF.Statement(None, rdf.type, owl.DatatypeProperty)):
        if not m.contains_statement( RDF.Statement( propertyStatement.subject, rdf.type, owl.DeprecatedProperty )):
            if str(propertyStatement.subject.uri).startswith(spec_url) :
                if return_name(m, propertyStatement.subject) not in proplist:
                    proplist.append(return_name(m, propertyStatement.subject))
    for propertyStatement in  m.find_statements(RDF.Statement(None, rdf.type, owl.ObjectProperty)):
        if not m.contains_statement( RDF.Statement( propertyStatement.subject, rdf.type, owl.DeprecatedProperty )):
            if str(propertyStatement.subject.uri).startswith(spec_url) :
                if return_name(m, propertyStatement.subject) not in proplist:
                    proplist.append(return_name(m, propertyStatement.subject))
    for propertyStatement in  m.find_statements(RDF.Statement(None, rdf.type, owl.SymmetricProperty)):
        if not m.contains_statement( RDF.Statement( propertyStatement.subject, rdf.type, owl.DeprecatedProperty )):
            if str(propertyStatement.subject.uri).startswith(spec_url) :
                if return_name(m, propertyStatement.subject) not in proplist:
                    proplist.append(return_name(m, propertyStatement.subject))
    for propertyStatement in  m.find_statements(RDF.Statement(None, rdf.type, owl.TransitiveProperty)):
        if not m.contains_statement( RDF.Statement( propertyStatement.subject, rdf.type, owl.DeprecatedProperty )):
            if str(propertyStatement.subject.uri).startswith(spec_url) :
                if return_name(m, propertyStatement.subject) not in proplist:
                    proplist.append(return_name(m, propertyStatement.subject))

    return classlist, proplist
    
def main(specloc, template, mode="spec"):
    """The meat and potatoes: Everything starts here."""
    m = RDF.Model()
    p = RDF.Parser()
    p.parse_into_model(m, specloc)
    
    classlist, proplist = specInformation(m)
    
    if mode == "spec":
        # Build HTML list of terms.
        azlist = buildazlist(classlist, proplist)
    elif mode == "list":
        # Build simple <ul> list of terms.
        azlist = build_simple_list(classlist, proplist)

    # Generate Term HTML
#    termlist = "<h3>Classes and Properties (full detail)</h3>"
    termlist = docTerms('Class',classlist,m)
    termlist += docTerms('Property',proplist,m)
    
    # Generate RDF from original namespace.
    u = urllib.urlopen(specloc)
    rdfdata = u.read()
    rdfdata = re.sub(r"(<\?xml version.*\?>)", "", rdfdata)
    rdfdata = re.sub(r"(<!DOCTYPE[^]]*]>)", "", rdfdata)
#    rdfdata.replace("""<?xml version="1.0"?>""", "")
    
    # print template % (azlist.encode("utf-8"), termlist.encode("utf-8"), rdfdata.encode("ISO-8859-1"))
    template = re.sub(r"^#format \w*\n", "", template)
    template = re.sub(r"\$VersionInfo\$", owlVersionInfo(m).encode("utf-8"), template) 
    
    # NOTE: This works with the assumtpion that all "%" in the template are escaped to "%%" and it
    #       contains the same number of "%s" as the number of parameters in % ( ...parameters here... )
    template = template % (azlist.encode("utf-8"), termlist.encode("utf-8"));    
    template += "<!-- specification regenerated at " + time.strftime('%X %x %Z') + " -->"
    
    return template

def usage():
    print "Usage: "
    print "  No information yet !!!"

if __name__ == "__main__":
    """Specification generator tool, used for SIOC ontology maintenance."""
    
    specloc = "file:index.rdf"
    temploc = "template.html"
    mode = "spec"

    try:
        optlist, args = getopt.getopt( sys.argv[1:], "l" )
    except getopt.GetoptError:
        usage()
        sys.exit()
    
    if (len(args) >= 2):
        temploc = args[1]
    if (len(args) >= 1):
        specloc = args[0]

    for o,v in optlist:
        if o == "-l":
            mode = "list"

    # template is a template file for the spec, python-style % escapes
    # for replaced sections.
    f = open(temploc, "r")
    template = f.read()

    print main(specloc, template, mode)

