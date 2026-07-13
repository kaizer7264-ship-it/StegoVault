# 🔒 StegoVault

**StegoVault** is a modern cross-platform desktop application for securely hiding sensitive information inside images using **Least Significant Bit (LSB) steganography** with optional **AES encryption**.

Designed with a modular architecture and an intuitive graphical interface, StegoVault allows users to hide both text messages and files inside PNG images while keeping the data protected from unauthorized access.

---

## ✨ Features

* Hide secret text inside PNG images
* Extract hidden text from images
* Hide files inside images
* Extract embedded files
* Optional AES encryption for additional security
* Modern PySide6 graphical interface
* Capacity checking before embedding
* Cross-platform Python implementation
* Modular and maintainable architecture

---

## 📸 Screenshots

Screenshots are available in the `screenshots/` directory.

---

## 📁 Project Structure

```
StegoVault/
├── assets/
├── docs/
├── screenshots/
├── src/
│   └── stegovault/
│       ├── core/
│       ├── crypto/
│       ├── gui/
│       ├── services/
│       └── main.py
├── tests/
├── requirements.txt
└── README.md
```

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/kaizer7264-ship-it/StegoVault.git
cd StegoVault
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```cmd
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python src/stegovault/main.py
```

---
## 📖 Usage

### Hide Text

1. Launch StegoVault.
2. Select a PNG image.
3. Enter your secret message.
4. (Optional) Enable AES encryption and provide a password.
5. Save the generated image.

### Extract Text

1. Open an encoded PNG image.
2. Enter the password if encryption was used.
3. Extract the hidden message.

### Hide Files

1. Select a carrier PNG image.
2. Choose the file you want to embed.
3. Enable encryption if desired.
4. Save the output image.

### Extract Files

1. Open the encoded image.
2. Provide the password if required.
3. Extract and save the embedded file.

## 🔐 Technologies Used

* Python
* PySide6
* Pillow
* Cryptography (AES)
* LSB Steganography

---

## 📋 Requirements

* Python 3.12+
* PySide6
* Pillow
* cryptography

---

## 🛡️ Security Notice

StegoVault is intended for educational purposes and legitimate privacy use. Users are responsible for complying with applicable laws and regulations when using this software.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Muhammad Sami Butt**

GitHub: https://github.com/kaizer7264-ship-it

LinkedIn: https://www.linkedin.com/in/sami7264/
