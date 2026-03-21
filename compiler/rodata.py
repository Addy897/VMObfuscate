from ast import Raise
import re
import subprocess
from typing import Any


class RODATA:
    def __init__(self,filename) -> None:
        self.rodata_array={}
        self.rodata_pat=re.compile(r"\s*(?P<addr>[0-9A-Fa-f]+)\s(?P<data>([0-9A-Fa-f]{8}\s)*)")
        raw_rodata=subprocess.check_output(["objdump","-s","-j",".rodata",filename]).decode()
        current_base=None
        current_data=""
        for line in raw_rodata.splitlines():
            match=self.rodata_pat.match(line)
            if(match):
                start_addr=match.group("addr")
                raw_bytes=match.group("data").replace(" ","")
                if(current_base is None):
                    current_base=int(start_addr,16)

                for i in range(0,len(raw_bytes),2):
                    if(raw_bytes[i:i+2]=="00"):
                        if(current_data!=""):
                            self.rodata_array[hex(current_base)]=current_data
                        current_data=""
                        current_base=int(start_addr,16)+(i+2)//2
                        continue
                    current_data+=raw_bytes[i:i+2]

    def get(self,key:str,fail:Any=None) -> str|Any:
        return self.rodata_array.get(key,fail)
if __name__ =="__main__":
    rodata=RODATA("../payload/payload")
    print(rodata.rodata_array)
