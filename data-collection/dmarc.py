import dns.message
import dns.asyncquery
import asyncio
import sys
from random import choice, randint, random

C = 1.3
FAC = 5
MUL = int(C**(FAC-1))
BASEMUL = MUL
cnt = 0

async def solve (num, path):
    
    global cnt
    global MUL
    global BASEMUL

    D = 1.1
    TMO = 2
    THRSH = 100

    IP = ['8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1', '172.17.176.1', '208.67.222.222', '208.67.220.220'] # '76.76.2.0', '9.9.9.9', '76.76.19.19'
    NIP = ['185.228.168.9', '185.228.169.9', '76.76.19.19', '76.223.122.150', '94.140.14.14', '94.140.15.15', '9.9.9.9', '149.112.112.112']
    MIP = ['8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1', '172.17.176.1', '208.67.222.222', '208.67.220.220', '185.228.168.9', '185.228.169.9', '76.76.19.19', '76.223.122.150', '94.140.14.14', '94.140.15.15', '9.9.9.9', '149.112.112.112']
    # create a dns message object with the query 

    await asyncio.sleep(randint(0, 80 * MUL) / 1000)

    q = dns.message.make_query(path, 'TXT')
    
    # send the query using dns asyncquery udp and await the response
    try:
        # random choice from IP list
        res = await dns.asyncquery.udp(q, choice(IP), timeout=TMO)
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
            res = await dns.asyncquery.udp(q, choice(MIP), timeout=TMO)
        except:
            res = None

    if random() > 0.5 and res is None:
        await asyncio.sleep(randint(0, 20) / 1000)
        try:
            # random choice from NIP list
            res = await dns.asyncquery.udp(q, choice(NIP), timeout=TMO)
        except:
            res = None

    return res

async def main ():
    content = []
    promises = []
    global FAC
    global MUL

    print('FACTOR: ', FAC)

    # open the top-10k.csv file for reading
    with open('base-1m.csv', 'r') as source_file:
        content = source_file.readlines()

    for i, line in enumerate(content):
        # split the line into a list of columns

        domain = '_dmarc.' + line.strip()

        promises.append(asyncio.ensure_future( solve(i, domain) ) )
        await asyncio.sleep(randint(0, 30) / 1000)
                
        # break after 10,000 lines
        if i == (1000 * FAC):
            break

    print('Writing results to file')
    with open(f'tral.txt', 'w') as target_file:

        print('Waiting for all coroutines to finish')
        results = await asyncio.gather(*promises, return_exceptions=True)

        target_file.write('RESULTS: ' + str(len(results)))
        print('RESULTS: ', len(results))
        target_file.write('RESULTS: ' + str(len([res for res in results if not res is None])))
        print('RESULTS: ', len([res for res in results if not res is None]))

        # iterate over the results
        for result in results:
            print('----------')
            print(result)
            if result is None:
                target_file.write('No answer\n')
                continue
            # get the domain name from the question
            domain = result.question[0].name
            if len(result.answer) == 0:
                target_file.write(str(domain) + ' : ' + 'NXDOMAIN\n')
                continue
            # get the answer from the result
            answer = result.answer[0].to_text()
            # write the domain and answer to the file
            target_file.write(str(domain) + ' : ' + str(answer) + '\n')

        target_file.write('RESULTS: ' + str(len(results)))
        print('RESULTS: ', len(results))
        target_file.write('RESULTS: ' + str(len([res for res in results if not res is None])))
        print('RESULTS: ', len([res for res in results if not res is None]))

asyncio.run(main())
