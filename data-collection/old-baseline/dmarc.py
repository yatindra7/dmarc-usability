import dns.resolver

def get_dmarc_record(domain):
    try:
        answers = dns.resolver.resolve('_dmarc.' + domain, 'TXT')
        for rdata in answers:
            for txt_string in rdata.strings:
                print('DMARC record for {}: {}'.format(domain, txt_string.decode()))
    except dns.resolver.NoAnswer:
        print('No DMARC record found for {}'.format(domain))
    except dns.resolver.NXDOMAIN:
        print('No such domain {}'.format(domain))
    except Exception as e:
        print('Error occurred: {}'.format(e))

# Test the function
get_dmarc_record('google.com')
