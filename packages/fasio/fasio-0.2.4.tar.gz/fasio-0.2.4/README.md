<img src="fasio.webp" alt="My Project Logo" style="width: 150px; height: auto; border: 20px solid #000; border-radius: 50%;"/>


## fasio  
A Truly Asynchronous Library for Coroutine Scheduling

---

## Overview

**fasio** is an advanced asynchronous I/O library designed to simplify the development of high-performance network applications. It leverages the power of coroutines to provide a truly asynchronous programming model, allowing you to manage tasks efficiently without blocking operations. With fasio, you can create responsive applications that scale effortlessly.

### Key Features

- **Truly Asynchronous**: Supports async-await syntax for writing non-blocking code, allowing for efficient I/O operations.
- **Robust Event Loop**: A fast and reliable event loop for managing asynchronous tasks and socket operations.
- **Cross-Thread Notifications**: Built-in mechanisms for receiving notifications from other threads and processes.
- **Easy Socket Handling**: Simplifies asynchronous socket programming, making it easy to build servers and clients.
- **Modular Design**: Designed to integrate seamlessly into existing applications, enhancing functionality without major refactoring.

---

## Installation

To install fasio, use pip:

```bash
pip install fasio
```

---

## Usage

fasio is designed for ease of use. Below is a simple example of how to create a basic TCP echo server using fasio's features.

### Example: Asynchronous TCP Echo Server

```python
from fasio import start, spawn, socket

async def handle_client(client):
    while True:
        data = await client.recv(100)

        if not data:
            break

        await client.send(data)

async def main():
    serverfd = socket(socket.AF_INET, socket.SOCK_STREAM)
    serverfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
    serverfd.bind(('localhost', 8080))
    serverfd.listen(socket.SOMAXCONN)

    while True:
        client, addr = await serverfd.accept()

        spawn(handle_client(client))

start(main())
```

### Explanation

In this example, we create a TCP server that listens on `localhost` at port `8080`. When a client connects, a new coroutine is spawned to handle the client’s requests. The server echoes back any data received, demonstrating fasio's capabilities for handling asynchronous socket operations.

---

## Contributing

Contributions to fasio are welcome! If you’d like to help improve the library, please fork the repository and submit a pull request. Feel free to report issues or request features through the issue tracker.

### How to Contribute

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with clear messages.
4. Push your branch and submit a pull request.

---

## License

fasio is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Contact

For any questions or feedback, please reach out via [iadityanath8@gmail.com](mailto:your.email@example.com).

---

With fasio, harness the power of asynchronous programming to create efficient, high-performance applications. Start building today and explore the possibilities!
