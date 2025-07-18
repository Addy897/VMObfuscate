# Obfuscation VM Engine
This proof-of-concept of a Windows-only VM-based obfuscation engine for x86-64 binaries.

# System Architecture Diagram
The following diagram illustrates the end-to-end pipeline of this proof-of-concept:

![System Architecture](Screenshot 2025-07-19 002246.png)

## File Structure

```text
translator.py        # Translates native objdump output into VM byte-code
main.cpp             # VM interpreter entrypoint and execution logic
main.h               # VM definitions and instruction handlers
obfuscate.py         # Orchestrates compilation, translation, encryption, and execution
payload.vmo          # Example byte-code payload
```

## Requirements

* **Windows MSYS2 (mingw64 shell)**
* **Mingw-w64 GCC** for compiling translator or interpreter
* **Python 3.8+** for running `translator.py` and `obfuscate.py`
* **GNU binutils** (`objdump`) for generating disassembly

---

> **Note:** This project is a **proof-of-concept** to demonstrate the VM-based obfuscation workflow. It is not intended for production use or real-world deployment.
