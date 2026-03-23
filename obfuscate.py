from compiler.translator_elf import Translator
import subprocess,os
from pprint import pprint
if __name__=="__main__":
    filename="payload"
    command=f'''gcc -O1 -march=x86-64  -fomit-frame-pointer -Wall  -o {filename} payloads/{filename}.c'''
    subprocess.run(command,shell=True)
    translator=Translator()
    translator.translate(f"{filename}")
    pprint(translator.translated_funcs['main'])
    os.remove(f"{filename}")
    subprocess.run("g++ -std=c++20 interpreter/main.cpp interpreter/value.cpp -o main -ggdb",shell=True);

