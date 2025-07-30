"""
report.py: HTML generator for report.
           This file is subject to the terms and conditions defined in file 'LICENCE.md', which is part of this source
           code package.
"""

__author__    = "Nuno Vicente"
__copyright__ = "Copyright 2018 OceanScan - Marine Systems & Technology, Lda."
__credits__   = "Ricardo Martins"

CSS = """
@page {
    size: A4 portrait;
    margin: 0.54cm 2cm 0.54cm 2cm;
}

body {
  font-family: Liberation Sans;
  font-size: 12px;
}

#header{
  border-spacing: 0;
  border: 0px;
  font-size: 10px;
  white-space: nowrap;
}

#header img{
  width: 200px;
}

#header td{
  border: 0px;
  border-right: 0.5px solid #2074bb;
  width: 100%;
  padding-left: 10px;
}

#header td.image{
  width: 210px;
}

hr{
  border: 0.5px solid #2074bb;
}

.section_start{
  background-color: #2074bb;
  color: #FFFFFF;
  border: 0.5px solid black;
  border-collapse: collapse;
  font-size: 14px;
}

table, tr, th, td {
  border-color: black;
  width: 100%;
  padding: 0;
  border-spacing: 0;
  border: 0.5px solid black;
  border-collapse: collapse;
  width: 100%
}

th {
  background-color: #eee;
  align: left;
  width: 150px
}

th, td {
  padding: 0.25em;
}

h1 {
    text-align: center;
}

pre {
  font-size: 10px;
  font-family: monospace;
  border: 0.5px solid black;
  padding: 10px 10px 10px 10px;
}

#footer {
  width: 100%;
  position: absolute;
  bottom: 0;
  text-align: right;
}

"""


class Document:
    def __init__(self, system, serial, logo):
        self.system = system
        self.serial = serial
        self._html = ''
        self._html = '<html>'
        self._html += '<head><title></title><style type="text/css">%s</style></head>' % CSS
        self._html += '<body>'
        self._html += '<table id="header"><tr id="header">'
        self._html += '<td class="image"><img src="file://%s"/></td>' % logo
        self._html += '<td><a href="http://www.oceanscan-mst.com/">www.oceanscan-mst.com</a>'
        self._html += '<p><p>Setup Certificate'
        self._html += '</td>'
        self._html += "</tr></table>"
        self._html += '<hr/><br/>'
        self._section = 1

    def section_start(self, title):
        self._html += '<table class="section_start">'
        self._html += '<tr><td><b>%u. %s</font></b></td></tr></table><br/>' % (self._section, title)
        self._html += '<table>'
        self._section += 1

    def section_line(self, label, text):
        self._html += '<tr><th>%s</th><td>%s</td></tr>\n' % (label, text)

    def section_end(self):
        self._html += '</table><br/>'

    def section_body(self, body):
        self._html += '<tr><td>'
        self._html += body
        self._html += '</td></tr>'

    def section_body_raw(self, body):
        self._html += '<pre>' + body + '</pre>'

    def section_footer(self):
        self._html += '<div id="footer">'
        self._html += '<hr/> OceanScan – Marine Systems & Technology Lda. All rights reserved.'
        self._html += '<br>CONFIDENTIAL INFORMATION | This document after printing is no longer controlled'
        self._html += '</div>'

    def html(self):
        return self._html + '</body></html>'
