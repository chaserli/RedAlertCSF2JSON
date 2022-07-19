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

def make_header(csf:TextIOWrapper,num_labels:int,num_strings:int,locale=0):
    header_info={
        "FSC":b" FSC",
        "CSF Version":3,
        "NumLabels":num_labels,
        "NumStrings":num_strings,
        "unused":0,
        "Language":locale
    }
    csf.write(struct.pack("<4sLLLLL"
    ,header_info["FSC"]
    ,header_info["CSF Version"]
    ,header_info["NumLabels"]
    ,header_info["NumStrings"]
    ,header_info["unused"]
    ,header_info["Language"]
    ))
    return csf


def string2bytes(content:str)->bytes:
    raw_bytes=bytearray(content.encode("UTF-16LE"))
    for idx in range(len(raw_bytes)-1,-1,-1):
        raw_bytes[idx]=raw_bytes[idx]^ 0xff
    return bytes(raw_bytes)

def main_coversion(csf_file:TextIOWrapper,name_str_map:dict):
    csf_file=make_header(csf_file,len(name_str_map),len(name_str_map))
    for label,ui_content in name_str_map.items():
        csf_file.write(struct.pack("<4sL",b" LBL",1))
        uiname_bytes=label.encode('utf-8')
        csf_file.write(struct.pack(f"<L{len(uiname_bytes)}s4s",len(uiname_bytes),uiname_bytes,b' RTS'))
        value=string2bytes(ui_content)
        value_len=len(value)//2
        csf_file.write(struct.pack("<L",value_len))
        csf_file.write(struct.pack(f"<{value_len*2}s",value))

def parse_filenames(argv:str):
    input_json:str = 'test.json'
    output_csf:str = 'test.csf'

    try:
        opts, _ = getopt.getopt(argv,"hi:o:",["json=","csf="])
    except getopt.GetoptError:
        print('json2csf.py --json <input json file> --csf <output csf file>')
        sys.exit(114514)
    for opt, arg in opts:
        if opt == '-h':
            print('json2csf.py --json <input json file> --csf <output csf file>')
            sys.exit()
        elif opt in ("-i", "--json"):
            input_json = arg
        elif opt in ("-o", "--csf"):
            output_csf = arg
    return input_json,output_csf

if __name__ == "__main__":
    jsn_filename,csf_filename=parse_filenames(sys.argv[1:])
    with open(jsn_filename,mode="r", encoding="GB2312") as jsn_file:
        name_str_map=json.load(jsn_file)

        with open(csf_filename,mode="wb") as csf_file:
            main_coversion(csf_file,name_str_map)