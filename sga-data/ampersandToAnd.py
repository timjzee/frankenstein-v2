import json

with open("./output/text_list_processed.json") as f:
    text_list = json.loads(f.read())

text_list_ands = []

for word in text_list:
    if word == "&":
        text_list_ands.append("and")
    else:
        text_list_ands.append(word)

with open("./output/text_list_processed_ands.json", "w") as f:
    f.write(json.dumps(text_list_ands))
