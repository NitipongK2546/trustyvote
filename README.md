# TrustyVote

## Member

1. 6510615070 ณภัทร วงศ์แก้ว
1. 6510615138 นคินทร รุ่งเรือง
1. 6510615153 นิติพงษ์ ขัดสีทะลี
1. 6510615237 พลวิชญ์ วงษ์สุนทร

---
## IMPORTANT, READ THIS

This is the branch that only create 1 server ***and is OLD***

For the newer branch with the following feature

- Deploying 2 servers
    1. Server for Poll Creation, Poll Score Count, and input voting code.
    1. Server for actually doing the voting.
- Vote only get counted when Poll Creator click **Count Vote**
- Bug fixes 

Use the two_server branch.

---
## How to use

1. git clone https://github.com/NitipongK2546/trustyvote \[your-dir]

1. cd [your-dir]

    - If you wish to use two_server version, run:
    ```
    git switch two-server
    ```

1. create .env file based on the .env.example files

1. run 
    ```
    docker compose up -d --build
    ```

---

Docker should create MariaDB, Nginx, and 1-2 Django Containers.

The server you will be using is on **localhost:9000**
