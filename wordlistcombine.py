import re

filenames = ["chat/678676683", "chat/677708658", "chat/676838428", "chat/675768252", "chat/674845198", "chat/673752090", "chat/672813291", "chat/671981070", "chat/670857593"]

for filepath in filenames:
    print(f"opening {filepath}.txt")
    log = open(f'xqctext.txt','a+')
    with open(f"{filepath}.txt", errors='ignore') as fp:
        lines = fp.readlines()
        for line in lines:
            text = re.sub(r'<\w+>', '', line[10:])
            text2 = re.sub(r'[^0-9a-zA-Z]', ' ', text)
            log.write(f"{text2}\n")
    log.close()