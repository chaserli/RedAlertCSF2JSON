#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Author : Trsdy

https://modenc.renegadeprojects.com/CSF_File_Format
'''

from io import TextIOWrapper
import struct
import json
import argparse


def __make_header(csf: TextIOWrapper, num_labels: int, num_strings: int, locale=0):
    header_info = {
        "FSC": b" FSC",
        "CSF Version": 3,
        "NumLabels": num_labels,
        "NumStrings": num_strings,
        "unused": 0,
        "Language": locale
    }
    csf.write(struct.pack("<4sLLLLL"
                          , header_info["FSC"]
                          , header_info["CSF Version"]
                          , header_info["NumLabels"]
                          , header_info["NumStrings"]
                          , header_info["unused"]
                          , header_info["Language"]
                          ))
    return csf


def __string2bytes(content: str) -> bytes:
    raw_bytes = bytearray(content.encode("UTF-16LE"))
    for idx in range(len(raw_bytes)-1, -1, -1):
        raw_bytes[idx] = raw_bytes[idx] ^ 0xff
    return bytes(raw_bytes)


def __main_coversion(csf_file: TextIOWrapper, name_str_map: dict):
    csf_file = __make_header(csf_file, len(name_str_map), len(name_str_map))
    for label, ui_content in name_str_map.items():
        csf_file.write(struct.pack("<4sL", b" LBL", 1))
        uiname_bytes = label.encode('utf-8')
        csf_file.write(struct.pack(f"<L{len(uiname_bytes)}s4s", len(
            uiname_bytes), uiname_bytes, b' RTS'))
        value = __string2bytes(ui_content)
        value_len = len(value)//2
        csf_file.write(struct.pack("<L", value_len))
        csf_file.write(struct.pack(f"<{value_len*2}s", value))


def __parse_filenames():
    parser = argparse.ArgumentParser(
        description="Convert a JSON file to a CSF file")
    parser.add_argument('-i', '--json', type=str, required=True, help="input JSON file")
    parser.add_argument('-o', '--csf', type=str, required=True, help="output CSF file")
    args = parser.parse_args()
    return args.json, args.csf


def json2csf(infile: str, outfile: str):
    with open(infile, mode="r", encoding="GB2312") as jsn_file:
        name_str_dict = json.load(jsn_file)
        with open(outfile, mode="wb") as CSF_File:
            __main_coversion(CSF_File, name_str_dict)


if __name__ == "__main__":
    jsn_filename, csf_filename = __parse_filenames()
    json2csf(jsn_filename, csf_filename)
