### Scalable web cache using consistent hashing

We have implemented a miniature version of consistent hashing as well as simple hashing that are used to cache the requests between the Server and Client. Later is implemented to make a comparison between the two schemes. Also for simplicity we have assumed that all clients have the same view of the system, i.e. we have assumed synchronous information propagation through the internet. The Code has 4 major components:
 - Client
 - Server
 - Hashing Scheme
 - Cache server

Check report for further insights.

**Usage**: Open two seperate terminals and run client(s) and server
 ```
python3 Server.py
python3 Client.py 127.0.0.1 8080
```
