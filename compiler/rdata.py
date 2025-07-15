from ast import Raise
import re
import subprocess
from typing import Any


class RDATA:
    def __init__(self,filename) -> None:
        self.rdata_array={}
        self.rdata_pat=re.compile(r"\s*(?P<addr>[0-9A-Fa-f]+)\s(?P<data>([0-9A-Fa-f]{8}\s){4})")
        raw_rdata=subprocess.check_output(["objdump","-s","-j",".rdata",filename]).decode()
        current_base=None
        current_data=""
        for line in raw_rdata.splitlines():
            match=self.rdata_pat.match(line)
            if(match):
                start_addr=match.group("addr")
                raw_bytes=match.group("data").replace(" ","")
                if(current_base is None):
                    current_base=int(start_addr,16)

                for i in range(0,len(raw_bytes),2):
                    if(raw_bytes[i:i+2]=="00"):
                        if(current_data!=""):
                            self.rdata_array[hex(current_base)]=current_data
                        current_data=""
                        current_base=int(start_addr,16)+(i+2)//2
                        continue
                    current_data+=raw_bytes[i:i+2]

    def get(self,key:str,fail:Any=None) -> str|Any:
        return self.rdata_array.get(key,fail)
if __name__ =="__main__":
    rdata=RDATA("test.exe")
    print(rdata.rdata_array)
