import dns.message
import dns.asyncquery
import asyncio
import json
from random import choice, randint, random

# Todo: scaling work

C = 1.3
FAC = 5
MUL = int(C**(FAC-1))
BASEMUL = MUL
cnt = 0

async def extract_ips(record):
    parts = record.split()
    ipv4s = [part[4:] for part in parts if part.startswith('ip4:')]
    ipv6s = [part[4:] for part in parts if part.startswith('ip6:')]
    return ipv4s, ipv6s

async def get_ips_for_domain(domain, ip):

    # print('=====')
    # print(domain)

    TMO = 2

    global MUL
    await asyncio.sleep(randint(0, 80 * MUL) / 1000)

    ipv4s = []
    ipv6s = []
    query = dns.message.make_query(domain, 'TXT')
    try:
        response = await dns.asyncquery.udp(query, ip, timeout=TMO)
        print(response)
    except Exception as e:
        # print(e)
        # print(domain)
        return None

    for rrset in response.answer:
        for rr in rrset:
            if rr.rdtype == dns.rdatatype.TXT and (rr.to_text().startswith('v=spf1') or rr.to_text().startswith('spf2.0/')):
                print(f'{domain}: {rr.to_text()}')
                record_ipv4s, record_ipv6s = await extract_ips(rr.to_text())
                ipv4s.extend(record_ipv4s)
                ipv6s.extend(record_ipv6s)
                if 'include:' in rr.to_text():
                    included_domains = [part[8:] for part in rr.to_text().split() if part.startswith('include:')]
                    for included_domain in included_domains:
                        res = await solve(included_domain)
                        if res is None:
                            continue
                        ipv4s, ipv6s = res
                        ipv4s.extend(included_ipv4s)
                        ipv6s.extend(included_ipv6s)
    return ipv4s, ipv6s

async def solve (path):
    
    global cnt
    global MUL
    global BASEMUL

    D = 1.1
    THRSH = 100

    IP = ['8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1', '172.17.176.1', '208.67.222.222', '208.67.220.220'] # '76.76.2.0', '9.9.9.9', '76.76.19.19'
    NIP = ['185.228.168.9', '185.228.169.9', '76.76.19.19', '76.223.122.150', '94.140.14.14', '94.140.15.15', '9.9.9.9', '149.112.112.112']
    MIP = ['8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1', '172.17.176.1', '208.67.222.222', '208.67.220.220', '185.228.168.9', '185.228.169.9', '76.76.19.19', '76.223.122.150', '94.140.14.14', '94.140.15.15', '9.9.9.9', '149.112.112.112']

    await asyncio.sleep(randint(0, 80 * MUL) / 1000)
    
    # send the query using dns asyncquery udp and await the response
    try:
        # random choice from IP list
        res = await get_ips_for_domain(path, choice(IP))
        cnt += 1

        if cnt > THRSH and MUL > BASEMUL:
            MUL = BASEMUL

    except:
        res = None
        if MUL == BASEMUL:
            MUL *= D
        cnt = 0

    if res is None:
        await asyncio.sleep(randint(0, 30) / 1000)
        try:
            # random choice from NIP list
            res = await get_ips_for_domain(path, choice(MIP))
        except:
            res = None

    if random() > 0.5 and res is None:
        await asyncio.sleep(randint(0, 20) / 1000)
        try:
            # random choice from NIP list
            res = await get_ips_for_domain(path, choice(NIP))
        except:
            res = None

    return res

async def main():
    zr = 0
    with open('base-1m.csv', 'r') as f:
        domains = [line.strip() for line in f]
    results = []
    fresults = []
    for domain in domains[:1000]:
        results.append(solve(domain) )
        await asyncio.sleep(randint(0, 30) / 1000)
    
    results = await asyncio.gather(*results, return_exceptions=True)

    with open('output.json', 'w') as f:
        for i, res in enumerate(results):
            if res is None:
                zr += 1
                continue

            ipv4s, ipv6s = res

            if ipv4s or ipv6s:
                print(res)
            result = {
                'domain': domain,
                'ip4': ipv4s,
                'ip6': ipv6s
            }
            fresults.append(res)

        json.dump(fresults, f)
    
    print(f'Printed results: {len(results)} | Zero results: {zr}')

# Run the main function
asyncio.run(main())
