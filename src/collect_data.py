#!/usr/bin/env python3
#
#    collect_data.py
#
# collect all modelled data in one single json file for web app
#
# MIT License
#
# Copyright (c) 2025 Alicia González Martínez
#
# usage:
#   $ python3 collect_data.py ../data/text_corrected ../data/json_modelled ../data/app_data.json
#
################################################################################################

import os
import re
import sys
import configparser
import ujson as json
from tqdm import tqdm
from pathlib import Path
from pprint import pprint
from argparse import ArgumentParser, FileType


NORM_MAPPING = {
    "Magrébino": "Magrébine",
    "Magrobine": "Magrébine",
    "Magréline": "Magrébine"
}


NORM_REGEX = re.compile("|".join(
    list(
        filter(
            re.escape,
            sorted(NORM_MAPPING, key=len, reverse=True)
        )
    )))

def norm(text: str) -> str:
    text = NORM_REGEX.sub(lambda m: NORM_MAPPING[m.group(0)], text)
    return text


if __name__ == "__main__":

    parser = ArgumentParser(
        description="collect all modelled data in one single json file for web app")
    parser.add_argument("input_text",
        help="path with text files containing catalogue records")
    parser.add_argument("input_json",
        help="path with json files")
    parser.add_argument("output",
        type=FileType("w"),
        help="ouput file")
    args = parser.parse_args()

    text_fpaths = Path(args.input_text).rglob("*.txt")

    records = {}
    for fpath in text_fpaths:
        with open(fpath) as fp:
            text = re.sub(r"\n+", "\n", fp.read())
        records[int(fpath.stem)] = text

    fpaths = ((int(p.stem), p) for p in Path(args.input_json).rglob("*.json"))

    collected = []

    for id_, fpath in sorted(fpaths, key=lambda x: x[0]):

        text = records[id_]
        
        with open(fpath) as fp:
            data = json.load(fp)

        for obj in data["catalogue_entry"]:
            for k, v in obj.items():
                if isinstance(v, str):
                    obj[k] = norm(v)
            obj["text"] = norm(text)

            collected.append(obj)
    
    json.dump(collected, args.output, ensure_ascii=False, indent=4)
