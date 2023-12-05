import dns.message
import dns.asyncquery
import asyncio
import sys

x = int(sys.argv[1])

IP = ['8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1', '208.67.222.222', '208.67.220.220', '172.17.176.1'] # '76.76.2.0', '9.9.9.9', '76.76.19.19'

async def solve (num, path):
    # print('Solving for ', num, ' : ', path)
    # create a dns message object with the query 
    q = dns.message.make_query(path, 'TXT')
    # send the query using dns asyncquery udp and await the response
    try:
        res = await dns.asyncquery.udp(q, IP[x], timeout=2)
            
        # printing the result
        # print(res)
    except:
        res = None
    return res
    return res

async def main ():
    content = []
    promises = []

    # open the top-10k.csv file for reading
    with open('top-10k.csv', 'r') as source_file:
        content = source_file.readlines()

    for i, line in enumerate(content[x*1000:(x+1)*1000]):
        # split the line into a list of columns
        columns = line.split(',')
        # get the domain name from the second column
        domain = columns[1]

        promises.append( solve(i, domain) )
                
        # break after 10,000 lines
        if i == 1000:
            break

    print('Writing results to file')
    with open(f'results_{x}.txt', 'a') as target_file:

        print('Waiting for all coroutines to finish')
        results = await asyncio.gather(*promises, return_exceptions=True)

        # iterate over the results
        for result in results:
            print('----------')
            print(result)
            if result is None:
                target_file.write('No answer\n')
                continue
            # get the domain name from the question
            domain = result.question[0].name
            # get the answer from the result
            answer = str(result).replace('\n', '|')
            # write the domain and answer to the file
            target_file.write(str(domain) + ' : ' + str(answer) + '\n')

        target_file.write('RESULTS: ' + str(len(results)))
        print('RESULTS: ', len(results))
        target_file.write('RESULTS: ' + str(len([res for res in results if not res is None])))
        print('RESULTS: ', len([res for res in results if not res is None]))
asyncio.run(main())
