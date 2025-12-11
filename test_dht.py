import json
import socket
import time

def send(host, port, msg):
    s = socket.socket()
    s.connect((host, port))
    s.sendall(json.dumps(msg).encode())
    resp = s.recv(65536).decode()
    s.close()
    return resp


def test_sequence():
    print("=== Distributed Hash Table Test ===")

    print("\nTest 1: PUT('apple', 'red') → random node (5000)")
    r1 = send("127.0.0.1", 5000, {
        "type": "PUT",
        "key": "apple",
        "value": "red"
    })
    print("Response:", r1)

    print("\nTest 2: GET('apple') from another node (5001)")
    r2 = send("127.0.0.1", 5001, {
        "type": "GET",
        "key": "apple"
    })
    print("Response:", r2)

    print("\nTest 3: PUT/GET หลายค่าเพื่อดูการกระจาย")
    test_data = {
        "banana": "yellow",
        "grape": "purple",
        "melon": "green",
        "water": "blue"
    }

    for k, v in test_data.items():
        resp = send("127.0.0.1", 5002, {
            "type": "PUT",
            "key": k,
            "value": v
        })
        print(f"PUT({k}, {v}) →", resp)

    print("\nอ่านกลับทั้งหมด (ยิงไปที่ node เดียว เพื่อทดสอบ routing):")
    for k in test_data.keys():
        resp = send("127.0.0.1", 5000, {
            "type": "GET",
            "key": k
        })
        print(f"GET({k}) →", resp)

    print("\n=== Test Completed ===")


if __name__ == "__main__":
    time.sleep(1)
    test_sequence()
