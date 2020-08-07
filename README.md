### Scalable web cache using consistent hashing

This was a team project implemented by me, [Gaurav Batra](https://github.com/batra98), [Puru Gupta](https://github.com/purugupta99) as part of the Distributed Systems course.

We have implemented a miniature version of consistent hashing as well as simple hashing that are used to cache the requests between the Server and Client. Later is implemented to make a comparison between the two schemes. Also for simplicity we have assumed that all clients have the same view of the system, i.e. we have assumed synchronous information propagation through the internet. The Code has 4 major components:
 - Client
 - Server
 - Hashing Scheme
 - Cache server

Check report for further insights. [Video explanation](https://drive.google.com/drive/folders/1nzpbPmc9qENC3JGQu8dzBaOhfRATbrtc?usp=sharing) of the project.

## :running: Usage
* Open two seperate terminals and run client(s) and server
```bash
python3 Server.py
python3 Client.py 127.0.0.1 8080
```

[![asciicast](https://asciinema.org/a/Z8QBSvBvCsQyYmUqYImB3YDoA.svg)](https://asciinema.org/a/Z8QBSvBvCsQyYmUqYImB3YDoA)

## Components
- **Server**:
	- This is the place where data and cache servers are stored.
	- **Server.py** and **Server_2.py** contains servers with consitant hashing and normal hashing schemes respectively.
	- The server can handle requests from several clients and uses TCP/IP protocol to estaiblish connection with the clients.
	- LRU (least recently used) Caches have been implemented in the server.
- **Client**:
	- Client is the program that interacts with the server and request/creates data.
	- The Client can perform the following functions:
		* Add Cache server - **addnode [server:ip]** (Consistent Hashing), **addnode** (Normal Hashing).
		* Add Cache server - **rmnode [key]**.
		* Add/remove data - **add [key] [value]**
		* Get data - **get [key]**.
		* Check cache sever state - **stats**
		* Check performance of the system - **per**
		* Add multiple nodes and datapoints to test the cache - **test [number of nodes] [number of data points]**.
		* Reset the server - **clean [replicas] [cache size]** (Consistent Hashing), **clean** (Normal Hashing).

________

Feel free to Contribute :heart:



