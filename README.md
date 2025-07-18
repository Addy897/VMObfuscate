# Obfuscation VM Engine
This proof-of-concept of a Windows-only VM-based obfuscation engine for x86-64 binaries.

# System Architecture Diagram
The following diagram illustrates the end-to-end pipeline of this proof-of-concept:

![System Architecture](https://github.com/user-attachments/assets/25f7813b-51ab-478f-b199-770397bedc45)

## File Structure

```text
translator.py        # Translates native objdump output into VM byte-code
main.cpp             # VM interpreter entrypoint and execution logic
main.h               # VM definitions and instruction handlers
obfuscate.py         # Orchestrates compilation, translation, encryption, and execution
payload.vmo          # Example byte-code payload
```
## Features

* **Custom Byte-Code Format**: Defines a tailored instruction set optimized for obfuscation and simplified VM execution.
* **Automated Build Pipeline**: Single `obfuscate.py` script compiles source, translates to byte-code, encrypts, and executes.
* **XOR Encryption**: Lightweight encryption of byte-code payload to prevent casual inspection.
* **Fetch–Decode–Execute VM**: Implements a classic interpreter loop supporting control flow, arithmetic, and API stubs.
* **Windows API Stubs**: Basic support for `printf` and `MessageBoxA` calls within the VM environment.
* **Proof-of-Concept Clarity**: Minimal dependencies and clear separation of compiler, translator, and interpreter modules.


## Requirements

* **Windows MSYS2 (mingw64 shell)**
* **Mingw-w64 GCC** for compiling translator or interpreter
* **Python 3.8+** for running `translator.py` and `obfuscate.py`
* **GNU binutils** (`objdump`) for generating disassembly

---

> **Note:** This project is a **proof-of-concept** to demonstrate the VM-based obfuscation workflow. It is not intended for production use or real-world deployment.