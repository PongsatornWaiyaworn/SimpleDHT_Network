# Distributed Hash Table (DHT) — Proof of Concept

โปรเจกต์นี้เป็นตัวอย่างการทำงานของ **Distributed Hash Table (DHT)** อย่างง่าย ที่แสดงให้เห็นถึงกลไกพื้นฐานของการกระจายการจัดเก็บข้อมูลแบบ key-value ไปยังหลายโหนด (node) โดยใช้หลักการ Consistent Hashing (ผ่านการกำหนด Consistent Indexing ตามจำนวนโหนด) และการส่งต่อคำสั่ง (Message Forwarding)

## โครงสร้างและการทำงานของระบบ

ระบบนี้ประกอบด้วยโหนดหลายตัวที่ร่วมกันรับผิดชอบในการจัดเก็บ key-value คู่ต่าง ๆ การกำหนด "เจ้าของ" (Owner) ของ key จะใช้ **Hash Function (SHA-1)** เพื่อแปลง key เป็นค่าแฮช จากนั้นนำมาหาตำแหน่งของโหนดที่รับผิดชอบ

### การกำหนด Node Owner

โหนดที่รับผิดชอบ key จะถูกคำนวณตามสูตร:

$$
node\_owner\_index = sha1(key) \bmod len(nodes)
$$

* **key**: ข้อมูลที่ต้องการจัดเก็บ/ดึง
* **sha1(key)**: ค่าแฮชของ key ที่ได้จาก SHA-1 (ในทางปฏิบัติ มักใช้ค่าแฮชตัวเลข)
* **len(nodes)**: จำนวนโหนดทั้งหมดในระบบ

### การสื่อสารและการส่งต่อ (Forwarding)

การติดต่อระหว่างโหนดและไคลเอนต์ใช้ **TCP Socket**

1.  **Client Request:** ไคลเอนต์ส่งคำสั่งไปยังโหนดใดก็ได้ในระบบ (เช่น Node A)
2.  **Ownership Check:** โหนดที่รับคำสั่ง (Node A) คำนวณหาเจ้าของ key ที่แท้จริง (เช่น Node B)
3.  **Forwarding:**
    * **ถ้า Node A เป็นเจ้าของ:** Node A ประมวลผลคำสั่งทันที
    * **ถ้า Node A ไม่ใช่เจ้าของ:** Node A จะ **ส่งต่อ (forward)** คำสั่งไปยังโหนดเจ้าของที่ถูกต้อง (Node B)
4.  **Response:** โหนดเจ้าของประมวลผลคำสั่งและส่งผลลัพธ์กลับไปยังโหนดเริ่มต้น (Node A) ซึ่งจะส่งต่อไปยังไคลเอนต์

**ตัวอย่าง Flow:**

`Client → Node A (ไม่ใช่เจ้าของ) → Node B (เจ้าของ) → Node A → Client`

> หากคุณอยากเห็น **ตัวอย่าง TCP** และเข้าใจการทำงานของระบบ Client/Server, สามารถดูได้ที่ GitHub ของโปรเจกต์นี้:  
> [SimpleTCP Client-Server](https://github.com/PongsatornWaiyaworn/SimpleTCP_client-server.git)

### รูปแบบคำสั่งที่รองรับ

* **PUT**: `{"type": "PUT", "key": "...", "value": "..."}`
    * ใช้สำหรับจัดเก็บค่าในโหนดเจ้าของ key นั้น
* **GET**: `{"type": "GET", "key": "..."}`
    * ใช้สำหรับดึงค่าจากโหนดเจ้าของ key นั้น

### การระบุโหนด (Node Identification)

โหนดจะถูกระบุด้วย ID, Host, และ Port ในรูปแบบ `id:host:port`

**ตัวอย่าง:**
`1:127.0.0.1:5000,2:127.0.0.1:5001,3:127.0.0.1:5002`

---

## วิธีรันระบบ (Start Nodes)

ให้เปิด **3 Terminal** เพื่อรันโหนด 3 ตัว โดยทุกโหนดต้องระบุรายชื่อโหนดทั้งหมดในระบบเหมือนกัน

| Terminal | Node ID | Port | Command |
| :---: | :---: | :---: | :--- |
| **1** | 1 | 5000 | `python poc_dht.py --id 1 --port 5000 --nodes 1:127.0.0.1:5000,2:127.0.0.1:5001,3:127.0.0.1:5002` |
| **2** | 2 | 5001 | `python poc_dht.py --id 2 --port 5001 --nodes 1:127.0.0.1:5000,2:127.0.0.1:5001,3:127.0.0.1:5002` |
| **3** | 3 | 5002 | `python poc_dht.py --id 3 --port 5002 --nodes 1:127.0.0.1:5000,2:127.0.0.1:5001,3:127.0.0.1:5002` |

เมื่อโหนดพร้อมใช้งาน คุณจะเห็นข้อความคล้าย:
```
[Node X] listening on port XXXX 
Node ready.
```

---

## วิธีทดสอบระบบ (Testing)

1. รันระบบให้เสร็จครบทั้ง 3 node ก่อน
3. จากนั้นรันไฟล์test ไฟล์ที่แยกต่างหาก
```
python test_dht.py
```

### Output ที่คาดหวัง 

ประมาณนี้:
```
=== Distributed Hash Table Test ===

Test 1: PUT('apple', 'red') → random node (5000)
Response: {"status": "OK"}

Test 2: GET('apple') from another node (5001)
Response: {"status": "OK", "value": "red"}

Test 3: PUT/GET หลายค่าเพื่อดูการกระจาย
PUT(banana, yellow) → {"status": "OK"}
PUT(grape, purple) → {"status": "OK"}
PUT(melon, green) → {"status": "OK"}
PUT(water, blue) → {"status": "OK"}

อ่านกลับทั้งหมด (ยิงไปที่ node เดียว เพื่อทดสอบ routing):        
GET(banana) → {"status": "OK", "value": "yellow"}
GET(grape) → {"status": "OK", "value": "purple"}
GET(melon) → {"status": "OK", "value": "green"}
GET(water) → {"status": "OK", "value": "blue"}

=== Test Completed ===
```

ระบบจะ:

* กระจาย key ไปตาม node ที่ถูกต้อง
* รองรับ GET ที่ยิงไป node ไหนก็ได้
* forward ให้โดยอัตโนมัติ

## ประโยชน์ของการใช้งาน DHT

| ประโยชน์ | อธิบาย |
|-----------|--------|
| **กระจายข้อมูลอย่างมีประสิทธิภาพ** | DHT จัดเก็บข้อมูลในหลายโหนด ทำให้ไม่ต้องเก็บข้อมูลทั้งหมดในเครื่องเดียว ลดภาระการจัดเก็บและป้องกันจุดล้มเหลว (single point of failure) |
| **ค้นหาข้อมูลเร็วและตรงจุด** | DHT ใช้ key hashing เพื่อค้นหา node เจ้าของข้อมูลได้ทันที โดยไม่ต้องสแกนทุกโหนด (O(log N) ในหลายโครงสร้างเช่น Chord, Kademlia) |
| **ความทนทานต่อโหนดล่ม** | เมื่อโหนดหนึ่งล่ม ข้อมูลยังสามารถเข้าถึงจากโหนดอื่น ๆ ที่สำรองไว้ ทำให้ระบบยังทำงานได้ต่อเนื่อง |
| **ขยายตัวได้ง่าย (Scalable)** | สามารถเพิ่มจำนวนโหนดได้โดยไม่กระทบกับระบบทั้งหมด เพราะ DHT จะคำนวณตำแหน่ง key ใหม่อัตโนมัติ |
| **ไม่มีตัวกลาง (Decentralized)** | ไม่ต้องพึ่งพาเซิร์ฟเวอร์กลาง ลดค่าใช้จ่ายและป้องกันปัญหาคอขวดของระบบ |

---

## งานที่ใช้ DHT

| งาน/ระบบ | วิธีใช้ DHT |
|-----------|------------|
| **Peer-to-Peer (P2P) File Sharing** | เช่น BitTorrent ใช้ DHT เพื่อค้นหา peer ที่มีไฟล์โดยไม่ต้องพึ่ง tracker |
| **Blockchain / Cryptocurrency** | บางระบบใช้ DHT เพื่อจัดเก็บและค้นหาข้อมูลสัญญาอัจฉริยะ (smart contract) หรือ transaction ledger |
| **Distributed Storage Systems** | เช่น IPFS (InterPlanetary File System) ใช้ DHT เพื่อแมป hash ของไฟล์ไปยังโหนดที่เก็บไฟล์ |
| **Content Delivery Networks (CDN) แบบกระจาย** | ใช้ DHT จัดเก็บ metadata ของไฟล์/เนื้อหาเพื่อค้นหา node ที่เก็บไฟล์ใกล้ผู้ใช้งาน |
| **Decentralized Applications (DApps)** | แอปพลิเคชันแบบกระจาย ใช้ DHT จัดการข้อมูลผู้ใช้และทรัพยากรโดยไม่ต้องมีเซิร์ฟเวอร์กลาง |
