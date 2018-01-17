# Test script for a single page
from lxml import etree
import io
import re
import requests

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


def callDatamuse(word):
    """Uses the datamuse API to find (scores for) words"""
    base_url = "https://api.datamuse.com/words?sp="
    output = requests.get(base_url + word)
    output_list = output.json()
    if len(output_list) != 0:
        matched_words = [i["word"] for i in output_list]
        if word.lower() not in matched_words:  # takes into account when datamuse returns a number of words or a different 'related' word
            score = 0
        else:
            score = output_list[matched_words.index(word.lower())]["score"]
    else:
        score = 0
    return score


def processText(raw_text, no_of_calls, mod_status):
    """Cleans up text."""
    global print_text
    global dict_call_counter
    if mod_status:  # complex modifications and simple deletions need no extra spaces
        new_text = re.sub(r"\n *", "", raw_text)  # deals with newlines and spaces of xml structure
    else:  # simple adds need an extra space for reading text
        new_text = re.sub(r"\n *", " ", raw_text)
    # Next up: add spaces between lines, hyphens indicate a split up word, but some split up words are not marked by hyphens --> use dictionary (api) to determine whether two parts are words
    if no_of_calls == 1 and len(print_text) != 0 and new_text not in ["", " "]:
        if print_text[-1] == "-":
            print_text = print_text[:-1] + new_text
            print("#" + new_text + "# - A")
        elif print_text[-1] == " ":
            print_text += new_text
            print("#" + new_text + "# - B")
        elif print_text[-1] in [".", ",", "!", "?", ":", ";", '"']:
            if new_text[0] == " ":
                print_text += new_text
                print("#" + new_text + "# - C")
            else:
                print_text += " " + new_text
                print("#" + new_text + "# - D")
        else:
            if new_text[0] == " ":
                print_text += new_text
                print("#" + new_text + "# - E")
            else:  # determine whether two parts are words
                prevline_part = re.search(r"[^ ]+$", print_text).group()  # finds consecutive line-final non-space characters
                prevline_part_score = callDatamuse(prevline_part)
                curline_part = re.match(r"[^ ]+", new_text).group()  # finds consecutive line-initial non-space characters
                curline_part_score = callDatamuse(curline_part)
                combined_word = prevline_part + curline_part
                combined_score = callDatamuse(combined_word)
                if (prevline_part_score + curline_part_score) / 2 > combined_score:
                    print_text += " " + new_text
                    print("prev: " + prevline_part + " cur: " + curline_part, "SEPARATED")  # Debug output
                    print("#" + new_text + "# - F")
                else:
                    print_text += new_text
                    print("prev: " + prevline_part + " cur: " + curline_part, "JOINED")  # Debug output
                    print("#" + new_text + "# - G")
                dict_call_counter += 3
    else:
        if print_text != "" and new_text != "":
            if print_text[-1] == " " and new_text[0] == " ":
                print_text += new_text[1:]
                print("#" + new_text + "# - H")
            else:
                print_text += new_text
                print("#" + new_text + "# - I")
        else:
            print_text += new_text
            print("#" + new_text + "# - J")
    if new_text in ["", " "]:
        no_of_calls -= 1
    return no_of_calls


def processLine(zone_type, anchor_id, line_element, from_index, page_root, page_tree, displ_ids, displ_end_id):
    global delspan
    global delspan_id
    global hand
    global handspan_id
    process_text_calls = 0
    if line_element.text not in [None, "", "\n"] and from_index == 0:
        process_text_calls += 1
        process_text_calls = processText(line_element.text, process_text_calls, False)               # Prints text at the start of a line
    counter = 0
    for i in line_element.iter():
        if counter >= from_index:
            allowed_tags = ["add", "hi"]
            if i.tag in allowed_tags:
                if "del" not in page_tree.getelementpath(i) and "metamark" not in page_tree.getelementpath(i):  # Prints text in additions (additions within deletions are ignored)
                    if i.text not in [None, "", "\n"]:
                        process_text_calls += 1
                        mod = True if "mod" in page_tree.getelementpath(i) else False
                        process_text_calls = processText(i.text, process_text_calls, mod)
                    i_parent = i.getparent()
                    if i_parent.tag == "mod" and i_parent.index(i) == max(loc for loc, val in enumerate(i_parent.getchildren()) if val.tag in allowed_tags):
                        if i_parent.tail not in [None, "", "\n"]:
                            process_text_calls += 1
                            process_text_calls = processText(i_parent.tail, process_text_calls, True)      # Prints text that follows a <mod> after text of additions within <mod> have been printed
            elif i.tag == "delSpan":  # Breaks out of the line if a deletion spans multiple lines
                delspan = True
                delspan_id = i.get("spanTo")[1:]                                # Captures the ID of the anchor that marks the end of the deletion
                return False
            elif i.tag == "addSpan" and i.get("corresp"):
                if i.get("corresp")[1:] in displ_ids:
                    delspan = True
                    delspan_id = i.get("spanTo")[1:]
                    return False
            elif i.tag == "metamark" and (i.get("id") in displ_ids):
                process_text_calls = 0
                processZone(zone_type, anchor_id, page_root, page_tree, i.get("id"), displ_ids)
            elif i.tag == "anchor":                                             # Checks for anchor in a line and references a different zone
                if i.get("id") == displ_end_id:
                    return True
                anch_id = "#" + i.get("id")
                if len(page_root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:
                    process_text_calls = 0
                    processZone("", anch_id, page_root, page_tree, None, displ_ids)
                else:                                                           # Checks for referenced zone on different page
                    new_page_id = "ox-ms_abinger_" + anch_id[1:].split(".")[0]
                    if new_page_id != page_id:
                        new_root, new_tree = getPageRoot(new_page_id)
                        if len(new_root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:
                            process_text_calls = 0
                            processZone("", anch_id, new_root, new_tree, None, displ_ids)
            if i.tail not in [None, "", "\n"] and i.tag not in ["mod", "line"]:          # Prints text after/between additions that aren't contained within a <mod>
                process_text_calls += 1
                mod = True if "mod" in page_tree.getelementpath(i) else False
                process_text_calls = processText(i.tail, process_text_calls, mod)
        counter += 1
    return False


def processZone(zone_type, anchor_id, page_root, page_tree, displacement_id, displ_ids):
    global delspan
    global delspan_id
    global hand
    global handspan_id
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
        if zone.index(elem) >= from_element:  # also add to_element for volume files
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
                if elem.tag == "delSpan":  # marks delSpan that is initiated outside of a line
                    delspan = True
                    delspan_id = elem.get("spanTo")[1:]                             # Captures the ID of the anchor that marks the end of the deletion
                elif elem.tag == "addSpan" and elem.get("corresp"):  # marks displacement addSpan that is initiated outside of a line
                    if elem.get("corresp")[1:] in displ_ids and elem.get("corresp")[1:] != displacement_id:
                        delspan = True
                        delspan_id = elem.get("spanTo")[1:]
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
        else:  # even though these elements are not part of reading text we still want to check them for hand changes
            if elem.tag == "handShift":
                pass
            if len(elem.findall(".//handShift")) != 0:
                pass
            if elem.tag == "addSpan" and elem.get("hand"):
                pass
            if len(elem.findall(".//addSpan")) != 0 and elem.findall(".//addSpan")[0].get("hand"):
                pass
            if elem.tag == "anchor" and elem.get("id") == handspan_id:
                pass
            if len(elem.findall(".//anchor")) != 0 and elem.findall(".//anchor")[0].get("id") == handspan_id:
                pass


root, tree = getPageRoot(page_id)

delspan = False
delspan_id = ""
print_text = ""
hand = "mws"
handspan_id = ""
dict_call_counter = 0
processZone("main", "", root, tree, None, [])
print(print_text)
print(dict_call_counter)
