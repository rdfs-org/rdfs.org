# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - SiocAction - generating SIOC specification

    @copyright: 2006 - Uldis Bojars (captsolo@gmail.com)
    @license: GNU GPL, see COPYING for details.
"""

def execute(pagename, request):
    from MoinMoin import wikiutil
    from MoinMoin.Page import Page

    _ = request.getText
    thispage = Page(request, pagename)
   
    siocPage = "SiocSpecTemplate"
    specPath = "/var/www/html/spec/"
    specURL  = "http://sparql.captsolo.net/spec/"

    if pagename != siocPage:
        return thispage.send_page(request,
            msg = _('This action only works for SIOC template.'))

    # 1) get template (HTML) 
    #    = page contents

    template = thispage.get_raw_body()
    myMsg = '<p><b>Regenerated SIOC specification the template.</b></p>'

    # 2) run SpecGen code
    
    import sys
    sys.path.insert(0, specPath)
    import specgen4

    specgen4.setTermDir( specPath+'doc' )
    spec = specgen4.main( 'http://sw.deri.org/svn/sw/2005/08/sioc/ns/sioc', template )

    # 3) save file
    #

    file = open( specPath+'sioc.html', 'wt' )
    file.write(spec.encode('utf-8'))
    file.close()

    # 5) display message - OK

    myMsg += '<p>Check it out: <b><a href="' + specURL + '">SIOC specification</a></b> [draft]</p><p>&nbsp;</p>'

    return thispage.send_page(request,
        msg = _(myMsg))

