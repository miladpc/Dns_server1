import socket
import threading
from dnslib import DNSRecord, DNSHeader, RR, A

class DNSServer:
    def __init__(self, host='127.0.0.1', port=53):
        self.host = host
        self.port = port
        
         
        self.records = {
            "1.1.1.1": ("1.1.1.1", 60),   #مثال IP
            "8.8.8.8": ("8.8.8.8", 60)    #مثال 
        }

         #کش با TTL
        self.cache = {}
        self.lock = threading.Lock()

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        print(f"DNS server is running on {self.host}:{self.port}")

        while True:
            data, addr = sock.recvfrom(512)
            print(f"Received request from {addr}")
            threading.Thread(target=self.handle_request, args=(data, addr, sock)).start()

    def handle_request(self, data, addr, sock):
        request = DNSRecord.parse(data)
        response = DNSRecord(DNSHeader(id=request.header.id, aa=1, rcode=0))

        query_name = str(request.q.qname)

        with self.lock:
            if query_name in self.cache:
                ip, ttl = self.cache[query_name]
                response.add_answer(RR(query_name, A, rdata=ip, ttl=ttl))
                print(f"Cache hit for {query_name}")
            else:
                if query_name in self.records:
                    ip, ttl = self.records[query_name]
                    response.add_answer(RR(query_name, A, rdata=ip, ttl=ttl))
                    self.cache[query_name] = (ip, ttl)
                    print(f"Added {query_name} to cache")
                else:
                    response.header.rcode = 3   #NXDOMAIN: No such domain
                    print(f"No records found for {query_name}")

            self.cleanup_cache()
        
        sock.sendto(response.pack(), addr)

    def cleanup_cache(self):
        to_delete = []
        for key, (ip, ttl) in list(self.cache.items()):
            if ttl <= 0:
                to_delete.append(key)
            else:
                self.cache[key] = (ip, ttl - 1)

        for key in to_delete:
            del self.cache[key]
            print(f"Removed {key} from cache due to TTL expiration")

if __name__ == "__main__":
     #وارد کردن IP و پورت
    host = input("Enter the server IP (default khodesh 127.0.0.1): ")
    if not host:
        host = '127.0.0.1'
        
    try:
        port = int(input("Enter the server port (default khodesh 5353 ya 8080 ya 53 ): "))
    except ValueError:
        port = 5353   #اگر ورودی نادرست باشد از پورت پیش‌فرض استفاده می‌شود

    server = DNSServer(host, port)
    server.start()
