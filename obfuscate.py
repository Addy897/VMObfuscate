from compiler.translator_pe import Translator
import subprocess,os
from pprint import pprint
if __name__=="__main__":
    ext = ".exe" if os.name =="nt" else ""
    filename="payload"
    command=f'''gcc -O1 -ffunction-sections -fomit-frame-pointer -Wall  -o {filename}{ext} payloads/{filename}.c'''
    subprocess.run(command,shell=True)
    translator=Translator()
    translator.translate(f"{filename}{ext}")
    pprint(translator.translated_funcs)
    pprint(translator.funcs)
    #os.remove(f"{filename}{ext}")
    subprocess.run(f"g++ -std=c++20 interpreter/main.cpp interpreter/value.cpp -o main{ext} -ggdb",shell=True);

