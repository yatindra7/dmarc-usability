import dns.resolver
import time
from queue import Queue

def get_all_txt_records(domain, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            answers = dns.resolver.resolve(domain, 'TXT')
            return [record.strings for record in answers]
        except dns.resolver.NXDOMAIN:
            print(f"No DNS record found for {domain}")
            return []
        except dns.resolver.NoAnswer:
            print(f"No TXT record found for {domain}")
            return []
        except dns.resolver.LifetimeTimeout:
            retries += 1
            print(f"DNS resolution timed out for {domain}. Retrying... ({retries}/{max_retries})")
            time.sleep(1)  # Add a delay before retrying

    print(f"Failed to resolve DNS for {domain} after {max_retries} retries.")
    return []

def get_spf_record(txt_records):
    for record in txt_records:
        for entry in record:
            if b'v=spf1' in entry:
                return entry.decode('utf-8')
    return None

def extract_redirect_domain(spf_record):
    # Extract the redirected domains from an SPF record
    domains = []
    parts = spf_record.split()
    for part in parts:
        if part.startswith('redirect='):
            domains.append(part.split('=')[1])
        elif part.startswith('include:'):
            domains.append(part.split(':')[1])
    return domains if domains else None

def get_spf(domain):
    re_domains = Queue()
    re_domains.put(domain)

    
    while not re_domains.empty():
        current_domain = re_domains.get() 
        txt_records = get_all_txt_records(current_domain)

        if not txt_records:
            # print(f"\n{current_domain} has no TXT records \n")
            continue

        spf_record = get_spf_record(txt_records)
        if not spf_record:
            continue
        if spf_record:
            print(f"\nSPF record for {current_domain}:")
            print(spf_record)

            redirected_domains_list = extract_redirect_domain(spf_record)
            if redirected_domains_list:
                print(f"\nFollowing redirects for {current_domain} to:")
                for redirected_domain in redirected_domains_list:
                    print(redirected_domain)
                    redirected_domains.put(redirected_domain)


if __name__ == "__main__":
    domains = ["example.com", "google.com"]
    
    for domain in domains:
        get_spf(domain)
