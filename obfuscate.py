
import subprocess,os
if os.name =="nt":
    from compiler.translator_pe import Translator
else:
    from compiler.translator_elf import Translator
from pprint import pprint
if __name__=="__main__":
    ext = ".exe" if os.name =="nt" else ""
    filename="payload"
    command=f'''gcc -O1 -ffunction-sections -fomit-frame-pointer -Wall  -o {filename}{ext} payloads/{filename}.c'''
    subprocess.run(command,shell=True)
    translator=Translator()
    translator.translate(f"{filename}{ext}")
    os.remove(f"{filename}{ext}")
    subprocess.run(f"g++ -std=c++20 interpreter/main.cpp interpreter/value.cpp -o main{ext} -ggdb",shell=True);

