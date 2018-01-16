# Test script for a single page
from lxml import etree
import io
import re

page_id = "ox-ms_abinger_c57-0024"


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


def processText(raw_text, no_of_calls, mod_status):
    """Cleans up text."""
    global print_text
    if mod_status:  # complex modifications need no extra spaces
        new_text = re.sub(r"\n *", "", raw_text)  # deals with newlines and spaces due to xml structure
    else:  # simple adds need an extra space for reading text
        new_text = re.sub(r"\n *", " ", raw_text)
    print_text += new_text
    print("#" + new_text + "#")  # Debug output
    # Next up: add spaces between lines, hyphens indicate a split up word, but some split up words are not marked by hyphens --> use dictionary (api) to determine whether two parts are words


def processLine(zone_type, anchor_id, line_element, from_index, page_root, page_tree, displ_ids, displ_end_id):
    process_text_calls = 0
    if line_element.text not in [None, "", "\n"] and from_index == 0:
        process_text_calls += 1
        processText(line_element.text, process_text_calls, False)               # Prints text at the start of a line
    counter = 0
    for i in line_element.iter():
        if counter >= from_index:
            allowed_tags = ["add", "hi"]
            if i.tag in allowed_tags:
                if "del" not in page_tree.getelementpath(i) and "metamark" not in page_tree.getelementpath(i):  # Prints text in additions (additions within deletions are ignored)
                    if i.text not in [None, "", "\n"]:
                        process_text_calls += 1
                        mod = True if "mod" in page_tree.getelementpath(i) else False
                        processText(i.text, process_text_calls, mod)
                    i_parent = i.getparent()
                    if i_parent.tag == "mod" and i_parent.index(i) == max(loc for loc, val in enumerate(i_parent.getchildren()) if val.tag in allowed_tags):
                        if i_parent.tail not in [None, "", "\n"]:
                            process_text_calls += 1
                            processText(i_parent.tail, process_text_calls, True)      # Prints text that follows a <mod> after text of additions within <mod> have been printed
            elif i.tag == "delSpan" or (i.tag == "addSpan" and i.get("corresp")[1:] in displ_ids):  # Breaks out of the line if a deletion spans multiple lines
                global delspan
                delspan = True
                global delspan_id
                delspan_id = i.get("spanTo")[1:]                                # Captures the ID of the anchor that marks the end of the deletion
                return False
            elif i.tag == "metamark" and (i.get("id") in displ_ids):
                processZone(zone_type, anchor_id, page_root, page_tree, i.get("id"), displ_ids)
            elif i.tag == "anchor":                                             # Checks for anchor in a line and references a different zone
                if i.get("id") == displ_end_id:
                    return True
                anch_id = "#" + i.get("id")
                if len(page_root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:
                    processZone("", anch_id, page_root, page_tree, None, displ_ids)
                else:                                                           # Checks for referenced zone on different page
                    new_page_id = "ox-ms_abinger_" + anch_id[1:].split(".")[0]
                    if new_page_id != page_id:
                        new_root, new_tree = getPageRoot(new_page_id)
                        if len(new_root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:
                            processZone("", anch_id, new_root, new_tree, None, displ_ids)
            if i.tail not in [None, "", "\n"] and i.tag not in ["mod", "line"]:          # Prints text after/between additions that aren't contained within a <mod>
                process_text_calls += 1
                mod = True if "mod" in page_tree.getelementpath(i) else False
                processText(i.tail, process_text_calls, mod)
        counter += 1
    return False


def processZone(zone_type, anchor_id, page_root, page_tree, displacement_id, displ_ids):
    global delspan
    global delspan_id
    zone_att = "type" if zone_type == "main" else "corresp"
    att_value = "main" if zone_att == "type" else anchor_id
    zone = page_root.xpath("//zone[@{}='{}']".format(zone_att, att_value))[0]
    if displacement_id:  # i.e. if zone is a subzone
        subzone_start = zone.xpath("//addSpan[@corresp='#{}']".format(displacement_id))[0]
        end_id = subzone_start.get("spanTo")[1:]
        child = subzone_start
        while child not in zone:
            child = child.getparent()
        from_element = zone.index(child)
    else:
        from_element = 0
        end_id = None
        displ_ids = []
        for elem in zone:  # changed from zone.iter() to zone to make indexing easier
            if len(elem.findall(".//metamark[@function='displacement']")) != 0:
                for displ_mark in elem.findall(".//metamark[@function='displacement']"):
                    if displ_mark.get("id"):
                        displ_ids.append(displ_mark.get("id"))
            if elem.tag == "metamark" and elem.get("funtion") == "displacement" and elem.get("id"):
                displ_ids.append(elem.get("id"))
    zone_end = False
    for elem in zone:  # changed from zone.iter() to zone to make indexing easier
        if zone_end:
            break
        if zone.index(elem) >= from_element:
            if displacement_id:
                if elem.tag == "anchor" and elem.get("id") == end_id:
                    zone_end = True
                    continue
            if delspan:
                if len(elem.findall(".//anchor[@id='{}']".format(delspan_id))) != 0:  # only captures anchors within some other element
                    del_anchor = elem.findall(".//anchor[@id='{}']".format(delspan_id))[0]
                    delspan = False
                    if elem.tag == "line":
                        anchor_iter_index = [i for i in elem.iter()].index(del_anchor)
                        zone_end = processLine(zone_type, anchor_id, elem, anchor_iter_index, page_root, page_tree, displ_ids, end_id)
                if elem.tag == "anchor" and elem.get("id") == delspan_id:
                    delspan = False
            else:
                if elem.tag == "delSpan" or (elem.tag == "addSpan" and elem.get("corresp")[1:] in displ_ids and elem.get("corresp")[1:] != displacement_id):  # marks delSpan / displacement addSpan that is initiated outside of a line
                    delspan = True
                    delspan_id = elem.get("spanTo")[1:]                             # Captures the ID of the anchor that marks the end of the deletion
                elif elem.tag == "line":
                    zone_end = processLine(zone_type, anchor_id, elem, 0, page_root, page_tree, displ_ids, end_id)
                elif elem.tag == "metamark" and (elem.get("id") in displ_ids):
                    processZone(zone_type, anchor_id, page_root, page_tree, elem.get("id"), displ_ids)
                elif elem.tag == "anchor":       # Checks for anchor that is not in a line and references a different zone; removed following code due to iteration change:  and "line" not in page_tree.getelementpath(elem)
                    anchr_id = "#" + elem.get("id")
                    if len(page_root.xpath("//zone[@corresp='{}']".format(anchr_id))) != 0:
                        processZone("", anchr_id, page_root, page_tree, None, displ_ids)
                    else:                                                           # Checks for referenced zone on different page
                        new_page_id = "ox-ms_abinger_" + anchr_id[1:].split(".")[0]
                        if new_page_id != page_id:
                            new_root, new_tree = getPageRoot(new_page_id)
                            if len(new_root.xpath("//zone[@corresp='{}']".format(anchr_id))) != 0:
                                processZone("", anchr_id, new_root, new_tree, None, displ_ids)


root, tree = getPageRoot(page_id)

delspan = False
delspan_id = ""
print_text = ""
processZone("main", "", root, tree, None, [])
print(print_text)
