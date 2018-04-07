import json
import re

with open("./output/text.txt") as f:
    text = f.read()

with open("./output/text_list.json") as f:
    text_list = json.loads(f.read())

with open("./output/hand_list.json") as f:
    hand_list = json.loads(f.read())

# splitting regex

# split_regex = "".join(["[^A-Za-z", "\U00C0-\U00FF", "\U0100-\U01BF", "\U01C4-\U02AF", "\U0386\U0388-\U03FF", "\U0400-\U0481\U048A-\U0527", "\U05D0-\U05EA\U05F0-\U05F4", "\U0620-\U065F\U066E-\U06D3\U06D5\U06DC", "\U1E00-\U1EFF", "\U1F00-\U1FBC\U1FC2-\U1FCC\U1FD0-\U1FDB\U1FE0-\U1FEC\U1FF2-\U1FFC", "\U03E2-\U03EF\U2C80-\U2CF3", "\U10A0-\U10FF", "]+"])

split_list = [' ', '!', '(', ';', "'", '?', '\n', '^', ')', '–', '.', ',', '—', '>', '"', ':', '=']
# split_list = [' ']

# change within word hand changes

counter = 0
complete = True
incomplete_word = None
mws_score = 0
pbs_score = 0
new_text_list = []
new_hand_list = []
for segment in text_list:
    hand = hand_list[counter]
    # handle all completed words in a fragment
    if complete:
        word_list = re.findall(r'[^{}]+(?=[{}])'.format(re.escape("".join(split_list)), re.escape("".join(split_list))), segment)
        new_text_list.extend(word_list)
        new_hand_list.extend([hand] * len(word_list))
    else:
        if segment[0] in split_list:
            new_text_list.append(incomplete_word)
            majority_hand = "mws" if mws_score > pbs_score else "pbs"
            new_hand_list.append(majority_hand)
            print(incomplete_word, "mws:", mws_score, "pbs:", pbs_score, "hand:", majority_hand)
            incomplete_word = None
            mws_score = 0
            pbs_score = 0
            complete = True
            word_list = re.findall(r'[^{}]+(?=[{}])'.format(re.escape("".join(split_list)), re.escape("".join(split_list))), segment)
            new_text_list.extend(word_list)
            hand = hand_list[counter]
            new_hand_list.extend([hand] * len(word_list))
        else:  # i.e. if incomplete and start of segment is part of a word
            word_part = re.match(r'^[^{}]+'.format(re.escape("".join(split_list))), segment).group()
            incomplete_word += word_part[:]
            if hand == "mws":
                mws_score += len(word_part)
            elif hand == "pbs":
                pbs_score += len(word_part)
#            segment = re.sub(r'^[^ ]+', '', segment)
            word_list = re.findall(r'[^{}]+(?=[{}])'.format(re.escape("".join(split_list)), re.escape("".join(split_list))), segment[len(word_part):])
            if len(word_list) == 0 and segment[-1] not in split_list:
#                if " " in segment:  # i.e. if one space in segment
                if re.search(r'[{}]'.format(re.escape("".join(split_list))), segment):
                    new_text_list.append(incomplete_word)
                    majority_hand = "mws" if mws_score > pbs_score else "pbs"
                    new_hand_list.append(majority_hand)
                    print(incomplete_word, "mws:", mws_score, "pbs:", pbs_score, "hand:", majority_hand)
                    incomplete_word = None
                    mws_score = 0
                    pbs_score = 0
                    complete = True
            else:
                new_text_list.append(incomplete_word)
                majority_hand = "mws" if mws_score > pbs_score else "pbs"
                new_hand_list.append(majority_hand)
                print(incomplete_word, "mws:", mws_score, "pbs:", pbs_score, "hand:", majority_hand)
                incomplete_word = None
                mws_score = 0
                pbs_score = 0
                new_text_list.extend(word_list)
                new_hand_list.extend([hand] * len(word_list))
                complete = True
    # handle start of incompleted words
    if (segment[-1] not in split_list) and complete:
        complete = False
        word_start = re.search(r"[^{}]+$".format(re.escape("".join(split_list))), segment).group()
        if hand == "mws":
            mws_score += len(word_start)
        elif hand == "pbs":
            pbs_score += len(word_start)
        incomplete_word = word_start[:]
    counter += 1

if incomplete_word:
    new_text_list.append(incomplete_word)
    majority_hand = "mws" if mws_score > pbs_score else "pbs"
    new_hand_list.append(majority_hand)
    print(incomplete_word, "mws:", mws_score, "pbs:", pbs_score, "hand:", majority_hand)


new_text_list_lower = [wrd.lower() for wrd in new_text_list]

with open("./output/text_list_processed.json", "w") as f:
    f.write(json.dumps(new_text_list_lower))

with open("./output/hand_list_processed.json", "w") as f:
    f.write(json.dumps(new_hand_list))
