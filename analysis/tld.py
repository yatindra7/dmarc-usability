from tldextract import extract

# extracting the top level domains

dct = {}

with open('top-1m.csv', 'r') as source_file, open('base-1m.csv', 'w') as target_file:
    for i, line in enumerate(source_file):
        eurl = extract(line.split(',')[1])
        
        domain = eurl.domain + '.' + eurl.suffix

        if domain in dct:
            continue
        dct[domain] = True
    
    for key in dct:
        target_file.write(key + '\n')
    print(len(dct))
        
