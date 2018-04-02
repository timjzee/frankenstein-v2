from lxml import etree
import io
import re
import requests
import sys
import random
import math
import time


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


def callDatamuse(word, left_context=None):
    """Uses the datamuse API to find (scores for) words"""
    global dict_call_counter
    dict_call_counter += 1
    if not left_context:
        lc_text = ""
    else:
        lc_text = "&lc=" + re.sub(r'[-"—.–,;:!?()]', '', left_context[:])
    clean_word = re.sub(r'[-"—.–,;:!?()]', '', word)
    output = requests.get("https://api.datamuse.com/words?sp={}{}&md=f".format(clean_word, lc_text))
    output_list = output.json()
    if len(output_list) != 0:
        matched_words = [i["word"] for i in output_list]
        if clean_word.lower() not in matched_words:  # takes into account when datamuse returns a number of words or a different 'related' word
            score = 0
            freq = 0
        else:
            score = output_list[matched_words.index(clean_word.lower())]["score"]
            freq = float(output_list[matched_words.index(clean_word.lower())]["tags"][0][2:])
    else:
        score = 0
        freq = 0
    final_score = score * math.sqrt(freq)  # changed from (score + freq) / 2
    return final_score


def search1818Edition(wrd):
    search_word = re.sub(r'[-"—.–,;:!?()]', '', wrd)
    find_list = re.findall(r'[-"—.–,;:!?() ]{}[-"—.–,;:!?() ]'.format(re.escape(search_word)), edition_1818)
    return len(find_list)


def testWords(processed_text):
    global print_text
    global print_text_list
    global hand_list
    global prev_add_processed
    prevline_part = re.search(r"[^ ]+$", print_text).group()  # finds consecutive line-final non-space characters
    curline_part = re.match(r"[^ ]+", processed_text).group()  # finds consecutive line-initial non-space characters
    if prev_add_processed and (" " not in previous_addition):
        part_a = re.search(r"[^ ]+(?= *{}$)".format(re.escape(previous_addition)), print_text).group()
        score_a = callDatamuse(part_a)
        score_b = callDatamuse(previous_addition)
        score_c = callDatamuse(curline_part)
        score_ab = callDatamuse(part_a + previous_addition)
        score_bc = callDatamuse(previous_addition + curline_part)
        score_abc = callDatamuse(part_a + previous_addition + curline_part)
        combo_a_b_c = (score_a * score_b * score_c, part_a + " " + previous_addition + " " + processed_text, "a_b_c")  # score used to be average of all scores, i.e. sum of scores / number of scores
        combo_ab_c = (score_ab * score_ab * score_c, part_a + previous_addition + " " + processed_text, "ab_c")
        combo_a_bc = (score_a * score_a * score_bc, part_a + " " + previous_addition + processed_text, "a_bc")
        combo_abc = (score_abc * score_abc * score_abc, part_a + previous_addition + processed_text, "abc")
        if combo_abc[0] > 0:
            best_combo = combo_abc
            print("combo 1")
        elif re.fullmatch(r"[qwrtpsdfghjklzxcvbnm]+", part_a.lower()):  # if one or more consecutive consonants in part_a
            best_combo = max(combo_ab_c, combo_abc)
            print("combo 3")
            print("algo 1")
            if best_combo[0] == 0:  # if both scores are 0 search in 1818 edition
                print("algo 2")
                count_c = search1818Edition(curline_part) if score_c == 0 else score_c
                count_ab = search1818Edition(part_a + previous_addition) if score_ab == 0 else score_ab
                count_abc = search1818Edition(part_a + previous_addition + curline_part)
                combo_ab_c = (count_ab * count_c, part_a + previous_addition + " " + processed_text, "ab_c")
                combo_abc = (count_abc * count_abc, part_a + previous_addition + processed_text, "abc")
                best_combo = max(combo_ab_c, combo_abc)
                if best_combo[0] == 0:  # if both scores are 0 fall back on old algorithm
                    print("algo 3")
                    combo_ab_c = ((score_ab + score_c), part_a + previous_addition + " " + processed_text, "ab_c")
                    combo_abc = (score_abc, part_a + previous_addition + processed_text, "abc")
                    best_combo = max(combo_ab_c, combo_abc)
        elif re.fullmatch(r"[qwrtpsdfghjklzxcvbnm]+", previous_addition.lower()):  # if one or more consecutive consonants in part_b
            print("combo 2")
            print("algo 1")
            best_combo = max(combo_a_bc, combo_ab_c, combo_abc)
            if best_combo[0] == 0:  # if all scores are 0 search in 1818 edition
                print("algo 2")
                count_a = search1818Edition(part_a) if score_a == 0 else score_a
                count_c = search1818Edition(curline_part) if score_c == 0 else score_c
                count_ab = search1818Edition(part_a + previous_addition) if score_ab == 0 else score_ab
                count_bc = search1818Edition(previous_addition + curline_part) if score_bc == 0 else score_bc
                count_abc = search1818Edition(part_a + previous_addition + curline_part)
                combo_ab_c = (count_ab * count_c, part_a + previous_addition + " " + processed_text, "ab_c")
                combo_a_bc = (count_a * count_bc, part_a + " " + previous_addition + processed_text, "a_bc")
                combo_abc = (count_abc * count_abc, part_a + previous_addition + processed_text, "abc")
                best_combo = max(combo_a_bc, combo_ab_c, combo_abc)
                if best_combo[0] == 0:  # if all scores are 0 fall back on old algorithm
                    print("algo 3")
                    combo_ab_c = ((score_ab + score_c), part_a + previous_addition + " " + processed_text, "ab_c")
                    combo_a_bc = ((score_a + score_bc), part_a + " " + previous_addition + processed_text, "a_bc")
                    combo_abc = (score_abc, part_a + previous_addition + processed_text, "abc")
                    best_combo = max(combo_a_bc, combo_ab_c, combo_abc)
        else:
            best_combo = max(combo_a_b_c, combo_a_bc, combo_ab_c, combo_abc)
            print("combo 4")
            print("algo 1")
            if best_combo[0] == 0:  # if all scores are 0 fall back on old algorithm
                print("algo 2")
                count_a = search1818Edition(part_a) if score_a == 0 else score_a
                count_b = search1818Edition(previous_addition) if score_b == 0 else score_b
                count_c = search1818Edition(curline_part) if score_c == 0 else score_c
                count_ab = search1818Edition(part_a + previous_addition) if score_ab == 0 else score_ab
                count_bc = search1818Edition(previous_addition + curline_part) if score_bc == 0 else score_bc
                count_abc = search1818Edition(part_a + previous_addition + curline_part)
                combo_a_b_c = (count_a * count_b * count_c, part_a + " " + previous_addition + " " + processed_text, "a_b_c")
                combo_ab_c = (count_ab * count_ab * count_c, part_a + previous_addition + " " + processed_text, "ab_c")
                combo_a_bc = (count_a * count_bc * count_bc, part_a + " " + previous_addition + processed_text, "a_bc")
                combo_abc = (count_abc * count_abc, part_a + previous_addition + processed_text, "abc")
                best_combo = max(combo_a_b_c, combo_a_bc, combo_ab_c, combo_abc)
                if best_combo[0] == 0:  # if all scores are 0 fall back on old algorithm
                    print("algo 3")
                    combo_a_b_c = ((score_a + score_b + score_c), part_a + " " + previous_addition + " " + processed_text, "a_b_c")
                    combo_ab_c = ((score_ab + score_c), part_a + previous_addition + " " + processed_text, "ab_c")
                    combo_a_bc = ((score_a + score_bc), part_a + " " + previous_addition + processed_text, "a_bc")
                    combo_abc = (score_abc, part_a + previous_addition + processed_text, "abc")
                    best_combo = max(combo_a_b_c, combo_a_bc, combo_ab_c, combo_abc)
        print("#" + part_a + "#", "#" + previous_addition + "#", "#" + curline_part + "#")
        print(best_combo, "REVISION")
        match_str = re.search(r"{} *{}$".format(re.escape(part_a), re.escape(previous_addition)), print_text).group()
        print_text = re.sub(r"{}$".format(re.escape(match_str)), best_combo[1], print_text, count=1)
        if " " in match_str:
            if "a_b" in best_combo[2]:
                pass
            elif "ab" in best_combo[2]:
                print_text_list[-1] = re.sub(r" +{}$".format(re.escape(previous_addition)), previous_addition, print_text_list[-1], count=1)
        else:
            if "a_b" in best_combo[2]:
                print_text_list[-1] = re.sub(r"{}$".format(re.escape(previous_addition)), " " + previous_addition, print_text_list[-1], count=1)
            elif "ab" in best_combo[2]:
                pass
        if "b_c" in best_combo[2]:
            if hand == hand_list[-1]:
                print_text_list[-1] += " " + processed_text
            else:
                print_text_list.append(" " + processed_text)
                hand_list.append(hand)
        else:
            if hand == hand_list[-1]:
                print_text_list[-1] += processed_text
            else:
                print_text_list.append(processed_text)
                hand_list.append(hand)
    elif len(prevline_part) == 1 and re.fullmatch(r"[&0-9]", prevline_part):    # removed 'I' and 'a' from list, as this rule would separate words such as 'It'
        if hand == hand_list[-1]:
            print_text_list[-1] += " " + processed_text
        else:
            print_text_list.append(" " + processed_text)
            hand_list.append(hand)
        print_text += " " + processed_text
        print("prev: " + prevline_part + " cur: " + curline_part, "SEPARATED")  # Debug output
        print("#" + processed_text + "# - G")
    elif len(prevline_part) == 1 and re.fullmatch(r"[^Ia&0-9]", prevline_part):
        if hand == hand_list[-1]:
            print_text_list[-1] += processed_text
        else:
            print_text_list.append(processed_text)
            hand_list.append(hand)
        print_text += processed_text
        print("prev: " + prevline_part + " cur: " + curline_part, "JOINED")  # Debug output
        print("#" + processed_text + "# - H")
    elif curline_part in ["I", "&"]:
        if hand == hand_list[-1]:
            print_text_list[-1] += " " + processed_text
        else:
            print_text_list.append(" " + processed_text)
            hand_list.append(hand)
        print_text += " " + processed_text
        print("prev: " + prevline_part + " cur: " + curline_part, "SEPARATED")  # Debug output
        print("#" + processed_text + "# - I")
    elif curline_part in [".", ",", "?", ":", "!", ";"]:
        if hand == hand_list[-1]:
            print_text_list[-1] += processed_text
        else:
            print_text_list.append(processed_text)
            hand_list.append(hand)
        print_text += processed_text
        print("prev: " + prevline_part + " cur: " + curline_part, "JOINED")  # Debug output
        print("#" + processed_text + "# - J")
    elif re.fullmatch(r"[qwrtpsdfghjklzxcvbnm]+", prevline_part):  # i.e. if prevline_part consists entirely of consonants it can't be complete yet
        if hand == hand_list[-1]:
            print_text_list[-1] += processed_text
        else:
            print_text_list.append(processed_text)
            hand_list.append(hand)
        print_text += processed_text
        print("prev: " + prevline_part + " cur: " + curline_part, "JOINED")  # Debug output
        print("#" + processed_text + "# - K")
    elif len(curline_part) == len(processed_text) == len(previous_addition) == 1 and previous_addition not in [" ", "&", ".", ";", ".", "I"]:  # if the added text and the previously added text both consist of a single letter it is likely to be part of a within-word alteration
        if hand == hand_list[-1]:
            print_text_list[-1] += processed_text
        else:
            print_text_list.append(processed_text)
            hand_list.append(hand)
        print_text += processed_text
        print("prev: " + prevline_part + " cur: " + curline_part, "JOINED")  # Debug output
        print("#" + processed_text + "# - L")
    else:
        if print_text == "":
            l_context = None
        else:
            context_object = re.search(r"[^ ]+(?= *{}$)".format(re.escape(previous_addition)), print_text)
            if context_object:
                l_context = context_object.group()
            else:
                l_context = None
        prevline_part_score = callDatamuse(prevline_part, l_context)
        combined_word = prevline_part + curline_part
        if len(curline_part) == 1 and curline_part not in ["I", "a"]:
            curline_part_score = 0
            combined_score = callDatamuse(combined_word, l_context)
        else:
            if len(curline_part) > 1 and curline_part[-1] in [".", ",", ":", ";", "!", "?"]:  # if curline_part ends in a punctuation mark, ignore that mark when calling datamuse (this prevents incorrect separations)
                curline_part_score = callDatamuse(curline_part[:-1], prevline_part)
                combined_score = callDatamuse(combined_word[:-1], l_context)
            else:
                curline_part_score = callDatamuse(curline_part, prevline_part)
                combined_score = callDatamuse(combined_word, l_context)
        if (prevline_part_score * curline_part_score) > (combined_score * combined_score):  # changed algorithm from mean to product of parts
            if hand == hand_list[-1]:
                print_text_list[-1] += " " + processed_text
            else:
                print_text_list.append(" " + processed_text)
                hand_list.append(hand)
            print_text += " " + processed_text
            print("prev: " + prevline_part + " cur: " + curline_part, "SEPARATED")  # Debug output
            print("#" + processed_text + "# - M")
        elif (prevline_part_score * curline_part_score) == (combined_score * combined_score) and combined_score == 0:  # fall back on old algorithm
            if ((prevline_part_score + curline_part_score) / 2) > combined_score:  # changed algorithm from mean to product of parts
                if hand == hand_list[-1]:
                    print_text_list[-1] += " " + processed_text
                else:
                    print_text_list.append(" " + processed_text)
                    hand_list.append(hand)
                print_text += " " + processed_text
                print("prev: " + prevline_part + " cur: " + curline_part, "SEPARATED")  # Debug output
                print("#" + processed_text + "# - N")
            else:
                if hand == hand_list[-1]:
                    print_text_list[-1] += processed_text
                else:
                    print_text_list.append(processed_text)
                    hand_list.append(hand)
                print_text += processed_text
                print("prev: " + prevline_part + " cur: " + curline_part, "JOINED")  # Debug output
                print("#" + processed_text + "# - O")
        else:  # if joined score >= separated score
            if processed_text[0] == '"':
                processed_text = processed_text[1:]  # remove quotation marks that are within words due to EOL split
            if hand == hand_list[-1]:
                print_text_list[-1] += processed_text
            else:
                print_text_list.append(processed_text)
                hand_list.append(hand)
            print_text += processed_text
            print("prev: " + prevline_part + " cur: " + curline_part, "JOINED")  # Debug output
            print("#" + processed_text + "# - P")
    prev_add_processed = True
    return processed_text  # makes sure previous_addition does not contain word internal quotation marks


def processText(raw_text, mod_status):
    """Cleans up text."""
    global print_text
    global print_text_list
    global hand_list
    global previous_addition
    global prev_add_processed
    global process_text_calls
    if mod_status:  # complex modifications and simple deletions need no extra spaces
        new_text = re.sub(r"^[\n\t] *", "", raw_text)  # deals with newlines and spaces of xml structure
        new_text = re.sub(r"[\n\t] *", " ", new_text)
    else:  # simple adds need an extra space for reading text
        new_text = re.sub(r"[\n\t] *", " ", raw_text)
    # Next up: add spaces between lines, hyphens indicate a split up word, but some split up words are not marked by hyphens --> use dictionary (api) to determine whether two parts are words
    if process_text_calls == 1 and len(print_text) != 0 and new_text not in ["", " "]:
        if print_text[-1] == "-":
            prev_add_processed = False
            if new_text[0] in ["-", '"']:
                new_text = new_text[1:]
            if hand == hand_list[-1]:
                print_text_list[-1] = print_text_list[-1][:-1] + new_text
            else:
                print_text_list[-1] = print_text_list[-1][:-1]
                print_text_list.append(new_text)
                hand_list.append(hand)
            print_text = print_text[:-1] + new_text
            print("#" + new_text + "# - A")
        elif print_text[-1] == " ":
            prev_add_processed = False
            if hand == hand_list[-1]:
                print_text_list[-1] += new_text
            else:
                print_text_list.append(new_text)
                hand_list.append(hand)
            print_text += new_text
            print("#" + new_text + "# - B")
        elif print_text[-1] in [".", ",", "!", "?", ":", ";", '"']:
            prev_add_processed = False
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
                prev_add_processed = False
                if hand == hand_list[-1]:
                    print_text_list[-1] += new_text
                else:
                    print_text_list.append(new_text)
                    hand_list.append(hand)
                print_text += new_text
                print("#" + new_text + "# - E")
            elif new_text[0] == "-":
                prev_add_processed = False
                new_text = new_text[1:]
                if hand == hand_list[-1]:
                    print_text_list[-1] += new_text
                else:
                    print_text_list.append(new_text)
                    hand_list.append(hand)
                print_text += new_text
                print("#" + new_text + "# - F")
            else:  # determine whether two parts are words
                new_text = testWords(new_text)
    else:
        if print_text != "" and new_text != "":
            if print_text[-1] == " " and new_text[0] == " ":
                if new_text[1:] != "":
                    prev_add_processed = False
                    if hand == hand_list[-1]:
                        print_text_list[-1] += new_text[1:]
                    else:
                        print_text_list.append(new_text[1:])
                        hand_list.append(hand)
                    print_text += new_text[1:]
                    print("#" + new_text + "# - Q")
            else:
                if print_text[-1] != " " and new_text[0] != " ":
                    new_text = testWords(new_text)
                else:
                    if new_text != " ":
                        prev_add_processed = False
                        if hand == hand_list[-1]:
                            print_text_list[-1] += new_text
                        else:
                            print_text_list.append(new_text)
                            hand_list.append(hand)
                        print_text += new_text
                        print("#" + new_text + "# - R")
        else:
            if print_text == "":  # i.e. if it is the first text to be added
                prev_add_processed = False
                print_text_list.append(new_text)
                hand_list.append(hand)
                print_text += new_text
                print("#" + new_text + "# - S")
    if new_text in ["", " "]:
        process_text_calls -= 1
    if new_text != "":
        previous_addition = new_text[:]


def getOtherShelley(shelley):
    if shelley == "mws":
        return "pbs"
    else:
        return "mws"


def processElement(zone_type, anchor_id, element, from_anchor, page_root, page_tree, displ_end_id, cross_lin=False):
    global delspan
    global delspan_id
    global hand
    global prev_hand
    global handspan_id
    global ignore_adds
    global process_text_calls
    global zone_end
    global displ_ids
    if (("del" not in page_tree.getelementpath(element)) or re.search(r'restore.*del', page_tree.getelementpath(element))) and ((element.get("id") not in ignore_adds) or (cross_lin is True)) and "metamark" not in page_tree.getelementpath(element) and ("unclear" not in page_tree.getelementpath(element) or len(element.text) == 1):
        # print text
        if element.tag == "add" and element.get("hand"):
            prev_hand = hand[:]
            hand = element.get("hand")[1:]
        if element.text not in [None, "", "\n"] and not from_anchor:
            process_text_calls += 1
            processText(element.text, False)
        # process children
        element_children = element.getchildren()
        if (from_anchor is not None) and from_anchor in element_children:
            element_children = element_children[element_children.index(from_anchor):]
            from_anchor = None
        for element_child in element_children:
            if type(element_child) == etree._Element:
                from_anchor = processElement(zone_type, anchor_id, element_child, from_anchor, page_root, page_tree, displ_end_id)
                if zone_end or delspan:  # step out of recursion if zone_end is encountered
                    return from_anchor
        if element.tag == "add" and element.get("hand"):
            hand = prev_hand[:]
    # tag-specific processing
    if element.tag == "add" and element.get("next"):  # handle cross-linear modifications
        next_id = element.get("next")
        if len(page_root.xpath("//add[@id='{}']".format(next_id[1:]))) != 0:  # i.e. not implemented for addSpan
            next_add = page_root.xpath("//add[@id='{}']".format(next_id[1:]))[0]
            cur_add_zone = page_tree.getelementpath(element).split("/")[0]
            next_add_zone = page_tree.getelementpath(next_add).split("/")[0]
            if cur_add_zone == next_add_zone:  # modifications in another zone are already handled by anchor
                ignore_adds.append(next_id[1:])
                from_anchor = processElement(zone_type, anchor_id, next_add, from_anchor, page_root, page_tree, displ_end_id, True)
    elif element.tag == "metamark" and (element.get("id") in displ_ids):  # handle subzones
        process_text_calls = 0
        displ_id = element.get("id")
        if len(page_root.xpath("//addSpan[@corresp='#{}']".format(displ_id))) != 0:
            processZone(zone_type, anchor_id, page_root, page_tree, displ_id, 0, 1000)
            zone_end = False
    elif element.tag == "anchor":
        if element.get("id") == displ_end_id:  # handle end of subzone
            zone_end = True
            return from_anchor
        if element.get("id") == handspan_id:
            hand = getOtherShelley(hand[:])  # preferred over prev_hand in case hand changes occurred within addSpan
        anch_id = "#" + element.get("id")
        if len(page_root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:  # Checks for anchor that references a different zone
            process_text_calls = 0
            processZone("", anch_id, page_root, page_tree, None, 0, 1000)
        else:
            new_page_id = "ox-ms_abinger_" + anch_id[1:].split(".")[0]
            if new_page_id != page_id and "ox-ms_abinger_c5" in new_page_id:  # Checks for referenced text on different page
                new_root, new_tree = getPageRoot(new_page_id, "page")
                if len(new_root.xpath("//zone[@corresp='{}']".format(anch_id))) != 0:  # zone on different page
                    process_text_calls = 0
                    processZone("", anch_id, new_root, new_tree, None, 0, 1000)
                elif len(new_root.xpath("//addSpan[@corresp='{}']".format(anch_id))) != 0:  # subzone on different page
                    displ_ids.append(element.get("id"))
                    new_addspan = new_root.xpath("//addSpan[@corresp='{}']".format(anch_id))[0]
                    addspan_parent = new_addspan.getparent()
                    while addspan_parent.tag != "zone":  # get parent zone
                        addspan_parent = addspan_parent.getparent()
                    new_zone_type = addspan_parent.get("type")
                    if new_zone_type != "main":
                        processZone(new_zone_type, addspan_parent.get("corresp"), new_root, new_tree, anch_id[1:], 0, 1000)  # by passing a displacement_id, processZone will get the end_id
                        zone_end = False
                    else:
                        processZone(new_zone_type, "", new_root, new_tree, anch_id[1:], 0, 1000)
                        zone_end = False
    elif element.tag == "delSpan" or (element.tag == "milestone" and element.get("unit") == "tei:head"):  # Breaks out of the line if a deletion spans multiple lines
        delspan = True
        delspan_id = element.get("spanTo")[1:]                                # Captures the ID of the anchor that marks the end of the deletion
        return from_anchor
    elif element.tag == "addSpan":
        if element.get("corresp"):
            if element.get("corresp")[1:] in displ_ids:
                delspan = True
                delspan_id = element.get("spanTo")[1:]
                return from_anchor
        if element.get("hand"):
            if element.get("hand")[1:] in ["mws", "pbs"]:
                prev_hand = getOtherShelley(element.get("hand")[1:])
            else:
                prev_hand = hand[:]
            hand = element.get("hand")[1:]
            handspan_id = element.get("spanTo")[1:]
    elif element.tag == "handShift":
        hand = element.get("new")[1:]
    # print tail text
    if (("del" not in page_tree.getelementpath(element.getparent())) or re.search(r'restore.*del', page_tree.getelementpath(element.getparent()))) and "metamark" not in page_tree.getelementpath(element.getparent()):
        if element.tag == "add" and element.get("id") and len(page_root.xpath("//add[@next='{}']".format("#" + element.get("id")))) != 0:  # i.e. don't process tail if it is a cross-linear addition
            pass
        else:
            if element.tail not in [None, "", "\n"] and (from_anchor is None):
                mod = True if "mod" in page_tree.getelementpath(element.getparent()) else False
                process_text_calls += 1
                processText(element.tail, mod)
    return from_anchor


def processLine(zone_type, anchor_id, line_element, from_anchor, page_root, page_tree, displ_end_id):
    global delspan
    global delspan_id
    global hand
    global prev_hand
    global handspan_id
    global ignore_adds
    global process_text_calls
    global zone_end
    process_text_calls = 0
    if line_element.text not in [None, "", "\n"] and from_anchor is None:
        process_text_calls += 1
        processText(line_element.text, False)           # Prints text at the start of a line
    line_children = line_element.getchildren()
    if (from_anchor is not None) and from_anchor in line_children:
        line_children = line_children[line_children.index(from_anchor):]
        from_anchor = None
    for line_child in line_children:
        if type(line_child) == etree._Element:
            if line_child.tag in ["mod", "hi", "add", "retrace", "damage", "unclear", "restore", "anchor", "metamark", "del", "delSpan", "addSpan", "handShift", "milestone"]:
                from_anchor = processElement(zone_type, anchor_id, line_child, from_anchor, page_root, page_tree, displ_end_id)
            if zone_end or delspan:
                return


def processZone(zone_type, anchor_id, page_root, page_tree, displacement_id, from_element, to_element):
    global delspan
    global delspan_id
    global hand
    global prev_hand
    global handspan_id
    global ignore_adds
    global zone_end
    global displ_ids
    global print_text
    global print_text_list
    zone_att = "type" if zone_type == "main" else "corresp"
    att_value = "main" if zone_att == "type" else anchor_id
    zone = page_root.xpath("//zone[@{}='{}']".format(zone_att, att_value))[0]
    ignore_adds = []
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
        for elem in zone:  # changed from zone.iter() to zone to make indexing easier
            if len(elem.findall(".//metamark[@function='displacement']")) != 0:
                for displ_mark in elem.findall(".//metamark[@function='displacement']"):
                    if displ_mark.get("id"):
                        displ_ids.append(displ_mark.get("id"))
            if elem.tag == "metamark" and elem.get("funtion") == "displacement" and elem.get("id"):
                displ_ids.append(elem.get("id"))
    zone_end = False
    for elem in zone:  # changed from zone.iter() to zone to make indexing easier
        if type(elem) == etree._Element:
            if zone_end:
                break
            if zone.index(elem) >= from_element and zone.index(elem) <= to_element:  # also add to_element for volume files
                if displacement_id:
                    if elem.tag == "anchor" and elem.get("id") == end_id:
                        zone_end = True
                        continue
                if not delspan:
                    if elem.tag == "delSpan":  # marks delSpan that is initiated outside of a line
                        delspan = True
                        delspan_id = elem.get("spanTo")[1:]                             # Captures the ID of the anchor that marks the end of the deletion
                    elif elem.tag == "addSpan" and elem.get("corresp"):  # marks displacement addSpan that is initiated outside of a line
                        if elem.get("corresp")[1:] in displ_ids and elem.get("corresp")[1:] != displacement_id:
                            delspan = True
                            delspan_id = elem.get("spanTo")[1:]
                    elif elem.tag == "line":
                        processLine(zone_type, anchor_id, elem, None, page_root, page_tree, end_id)
                    elif elem.tag == "metamark" and (elem.get("id") in displ_ids):
                        if len(zone.xpath("//addSpan[@corresp='#{}']".format(elem.get("id")))) != 0:
                            processZone(zone_type, anchor_id, page_root, page_tree, elem.get("id"), from_element, to_element)
                            zone_end = False
    #                    else:
    #                        anchr_id = "#" + elem.get("id")
    #                        if len(page_root.xpath("//zone[@corresp='{}']".format(anchr_id))) != 0:
    #                            processZone("", anchr_id, page_root, page_tree, None, 0, 1000)
                    elif elem.tag == "anchor":       # Checks for anchor that is not in a line and references a different zone; removed following code due to iteration change:  and "line" not in page_tree.getelementpath(elem)
                        anchr_id = "#" + elem.get("id")
                        if len(page_root.xpath("//zone[@corresp='{}']".format(anchr_id))) != 0:
                            processZone("", anchr_id, page_root, page_tree, None, 0, 1000)
                        else:      # Checks for referenced (sub)zone on different page
                            new_page_id = "ox-ms_abinger_" + anchr_id[1:].split(".")[0]
                            if new_page_id != page_id and "ox-ms_abinger_c5" in new_page_id:
                                new_root, new_tree = getPageRoot(new_page_id, "page")
                                if len(new_root.xpath("//zone[@corresp='{}']".format(anchr_id))) != 0:
                                    processZone("", anchr_id, new_root, new_tree, None, 0, 1000)
                                elif len(new_root.xpath("//addSpan[@corresp='{}']".format(anchr_id))) != 0:
                                    displ_ids.append(elem.get("id"))
                                    new_addspan = new_root.xpath("//addSpan[@corresp='{}']".format(anchr_id))[0]
                                    addspan_parent = new_addspan.getparent()
                                    while addspan_parent.tag != "zone":  # get parent zone
                                        addspan_parent = addspan_parent.getparent()
                                    new_zone_type = addspan_parent.get("type")
                                    if new_zone_type != "main":
                                        processZone(new_zone_type, addspan_parent.get("corresp"), new_root, new_tree, anchr_id[1:], 0, 1000)  # by passing a displacement_id, processZone will get the end_id
                                        zone_end = False
                                    else:
                                        processZone(new_zone_type, "", new_root, new_tree, anchr_id[1:], 0, 1000)
                                        zone_end = False
                    elif elem.tag == "milestone" and elem.get("unit") == "tei:p" and len(print_text) > 0:
                        print("MILESTONE!")
                        if print_text[-1] in [".", ",", ":", ";", "!", "?", '"']:
                            print_text += " "
                            print_text_list[-1] += " "
                        elif print_text[-1] == " ":
                            pass
                        else:
                            print_text += ". "
                            print_text_list[-1] += ". "
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
                        processLine(zone_type, anchor_id, elem, del_anchor, page_root, page_tree, end_id)
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
                if elem.get("hand")[1:] in ["mws", "pbs"]:
                    prev_hand = getOtherShelley(elem.get("hand")[1:])
                else:
                    prev_hand = hand[:]
                hand = elem.get("hand")[1:]
                handspan_id = elem.get("spanTo")[1:]
            if elem.tag == "anchor" and elem.get("id") == handspan_id:
                hand = getOtherShelley(hand[:])


def processLocus(locus, match_page):
    global page_id
    raw_page_ids = locus.get("target").split(" ")
    page_ids = [i.split("#")[-1] for i in raw_page_ids]
    if len(page_ids) == 1:
        from_element = 0
        to_element = 1000
        if locus.get("fromElement"):
            from_element = int(locus.get("fromElement")) - 1
        if locus.get("toElement"):
            to_element = int(locus.get("toElement")) - 1
        page_id = page_ids[0]
        root, tree = getPageRoot(page_id, "page")
        processZone("main", "", root, tree, None, from_element, to_element)
    else:
        for page_id in page_ids:
            if match_page == "":
                print("\nProcessing page", page_id, "\n")
                from_element = 0
                to_element = 1000
                root, tree = getPageRoot(page_id, "page")
                processZone("main", "", root, tree, None, from_element, to_element)
            else:
                if page_id == match_page:
                    from_element = 0
                    to_element = 1000
                    root, tree = getPageRoot(page_id, "page")
                    processZone("main", "", root, tree, None, from_element, to_element)


def processChapter(chap, vol_no):
    chapter_no = chap.get("n")
    if not auto_mode:
        raw_p_ids = []
        for locus in chap.findall(".//locus"):
            raw_p_ids.extend(locus.get("target").split(" "))
        p_ids = [i[-7:] for i in raw_p_ids]
        if mode_input in ["random", "r", "R"]:
            t0 = time.time()
            p_id = random.choice(p_ids)
            print("Page ID {}".format(p_id))
            for loc in chap.findall(".//locus"):
                if p_id in loc.get("target"):
                    match_id = "ox-ms_abinger_c" + p_id
                    processLocus(loc, match_id)
        else:
            p_input = ""
            while p_input not in (p_ids + ["all"]):
                p_input = input("Chapter {} contains the following pages:\n{}\nWhich page? ".format(chapter_no, p_ids + ["all"]))
            t0 = time.time()
            if p_input != "all":
                p_id = p_input[:]
                for loc in chap.findall(".//locus"):
                    if p_id in loc.get("target"):
                        match_id = "ox-ms_abinger_c" + p_id
                        processLocus(loc, match_id)
            else:  # automode for a single chapter
                for loc in chap.findall(".//locus"):
                    processLocus(loc, "")
        print(print_text)
        print(print_text_list)
        print(hand_list)
        print("\nNumber of Datamuse API calls:", dict_call_counter)
        t1 = time.time()
        print("Script duration:", t1 - t0)
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
    volume_id = "ox-frankenstein-volume_" + vol_no
    vol_root, vol_tree = getPageRoot(volume_id, "volume")
    chapters = vol_root.findall(".//msItem[@class='#chapter']")
    if not auto_mode:
        allowed_chaps = [ch.get("n") for ch in chapters]
        if mode_input in ["random", "r", "R"]:
            chap_no = random.choice(allowed_chaps)
            print("Chapter {}".format(chap_no))
            chapter = chapters[allowed_chaps.index(chap_no)]
            processChapter(chapter, vol_no)
        else:
            chap_input = ""
            while chap_input not in (allowed_chaps + ["all"]):
                chap_input = input("Volume {} contains the following chapters:\n{}\nWhich chapter? ".format(vol_no, allowed_chaps + ["all"]))
            if chap_input != "all":
                chap_no = chap_input[:]
                chapter = chapters[allowed_chaps.index(chap_no)]
                processChapter(chapter, vol_no)
            else:  # automode for a single volume
                for chapter in chapters:
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
prev_add_processed = False
displ_ids = []
with open("frankenstein-1818edition.txt") as f:
    edition_1818 = f.read()

mode_input = ""
while mode_input not in ["choose", "c", "C", "random", "r", "R"]:
    mode_input = input("Mode select: [c]hoose / [r]andom ")
if mode_input in ["random", "r", "R"]:
    auto_mode = False
    volume_no = random.choice(["i", "ii", "iii"])
    print("SELECTING RANDOM PAGE\nVolume {}".format(volume_no))
else:
    volume_input = ""
    while volume_input not in ["i", "ii", "iii", "all"]:
        volume_input = input("Which volume? (i/ii/iii/all) ")
    if volume_input in ["i", "ii", "iii"]:
        auto_mode = False
        volume_no = volume_input[:]
        processVolume(volume_no)
    else:
        auto_mode = True
        for volume_no in ["i", "ii", "iii"]:
            processVolume(volume_no)
