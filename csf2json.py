#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Author : Trsdy

https://modenc.renegadeprojects.com/CSF_File_Format
'''

from io import TextIOWrapper
import struct
import json
import sys
import getopt

Locales = {
    0:"EN-US",
    1:"EN-UK",
    2:"DE",
    3:"FR",
    4:"ES",
    5:"IT",
    6:"JP",
    7:"Jabberwockie",
    8:"KR",
    9:"CN",
    114514:"Unknown"
}


def check_header(header:tuple)->int:
    print("Checking CSF file format:")
    if len(header)!=6:
        raise IOError("Not a valid CSF file!")
    fsc:bytes=header[0]
    if(fsc!=b" FSC"):
        raise AssertionError("This is not a valid CSF file!")
    csf_version:int=header[1]
    print(f"\tCSF Version:{csf_version}")
    num_labels:int=header[2]
    num_strings:int=header[3]
    if(num_labels!=num_strings):
        raise TypeError("label count and string count are unequal")
    unused:int=header[4]
    lang_id:int=header[5]
    if(lang_id<10):
        print(f"\tCSF language is {Locales[lang_id]}")
    print("-"*30)
    return num_labels

def bytes2string(content:bytes)->str:
    str_invert=bytearray(content)
    for idx in range(len(str_invert)-1,-1,-1):
        str_invert[idx]=str_invert[idx]^ 0xff
    return str_invert.decode("UTF-16LE")


def read_csf(csf_file:TextIOWrapper)->dict:
    num_label=check_header(struct.unpack("<4sLLLLL",csf_file.read(0x18)))
    name_str_map=dict()
    for _ in range(num_label):
        lbl, one, uiname_length = struct.unpack("<4sLL", csf_file.read(0xc))
        assert lbl==b" LBL"
        assert one==1
        UIName,rts_id = struct.unpack(f"<{uiname_length}s4s", csf_file.read(uiname_length+0x4))
        rts_len:int=struct.unpack("<L",csf_file.read(0x4))[0]*2
        content_raw:bytes=struct.unpack(f"<{rts_len}s",csf_file.read(rts_len))[0]

        if(rts_id!=b" RTS"):
            extra_len:int=struct.unpack("<L",csf_file.read(0x4))[0]
            extra_raw=struct.unpack(f"<{extra_len}s",csf_file.read(extra_len))
            raise Warning(f"Extra string {bytes2string(extra_raw)} is omitted")

        name_str_map[UIName.decode("utf-8")]=bytes2string(content_raw)
    return name_str_map

def parse_filenames(argv:str):
    input_csf:str = 'stringtable15.csf'
    output_json:str = 'testa.json'

    try:
        opts, _ = getopt.getopt(argv,"hi:o:",["json=","csf="])
    except getopt.GetoptError:
        print('csf2json.py --csf <input json file> --json <output csf file>')
        sys.exit(1919810)
    for opt, arg in opts:
        if opt == '-h':
            print('csf2json.py --csf <input json file> --json <output csf file>')
            sys.exit()
        elif opt in ("-i", "--csf"):
            input_csf = arg
        elif opt in ("-o", "--json"):
            output_json = arg
    return input_csf,output_json

if __name__ == "__main__":
    csf_filename,jsn_filename=parse_filenames(sys.argv[1:])

    with open(csf_filename,mode="rb") as csf_file:
        uiname_content_dict=read_csf(csf_file)

        with open(jsn_filename, mode="w") as jsn_file:
            json.dump(uiname_content_dict,jsn_file,indent=4,ensure_ascii=False)
