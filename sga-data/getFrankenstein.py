# Test script for a single page
from lxml import etree
import io

page_id = "ox-ms_abinger_c56-0028"


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


def getPageRoot(page_name):
    subfolder = "-".join(page_name.split("-")[:-1])
    file_path = "./{}/{}.xml".format(subfolder, page_name)
    page = etree.parse(file_path)
    page = removeNamespaces(page)
    rt = page.getroot()
    tr = rt.getroottree()
    return rt, tr


def processLine(line_element, from_index, page_root, page_tree):
    if line_element.text not in [None, "", "\n"] and from_index == 0:
        print(line_element.text)                                                # Prints text at the start of a line
    counter = 0
    for i in line_element.iter():
        if counter >= from_index:
            if i.tag in ["add", "hi"] and "del" not in page_tree.getelementpath(i):  # Prints text in additions (additions within deletions are ignored)
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
                if len(page_root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:
                    processZone("", anch_id, page_root, page_tree)
                else:                                                           # Checks for referenced zone on different page
                    new_page_id = "ox-ms_abinger_" + anch_id[1:].split(".")[0]
                    if new_page_id != page_id:
                        new_root, new_tree = getPageRoot(new_page_id)
                        if len(new_root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:
                            processZone("", anch_id, new_root, new_tree)
            if i.tail not in [None, "", "\n"] and i.tag != "mod":               # Prints text after/between additions that aren't contained within a <mod>
                print(i.tail)
        counter += 1


def processZone(zone_type, anchor_id, page_root, page_tree):
    global delspan
    zone_att = "type" if zone_type == "main" else "corresp"
    att_value = "main" if zone_att == "type" else anchor_id
    for elem in page_root.xpath("//zone[@{}='{}']".format(zone_att, att_value))[0].iter():
        if delspan:
            if len(elem.findall(".//anchor[@id='{}']".format(delspan_id))) != 0:
                del_anchor = elem.findall(".//anchor[@id='{}']".format(delspan_id))[0]
                delspan = False
                if elem.tag == "line":
                    anchor_iter_index = [i for i in elem.iter()].index(del_anchor)
                    processLine(elem, anchor_iter_index, page_root, page_tree)
        else:
            if elem.tag == "line":
                processLine(elem, 0, page_root, page_tree)
            if elem.tag == "anchor" and "line" not in page_tree.getelementpath(elem):       # Checks for anchor that is not in a line and references a different zone
                anchr_id = "#" + elem.get("id")
                if len(page_root.xpath("//zone[@corresp='{}']".format(anchr_id))) != 0:
                    processZone("", anchr_id, page_root, page_tree)
                else:                                                           # Checks for referenced zone on different page
                    new_page_id = "ox-ms_abinger_" + anchr_id[1:].split(".")[0]
                    if new_page_id != page_id:
                        new_root, new_tree = getPageRoot(new_page_id)
                        if len(new_root.xpath("//zone[@corresp='{}']".format(anchr_id))) != 0:
                            processZone("", anchr_id, new_root, new_tree)


root, tree = getPageRoot(page_id)

delspan = False
delspan_id = ""

processZone("main", "", root, tree)

# next steps:
#   - add text from <unclear> tags
#   - implement hand attribution
#       - <add place="superlinear" hand="#pbs">power</add>
#       - <handShift new="#pbs"/>
#       - <addSpan hand="#pbs" spanTo="#c56-0026.05"/>
#       - output:
#           - list that consists of consecutive fragments with the same hand
#           - list with same amount of elements and hand labels that correspond to fragments
#           - .json format
#   - Implement limitations in volume files:
#       - finish adding fromLine and toLine attributes in volume files
#       - line counter for use with fromLine and toLine attributes
#       - if (line < fromLine or line > toLine) then ignore-line = True
#       - else ignore-line = False
