import socket
import threading
import argparse
import json
import hashlib

class DHTNode:
    def __init__(self, node_id, port, nodes):
        self.node_id = node_id
        self.port = port
        self.nodes = nodes       
        self.store = {}

        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('127.0.0.1', port))
        self.server.listen(5)

    def start(self):
        print(f"[Node {self.node_id}] listening on port {self.port}")
        threading.Thread(target=self.accept_loop, daemon=True).start()

    def accept_loop(self):
        while True:
            conn, addr = self.server.accept()
            threading.Thread(target=self.handle_conn, args=(conn,), daemon=True).start()

    def hash_key(self, key):
        h = int(hashlib.sha1(key.encode()).hexdigest(), 16)
        return h % len(self.nodes)

    def get_responsible_node(self, key):
        idx = self.hash_key(key)
        return self.nodes[idx]   

    def forward(self, host, port, msg):
        s = socket.socket()
        s.connect((host, port))
        s.sendall(msg.encode())
        resp = s.recv(65536).decode()
        s.close()
        return resp

    def handle_conn(self, conn):
        with conn:
            data = conn.recv(65536).decode()
            if not data:
                return

            msg = json.loads(data)
            typ = msg["type"]
            key = msg["key"]

            owner = self.get_responsible_node(key)
            owner_id, owner_host, owner_port = owner

            if owner_id != self.node_id:
                resp = self.forward(owner_host, owner_port, data)
                conn.sendall(resp.encode())
                return

            if typ == "PUT":
                self.store[key] = msg["value"]
                conn.sendall(json.dumps({"status": "OK"}).encode())

            elif typ == "GET":
                val = self.store.get(key)
                conn.sendall(json.dumps({"status": "OK", "value": val}).encode())

def send(host, port, msg):
    s = socket.socket()
    s.connect((host, port))
    s.sendall(json.dumps(msg).encode())
    resp = s.recv(65536).decode()
    s.close()
    return resp

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--nodes", required=True)
    args = parser.parse_args()

    node_list = []
    for n in args.nodes.split(","):
        nid, host, port = n.split(":")
        node_list.append((nid, host, int(port)))

    node = DHTNode(args.id, args.port, node_list)
    node.start()

    print("Node ready.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down...")
