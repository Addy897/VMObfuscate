from compiler.translator import Translator
import subprocess,os
if __name__=="__main__":
    filename="payload"
    command=f'''gcc -O1 -march=x86-64 -ffunction-sections -fomit-frame-pointer -Wall "-Wl,--gc-sections" -o {filename}.exe payload\\{filename}.cpp -lkernel32 -luser32'''
    subprocess.run(command,shell=True)
    translator=Translator()
    translator.transalte(f"{filename}.exe")
    os.remove(f"{filename}.exe")
    subprocess.run("g++ interpreter\\main.cpp -o main.exe",shell=True);

