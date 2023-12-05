import csv
import re

def strip_nonalnum_re(word):
    return re.sub(r"^\W+|\W+$", "", word)

keys = ['v', 'p', 'pct', 'rua', 'ruf', 'sp', 'fo', 'rf', 'adkim', 'aspf', 'ri']

with open('dmarc_results_150k-196k.txt', 'r') as infile, open('ana_output_150k-196k.csv', 'w', newline='') as outfile:
    writer = csv.DictWriter(outfile, fieldnames=['domain'] + keys)
    writer.writeheader()
    cnt = 0
    for line in infile:
        if 'NXDOMAIN' in line or 'No answer' in line:
            continue
        domain, _, rest = line.partition(':')
        domain = domain.strip()

        try:
            tmp = "IN TXT"
            rest = rest[rest.index(tmp) + len(tmp):].strip()[1:-1]
            # print(rest)
            if rest:
                fields = dict(strip_nonalnum_re(item).split('=') for item in rest.split(';') if '=' in item)
                for key in keys:
                    fields.setdefault(key, 'default')
                writer.writerow({'domain': domain, **fields})
                cnt += 1
        except:
            print("Error writing: " + line)
    print('Count:', cnt)
