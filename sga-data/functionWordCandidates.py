import json
import re


word_dictionary = {}


def countWords(text_list):
    temp_dictionary = {}
    for word in text_list:
        if word in temp_dictionary:
            temp_dictionary[word] += 1
        else:
            temp_dictionary[word] = 1
        if word not in word_dictionary:
            word_dictionary[word] = 0
    return temp_dictionary


def tokenize(text):
    split_list = [' ', '!', '(', ';', "'", '?', '\n', '^', ')', '–', '.', ',', '—', '>', '"', ':', '=', '-']
    raw_split = re.split(r"[{}]+".format(re.escape("".join(split_list))), text)
    word_list = [wrd.lower() for wrd in raw_split if len(wrd) > 0]
    return word_list


with open("./output/text_list_processed_ands.json") as f:
    frankenstein_list = json.loads(f.read())

frankenstein_d = countWords(frankenstein_list)
print(len(frankenstein_d))

with open("/Users/tim/GitHub/frankenstein-v2/analysis/pca_texts/LAMB_glenarvon.txt") as f:
    glenarvon = f.read()

glenarvon_list = tokenize(glenarvon)
with open("/Users/tim/GitHub/frankenstein-v2/analysis/tokenized_texts/lam_glenarvon.json", "w") as f:
    f.write(json.dumps(glenarvon_list))

glenarvon_d = countWords(glenarvon_list)
print(len(glenarvon_d))

with open("/Users/tim/GitHub/frankenstein-v2/analysis/reference_set/mws_the-last-man.txt") as f:
    thelastman = f.read()

thelastman_list = tokenize(thelastman)
with open("/Users/tim/GitHub/frankenstein-v2/analysis/tokenized_texts/mws_the-last-man.json", "w") as f:
    f.write(json.dumps(thelastman_list))

thelastman_d = countWords(thelastman_list)
print(len(thelastman_d))

with open("/Users/tim/GitHub/frankenstein-v2/analysis/reference_set/pbs_st-irvyne.txt") as f:
    stirvyne = f.read()

stirvyne_list = tokenize(stirvyne)
with open("/Users/tim/GitHub/frankenstein-v2/analysis/tokenized_texts/pbs_st-irvyne.json", "w") as f:
    f.write(json.dumps(stirvyne_list))

stirvyne_d = countWords(stirvyne_list)
print(len(stirvyne_d))

with open("/Users/tim/GitHub/frankenstein-v2/analysis/reference_set/pbs_zastrozzi.txt") as f:
    zastrozzi = f.read()

zastrozzi_list = tokenize(zastrozzi)
with open("/Users/tim/GitHub/frankenstein-v2/analysis/tokenized_texts/pbs_zastrozzi.json", "w") as f:
    f.write(json.dumps(zastrozzi_list))

zastrozzi_d = countWords(zastrozzi_list)
print(len(zastrozzi_d))

for word in word_dictionary:
    if word in frankenstein_d:
        word_dictionary[word] += frankenstein_d[word] / len(frankenstein_list)
    if word in glenarvon_d:
        word_dictionary[word] += glenarvon_d[word] / len(glenarvon_list)
    if word in thelastman_d:
        word_dictionary[word] += thelastman_d[word] / len(thelastman_list)
    if word in stirvyne_d:
        word_dictionary[word] += stirvyne_d[word] / len(stirvyne_list)
    if word in zastrozzi_d:
        word_dictionary[word] += zastrozzi_d[word] / len(zastrozzi_list)

sorted_dictionary = sorted([(v, k) for k, v in word_dictionary.items()])[::-1]
