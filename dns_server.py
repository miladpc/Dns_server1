import socket
import threading
from dnslib import DNSRecord, DNSHeader, RR, A

class DNSServer:
    def init(self, host='127.0.0.1', port=5353):
        self.host = host
        self.port = port
        
        self.records = {
            "game-server-iran": ("192.168.1.1", 60),  # تغییر دهید
            "game-server-germany": ("192.168.yy.yy", 60)  # تغییر دهید
        }

        self.cache = {}
        self.lock = threading.Lock()

    def start(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self.host, self.port))
            print(f"DNS server is running on {self.host}:{self.port}")

            while True:
                data, addr = sock.recvfrom(512)
                print(f"Received request from {addr}")
                threading.Thread(target=self.handle_request, args=(data, addr, sock)).start()
        except Exception as e:
            print(f"An error occurred while starting the server: {str(e)}")

    def handle_request(self, data, addr, sock):
        try:
            request = DNSRecord.parse(data)
            response = DNSRecord(DNSHeader(id=request.header.id, aa=1, rcode=0))

            query_name = str(request.q.qname).rstrip('.')

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

        except Exception as e:
            print(f"An error occurred while handling the request: {str(e)}")

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

def main():
    host = input("Enter the server IP (default is 127.0.0.1): ") or '127.0.0.1'
    try:
        port = int(input("Enter the server port (default is 5353): ")) or 5353
    except ValueError:
        port = 5353   #If the input is invalid, use the default port

    server_ips = {
        "game-server-iran": input("Enter the IP of the Iranian game server: "),
        "game-server-germany": input("Enter the IP of the German game server: ")
    }

    server = DNSServer(host, port)
    server.start()

if __name__ == "__main__":
    main()

