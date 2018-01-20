from lxml import etree
import io
import re
import requests
import sys


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


def getPageRoot(page_name, file_type):
    if file_type == "page":
        subfolder = "-".join(page_name.split("-")[:-1])
        file_path = "./{}/{}.xml".format(subfolder, page_name)
    else:
        file_path = "./{}.xml".format(page_name)
    page = etree.parse(file_path)
    page = removeNamespaces(page)
    rt = page.getroot()
    tr = rt.getroottree()
    return rt, tr


def callDatamuse(word):
    """Uses the datamuse API to find (scores for) words"""
    global dict_call_counter
    dict_call_counter += 1
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


def testWords(processed_text):
    global print_text
    global print_text_list
    global hand_list
    prevline_part = re.search(r"[^ ]+$", print_text).group()  # finds consecutive line-final non-space characters
    curline_part = re.match(r"[^ ]+", processed_text).group()  # finds consecutive line-initial non-space characters
    if len(prevline_part) == 1:
        if re.fullmatch(r"[Ia&0-9]", prevline_part):    # if prevline_part in ["I", "a", "&"]:
            if hand == hand_list[-1]:
                print_text_list[-1] += " " + processed_text
            else:
                print_text_list.append(" " + processed_text)
                hand_list.append(hand)
            print_text += " " + processed_text
            print("prev: " + prevline_part + " cur: " + curline_part, "SEPARATED")  # Debug output
            print("#" + processed_text + "# - F")
        else:
            if hand == hand_list[-1]:
                print_text_list[-1] += processed_text
            else:
                print_text_list.append(processed_text)
                hand_list.append(hand)
            print_text += processed_text
            print("prev: " + prevline_part + " cur: " + curline_part, "JOINED")  # Debug output
            print("#" + processed_text + "# - G")
    elif curline_part in ["I", "&"]:
        if hand == hand_list[-1]:
            print_text_list[-1] += " " + processed_text
        else:
            print_text_list.append(" " + processed_text)
            hand_list.append(hand)
        print_text += " " + processed_text
        print("prev: " + prevline_part + " cur: " + curline_part, "SEPARATED")  # Debug output
        print("#" + processed_text + "# - H")
    elif re.fullmatch(r"[qwrtpsdfghjklzxcvbnm]+", prevline_part):  # i.e. if prevline_part consists entirely of consonants it can't be complete yet
        if hand == hand_list[-1]:
            print_text_list[-1] += processed_text
        else:
            print_text_list.append(processed_text)
            hand_list.append(hand)
        print_text += processed_text
        print("prev: " + prevline_part + " cur: " + curline_part, "JOINED")  # Debug output
        print("#" + processed_text + "# - I")
    elif len(curline_part) == len(processed_text) == len(previous_addition) == 1 and previous_addition not in [" ", "&", ".", ";", ".", "I"]:  # if the added text and the previously added text both consist of a single letter it is likely to be part of a within-word alteration
        if hand == hand_list[-1]:
            print_text_list[-1] += processed_text
        else:
            print_text_list.append(processed_text)
            hand_list.append(hand)
        print_text += processed_text
        print("prev: " + prevline_part + " cur: " + curline_part, "JOINED")  # Debug output
        print("#" + processed_text + "# - I2")
    else:
        prevline_part_score = callDatamuse(prevline_part)
        if len(curline_part) == 1:
            curline_part_score = 0
        else:
            curline_part_score = callDatamuse(curline_part)
        combined_word = prevline_part + curline_part
        combined_score = callDatamuse(combined_word)
        if (prevline_part_score + curline_part_score) / 2 > combined_score:
            if hand == hand_list[-1]:
                print_text_list[-1] += " " + processed_text
            else:
                print_text_list.append(" " + processed_text)
                hand_list.append(hand)
            print_text += " " + processed_text
            print("prev: " + prevline_part + " cur: " + curline_part, "SEPARATED")  # Debug output
            print("#" + processed_text + "# - J")
        else:
            if hand == hand_list[-1]:
                print_text_list[-1] += processed_text
            else:
                print_text_list.append(processed_text)
                hand_list.append(hand)
            print_text += processed_text
            print("prev: " + prevline_part + " cur: " + curline_part, "JOINED")  # Debug output
            print("#" + processed_text + "# - K")


def processText(raw_text, no_of_calls, mod_status):
    """Cleans up text."""
    global print_text
    global print_text_list
    global hand_list
    global previous_addition
    if mod_status:  # complex modifications and simple deletions need no extra spaces
        new_text = re.sub(r"[\n\t] *", "", raw_text)  # deals with newlines and spaces of xml structure
    else:  # simple adds need an extra space for reading text
        new_text = re.sub(r"[\n\t] *", " ", raw_text)
    # Next up: add spaces between lines, hyphens indicate a split up word, but some split up words are not marked by hyphens --> use dictionary (api) to determine whether two parts are words
    if no_of_calls == 1 and len(print_text) != 0 and new_text not in ["", " "]:
        if print_text[-1] == "-":
            if hand == hand_list[-1]:
                print_text_list[-1] = print_text_list[-1][:-1] + new_text
            else:
                print_text_list[-1] = print_text_list[-1][:-1]
                print_text_list.append(new_text)
                hand_list.append(hand)
            print_text = print_text[:-1] + new_text
            print("#" + new_text + "# - A")
        elif print_text[-1] == " ":
            if hand == hand_list[-1]:
                print_text_list[-1] += new_text
            else:
                print_text_list.append(new_text)
                hand_list.append(hand)
            print_text += new_text
            print("#" + new_text + "# - B")
        elif print_text[-1] in [".", ",", "!", "?", ":", ";", '"']:
            if new_text[0] == " ":
                if hand == hand_list[-1]:
                    print_text_list[-1] += new_text
                else:
                    print_text_list.append(new_text)
                    hand_list.append(hand)
                print_text += new_text
                print("#" + new_text + "# - C")
            else:
                if hand == hand_list[-1]:
                    print_text_list[-1] += " " + new_text
                else:
                    print_text_list.append(" " + new_text)
                    hand_list.append(hand)
                print_text += " " + new_text
                print("#" + new_text + "# - D")
        else:
            if new_text[0] == " ":
                if hand == hand_list[-1]:
                    print_text_list[-1] += new_text
                else:
                    print_text_list.append(new_text)
                    hand_list.append(hand)
                print_text += new_text
                print("#" + new_text + "# - E")
            else:  # determine whether two parts are words
                testWords(new_text)
    else:
        if print_text != "" and new_text != "":
            if print_text[-1] == " " and new_text[0] == " ":
                if new_text[1:] != "":
                    if hand == hand_list[-1]:
                        print_text_list[-1] += new_text[1:]
                    else:
                        print_text_list.append(new_text[1:])
                        hand_list.append(hand)
                    print_text += new_text[1:]
                    print("#" + new_text + "# - L")
            else:
                if print_text[-1] != " " and new_text[0] != " ":
                    testWords(new_text)
                else:
                    if hand == hand_list[-1]:
                        print_text_list[-1] += new_text
                    else:
                        print_text_list.append(new_text)
                        hand_list.append(hand)
                    print_text += new_text
                    print("#" + new_text + "# - M")
        else:
            if print_text == "":  # i.e. if it is the first text to be added
                print_text_list.append(new_text)
                hand_list.append(hand)
                print_text += new_text
                print("#" + new_text + "# - N")
    if new_text in ["", " "]:
        no_of_calls -= 1
    previous_addition = new_text[:]
    return no_of_calls


def processLine(zone_type, anchor_id, line_element, from_index, page_root, page_tree, displ_ids, displ_end_id):
    global delspan
    global delspan_id
    global hand
    global prev_hand
    global handspan_id
    process_text_calls = 0
    if line_element.text not in [None, "", "\n"] and from_index == 0:
        process_text_calls += 1
        process_text_calls = processText(line_element.text, process_text_calls, False)               # Prints text at the start of a line
    counter = 0
    for i in line_element.iter():
        if counter >= from_index:
            allowed_tags = ["add", "hi", "retrace"]
            if i.tag in allowed_tags:
                if "del" not in page_tree.getelementpath(i) and "metamark" not in page_tree.getelementpath(i):  # Prints text in additions (additions within deletions are ignored)
                    if i.text not in [None, "", "\n"]:
                        if i.tag == "add" and i.get("hand"):
                            prev_hand = hand[:]
                            hand = i.get("hand")[1:]
                        process_text_calls += 1
#                        mod = True if "mod" in page_tree.getelementpath(i) else False
                        mod = False
                        process_text_calls = processText(i.text, process_text_calls, mod)
                        if i.tag == "add" and i.get("hand"):
                            hand = prev_hand[:]
#                    if len(i.findall(".//metamark[@function='displacement']")) != 0:  # if there's a displacement metamark in an add tag
#                        j = i.findall(".//metamark[@function='displacement']")[0]
#                        if j.get("id") in displ_ids:
#                            process_text_calls = 0
#                            displ_id = j.get("id")
#                            if len(page_root.xpath("//addSpan[@corresp='#{}']".format(displ_id))) != 0:
#                                processZone(zone_type, anchor_id, page_root, page_tree, displ_id, displ_ids, from_element, to_element)
#                            else:  # i.e. if metamark (mistakenly?) references a different zone rather than a subzone
#                                anch_id = "#" + j.get("id")
#                                if len(page_root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:
#                                    processZone("", anch_id, page_root, page_tree, None, displ_ids, 0, 1000)
            if i.tag == "delSpan":  # Breaks out of the line if a deletion spans multiple lines
                delspan = True
                delspan_id = i.get("spanTo")[1:]                                # Captures the ID of the anchor that marks the end of the deletion
                return False
            elif i.tag == "addSpan":
                if i.get("corresp"):
                    if i.get("corresp")[1:] in displ_ids:
                        delspan = True
                        delspan_id = i.get("spanTo")[1:]
                        return False
                if i.get("hand"):
                    prev_hand = hand[:]
                    hand = i.get("hand")[1:]
                    handspan_id = i.get("spanTo")[1:]
            elif i.tag == "handShift":
                hand = i.get("new")[1:]
            elif i.tag == "metamark" and (i.get("id") in displ_ids):
                process_text_calls = 0
                displ_id = i.get("id")
                if len(page_root.xpath("//addSpan[@corresp='#{}']".format(displ_id))) != 0:
                    processZone(zone_type, anchor_id, page_root, page_tree, displ_id, displ_ids, 0, 1000)
#                else:  # i.e. if metamark (mistakenly?) references a different zone rather than a subzone
#                    anch_id = "#" + i.get("id")
#                    if len(page_root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:
#                        processZone("", anch_id, page_root, page_tree, None, displ_ids, 0, 1000)
            elif i.tag == "anchor":
                if i.get("id") == displ_end_id:
                    return True
                anch_id = "#" + i.get("id")
                if len(page_root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:  # Checks for anchor in a line and references a different zone
                    process_text_calls = 0
                    processZone("", anch_id, page_root, page_tree, None, displ_ids, 0, 1000)
                else:
                    new_page_id = "ox-ms_abinger_" + anch_id[1:].split(".")[0]
                    if new_page_id != page_id:  # Checks for referenced zone on different page
                        new_root, new_tree = getPageRoot(new_page_id, "page")
                        if len(new_root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:
                            process_text_calls = 0
                            processZone("", anch_id, new_root, new_tree, None, displ_ids, 0, 1000)
                    else:  # i.e. if an anchor is not used for displacement purposes
                        if i.get("id") == handspan_id:
                            hand = prev_hand[:]
            if "mod" in page_tree.getelementpath(i) and i.tag != "mod":  # turn into if "mod" is somewhere upstream
                if i.tail not in [None, "", "\n"]:
                    process_text_calls += 1
                    process_text_calls = processText(i.tail, process_text_calls, True)
                mod_parent = i.getparent()
                while mod_parent.tag != "mod":
                    mod_parent = mod_parent.getparent()
                mod_children = [k for k in mod_parent.iter()]
                if mod_children.index(i) == (len(mod_children) - 1):  # if val.tag in allowed_tags): outdented so it doesn't just apply to tags which contain reading text
                    if mod_parent.tail not in [None, "", "\n"]:
                        process_text_calls += 1
                        process_text_calls = processText(mod_parent.tail, process_text_calls, True)      # Prints text that follows a <mod> after text of additions within <mod> have been printed
            if i.tail not in [None, "", "\n"] and i.tag not in ["mod", "line"] and "del" not in page_tree.getelementpath(i.getparent()) and "mod" not in page_tree.getelementpath(i):          # Prints text after/between additions that aren't contained within a <mod> # change final condition: "del" or "mod" cannot be upstream somewhere
                process_text_calls += 1
                mod = True if "mod" in page_tree.getelementpath(i) else False
                process_text_calls = processText(i.tail, process_text_calls, mod)
        counter += 1
    return False


def processZone(zone_type, anchor_id, page_root, page_tree, displacement_id, displ_ids, from_element, to_element):
    global delspan
    global delspan_id
    global hand
    global prev_hand
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
        # from_element = 0  # remove this and add from_element and to_element as parameters
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
        if zone.index(elem) >= from_element and zone.index(elem) <= to_element:  # also add to_element for volume files
            if displacement_id:
                if elem.tag == "anchor" and elem.get("id") == end_id:
                    zone_end = True
                    continue
            if delspan:
                if len(elem.findall(".//delSpan")) != 0:
                    old_delspan_anchor = zone.findall(".//anchor[@id='{}']".format(delspan_id))[0]
                    child_node1 = old_delspan_anchor
                    while child_node1 not in zone:
                        child_node1 = child_node1.getparent()
                    old_dspan_anchor_index = zone.index(child_node1)
                    for dspan in elem.findall(".//delSpan"):
                        new_delspan_id = dspan.get("spanTo")[1:]
                        new_delspan_anchor = zone.findall(".//anchor[@id='{}']".format(new_delspan_id))[0]
                        child_node2 = new_delspan_anchor
                        while child_node2 not in zone:
                            child_node2 = child_node2.getparent()
                        new_dspan_anchor_index = zone.index(child_node2)
                        if new_dspan_anchor_index > old_dspan_anchor_index:  # if delspan that is initiated in current delspan outlasts current delspan
                            delspan_id = new_delspan_id[:]
                if len(elem.findall(".//anchor[@id='{}']".format(delspan_id))) != 0:  # only captures anchors within some other element
                    del_anchor = elem.findall(".//anchor[@id='{}']".format(delspan_id))[0]
                    delspan = False
                    anchor_iter_index = [i for i in elem.iter()].index(del_anchor)
                    if len(elem.findall(".//handShift")) != 0:  # these statements check for hand changes in delspan lines
                        hand_elem = elem.findall(".//handShift")[0]
                        hand_iter_index = [i for i in elem.iter()].index(hand_elem)
                        if hand_iter_index < anchor_iter_index:  # and whether they occur before or after the delspan is removed
                            hand = hand_elem.get("new")[1:]
                    if len(elem.findall(".//addSpan")) != 0 and elem.findall(".//addSpan")[0].get("hand"):
                        hand_elem = elem.findall(".//addSpan")[0]
                        hand_iter_index = [i for i in elem.iter()].index(hand_elem)
                        if hand_iter_index < anchor_iter_index:
                            prev_hand = hand[:]
                            hand = elem.findall(".//addSpan")[0].get("hand")[1:]
                            handspan_id = elem.findall(".//addSpan")[0].get("spanTo")[1:]
                    if len(elem.findall(".//anchor")) != 0 and elem.findall(".//anchor")[0].get("id") == handspan_id:
                        hand_anchor = elem.findall(".//anchor")[0]
                        hand_anchor_iter_index = [i for i in elem.iter()].index(hand_anchor)
                        if hand_anchor_iter_index < anchor_iter_index:
                            hand = prev_hand[:]
                    zone_end = processLine(zone_type, anchor_id, elem, anchor_iter_index, page_root, page_tree, displ_ids, end_id)
                else:
                    if elem.tag == "anchor" and elem.get("id") == delspan_id:
                        delspan = False
                    if len(elem.findall(".//handShift")) != 0:  # these statements check for hand changes in delspan lines
                        hand = elem.findall(".//handShift")[0].get("new")[1:]
                    if len(elem.findall(".//addSpan")) != 0 and elem.findall(".//addSpan")[0].get("hand"):
                        prev_hand = hand[:]
                        hand = elem.findall(".//addSpan")[0].get("hand")[1:]
                        handspan_id = elem.findall(".//addSpan")[0].get("spanTo")[1:]
                    if len(elem.findall(".//anchor")) != 0 and elem.findall(".//anchor")[0].get("id") == handspan_id:
                        hand = prev_hand[:]
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
                    if len(zone.xpath("//addSpan[@corresp='#{}']".format(elem.get("id")))) != 0:
                        processZone(zone_type, anchor_id, page_root, page_tree, elem.get("id"), displ_ids, from_element, to_element)
#                    else:
#                        anchr_id = "#" + elem.get("id")
#                        if len(page_root.xpath("//zone[@corresp='{}']".format(anchr_id))) != 0:
#                            processZone("", anchr_id, page_root, page_tree, None, displ_ids, 0, 1000)
                elif elem.tag == "anchor":       # Checks for anchor that is not in a line and references a different zone; removed following code due to iteration change:  and "line" not in page_tree.getelementpath(elem)
                    anchr_id = "#" + elem.get("id")
                    if len(page_root.xpath("//zone[@corresp='{}']".format(anchr_id))) != 0:
                        processZone("", anchr_id, page_root, page_tree, None, displ_ids, 0, 1000)
                    else:      # Checks for referenced zone on different page
                        new_page_id = "ox-ms_abinger_" + anchr_id[1:].split(".")[0]
                        if new_page_id != page_id:
                            new_root, new_tree = getPageRoot(new_page_id, "page")
                            if len(new_root.xpath("//zone[@corresp='{}']".format(anchr_id))) != 0:
                                processZone("", anchr_id, new_root, new_tree, None, displ_ids, 0, 1000)
        else:  # even though these lines are not part of reading text we still want to check them for hand changes
            if len(elem.findall(".//handShift")) != 0:
                hand = elem.findall(".//handShift")[0].get("new")[1:]
            if len(elem.findall(".//addSpan")) != 0 and elem.findall(".//addSpan")[0].get("hand"):
                prev_hand = hand[:]
                hand = elem.findall(".//addSpan")[0].get("hand")[1:]
                handspan_id = elem.findall(".//addSpan")[0].get("spanTo")[1:]
            if len(elem.findall(".//anchor")) != 0 and elem.findall(".//anchor")[0].get("id") == handspan_id:
                hand = prev_hand[:]
        if elem.tag == "handShift":  # the following hand related statements apply to all elements regardless of delSpan, from_element and to_element
            hand = elem.get("new")[1:]
        if elem.tag == "addSpan" and elem.get("hand"):
            prev_hand = hand[:]
            hand = elem.get("hand")[1:]
            handspan_id = elem.get("spanTo")[1:]
        if elem.tag == "anchor" and elem.get("id") == handspan_id:
            hand = prev_hand[:]


def processLocus(locus, match_page):
    global auto_mode
    global page_id
    raw_page_ids = locus.get("target").split(" ")
    page_ids = [i[1:] for i in raw_page_ids]
    if len(page_ids) == 1:
        from_element = 0
        to_element = 1000
        if locus.get("fromElement"):
            from_element = int(locus.get("fromElement")) - 1
        if locus.get("toElement"):
            to_element = int(locus.get("toElement")) - 1
        page_id = page_ids[0]
        root, tree = getPageRoot(page_id, "page")
        processZone("main", "", root, tree, None, [], from_element, to_element)
    else:
        for page_id in page_ids:
            if not auto_mode:
                if page_id == match_page:
                    from_element = 0
                    to_element = 1000
                    root, tree = getPageRoot(page_id, "page")
                    processZone("main", "", root, tree, None, [], from_element, to_element)
            else:
                from_element = 0
                to_element = 1000
                root, tree = getPageRoot(page_id, "page")
                processZone("main", "", root, tree, None, [], from_element, to_element)


def processChapter(chap, vol_no):
    global auto_mode
    chapter_no = chap.get("n")
    if not auto_mode:
        raw_p_ids = []
        for locus in chap.findall(".//locus"):
            raw_p_ids.extend(locus.get("target").split(" "))
        p_ids = [i[-7:] for i in raw_p_ids]
        p_id = ""
        while p_id not in p_ids:
            p_id = input("Chapter {} contains the following pages:\n{}\nWhich page? ".format(chapter_no, p_ids))
        for loc in chap.findall(".//locus"):
            if p_id in loc.get("target"):
                match_id = "ox-ms_abinger_c" + p_id
                processLocus(loc, match_id)
        print(print_text)
        print(print_text_list)
        print(hand_list)
        print("\nNumber of Datamuse API calls:", dict_call_counter)
    else:
        for loc in chap.findall(".//locus"):
            processLocus(loc, "")
        print(print_text)
        print(print_text_list)
        print(hand_list)
        continue_script = input("\nNumber of Datamuse API calls: {}\nVolume: {} Chapter: {}\nContinue? (y/n) ".format(dict_call_counter, vol_no, chapter_no))
        if continue_script not in ["y", "Y"]:
            sys.exit()


def processVolume(vol_no):
    global auto_mode
    volume_id = "ox-frankenstein-volume_" + vol_no
    vol_root, vol_tree = getPageRoot(volume_id, "volume")
    chapters = vol_root.findall(".//msItem[@class='#chapter']")
    if not auto_mode:
        allowed_chaps = [ch.get("n") for ch in chapters]
        chap_no = ""
        while chap_no not in allowed_chaps:
            chap_no = input("Volume {} contains the following chapters:\n{}\nWhich chapter? ".format(vol_no, allowed_chaps))
        chapter = chapters[allowed_chaps.index(chap_no)]
        processChapter(chapter, vol_no)
    else:
        for chapter in chapters:
            processChapter(chapter, vol_no)


dict_call_counter = 0
print_text = ""
print_text_list = []
hand_list = []
delspan = False
delspan_id = ""
prev_hand = "mws"  # only used to switch back after an addSpan or add, do not use for handlist
hand = "mws"
handspan_id = ""
previous_addition = ""

auto_mode = True if input("Auto mode? (y/n) ") in ["Y", "y"] else False
if not auto_mode:
    volume_no = ""
    while volume_no not in ["i", "ii", "iii"]:
        volume_no = input("Which volume? (i/ii/iii) ")
    processVolume(volume_no)
else:
    for volume_no in ["i", "ii", "iii"]:
        processVolume(volume_no)
