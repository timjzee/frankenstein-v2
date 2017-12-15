# Test script for a single page
from lxml import etree
import io

file_path = "./ox-ms_abinger_c56/ox-ms_abinger_c56-0026.xml"


def removeNamespaces(xml_file):
    """XSL script taken from http://wiki.tei-c.org/index.php/Remove-Namespaces.xsl"""
    xslt = b'''
    <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="no"/>

    <xsl:template match="/|comment()|processing-instruction()">
        <xsl:copy>
          <xsl:apply-templates/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="*">
        <xsl:element name="{local-name()}">
          <xsl:apply-templates select="@*|node()"/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="@*">
        <xsl:attribute name="{local-name()}">
          <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>
    </xsl:stylesheet>'''
    xslt_doc = etree.parse(io.BytesIO(xslt))
    transform = etree.XSLT(xslt_doc)
    new_file = transform(xml_file)
    return new_file


def processLine(line_element, from_index):
    if line_element.text not in [None, "", "\n"] and from_index == 0:
        print(line_element.text)                                                # Prints text at the start of a line
    counter = 0
    for i in line_element.iter():
        if counter >= from_index:
            if i.tag in ["add", "hi"]:                                          # Prints text in additions (deletions are ignored)
                if i.text not in [None, "", "\n"]:
                    print(i.text)
                i_parent = i.getparent()
                if i_parent.tag == "mod" and len(i_parent.getchildren()) == (i_parent.index(i) + 1):
                    if i_parent.tail not in [None, "", "\n"]:
                        print(i_parent.tail)                                    # Prints text that follows a <mod> after text of additions within <mod> have been printed
            elif i.tag == "delSpan":                                            # Breaks out of the line if a deletion spans multiple lines
                global delspan
                delspan = True
                global delspan_id
                delspan_id = i.get("spanTo")[1:]                                # Captures the ID of the anchor that marks the end of the deletion
                break
            elif i.tag == "anchor":                                             # Checks for anchor in a line and references a different zone
                anch_id = "#" + i.get("id")
                if len(root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:
                    processZone("", anch_id)
            if i.tail not in [None, "", "\n"] and i.tag != "mod":               # Prints text after/between additions that aren't contained within a <mod>
                print(i.tail)
        counter += 1


def processZone(zone_type, anchor_id):
    global delspan
    zone_att = "type" if zone_type == "main" else "corresp"
    att_value = "main" if zone_att == "type" else anchor_id
    for elem in root.xpath("//zone[@{}='{}']".format(zone_att, att_value))[0].iter():
        if delspan:
            if len(elem.findall(".//anchor[@id='{}']".format(delspan_id))) != 0:
                del_anchor = elem.findall(".//anchor[@id='{}']".format(delspan_id))[0]
                delspan = False
                if elem.tag == "line":
                    anchor_iter_index = [i for i in elem.iter()].index(del_anchor)
                    processLine(elem, anchor_iter_index)
        else:
            if elem.tag == "line":
                processLine(elem, 0)
            elif elem.tag == "anchor":                                          # Checks for anchor that is not in a line and references a different zone
                anchr_id = "#" + elem.get("id")
                if len(root.xpath("//zone[@corresp='{}']".format(anchr_id))) != 0:
                    processZone("", anchr_id)


page = etree.parse(file_path)
page = removeNamespaces(page)
root = page.getroot()
delspan = False
delspan_id = ""

processZone("main", "")

# next steps:
#   - implement check in processLine() and processZone() for anchor that references a different zone on a different page
#   - implement hand attribution
