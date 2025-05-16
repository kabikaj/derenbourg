#!/usr/bin/env python3
#
#    prepare_data.py
#
# prepare text data for RAG, convert json to plain txt files,
#  one per catalogue entry
#
# MIT License
#
# Copyright (c) 2025 Alicia González Martínez
#
# usage:
#   $ python3 prepare_data.py ../data/json ../data/text
#
############################################################

import re
import ujson as json
from pathlib import Path
from tqdm import tqdm
from argparse import ArgumentParser, FileType


PUNCT = r"[\.,;!\?\(\)]*"
ARABIC = r"[؀-ۿ]+"
FRENCH = r"[a-zA-ZÀ-ÿ'0-9]+"

ARABIC_PATTERN = fr'{ARABIC}(?:{PUNCT}\s+{ARABIC})*'
FRENCH_PATTERN = fr'{FRENCH}(?:{PUNCT}\s+{FRENCH})*'


def fix_order(text):    
    if (arabic_match := re.search(ARABIC_PATTERN, text)) and \
       (french_match := re.search(FRENCH_PATTERN, text)):

        arabic_text = arabic_match.group()
        french_text = french_match.group()

        swapped_text = text.replace(arabic_text, "{{ARABIC}}", 1)\
                           .replace(french_text, "{{FRENCH}}", 1)
        swapped_text = swapped_text.replace("{{ARABIC}}", french_text, 1)\
                                   .replace("{{FRENCH}}", arabic_text, 1)
        return swapped_text

    return text


def is_arabic(text):
    return bool(re.search('[\u0600-\u06FF]', text))


def swap(text):
    # This regex splits the text into words, considering punctuation and spaces
    words = re.findall(r'\S+|\s+|[^\w\s]', text)
    
    arabic_parts = []
    french_parts = []
    
    for word in words:
        if is_arabic(word):
            arabic_parts.append(word)
        else:
            french_parts.append(word)
    
    result = arabic_parts[::-1] + french_parts[::-1]
    
    return "".join(result)


def swap(text):
    def is_arabic(char):
        # Check if the character is within the Arabic Unicode range
        return '\u0600' <= char <= '\u06FF' or \
               '\u0750' <= char <= '\u077F' or \
               '\u08A0' <= char <= '\u08FF' or \
               '\uFB50' <= char <= '\uFDFF' or \
               '\uFE70' <= char <= '\uFEFF'

    def is_french(char):
        # Check if the character is a French letter or punctuation
        return char.isalpha() or char in "àâäçéèêëîïôöùûüÿæœÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸÆŒ',;:!?.-"

    chunks = []
    start = 0
    current_lang = None

    for i, char in enumerate(text):
        if is_arabic(char):
            if current_lang == 'french':
                # Save the current chunk and start a new Arabic chunk
                chunks.append(text[start:i])
                start = i
                current_lang = 'arabic'
            elif current_lang is None:
                # Start the first chunk as Arabic
                current_lang = 'arabic'
        elif is_french(char):
            if current_lang == 'arabic':
                # Save the current chunk and start a new French chunk
                chunks.append(text[start:i])
                start = i
                current_lang = 'french'
            elif current_lang is None:
                # Start the first chunk as French
                current_lang = 'french'
        else:
            # Spaces, numbers, symbols, etc., are part of the current chunk
            continue

    # Append the last chunk
    if start < len(text):
        chunks.append(text[start:])

    # Reverse the order of the chunks
    reversed_chunks = chunks[::-1]

    # Join the reversed chunks into a single string
    reversed_text = ' '.join(reversed_chunks)

    return reversed_text


NORM_MAPPING = {
    "Sibonyéh": "Sîbouyéh",
    "Sîboûtyéh": "Sîbouyéh",
    "l'Eseurial": "l'Escorial",
    "About": "Aboû",
}

NORM_REGEX = re.compile("|".join(map(re.escape, NORM_MAPPING)))


def norm(text: str) -> str:
    text = "".join([swap(t) for t in text.splitlines(True)])
    # remove header
    text = re.sub(r"GRAMMAIRE\.\n(?:00\n)?\d+", "", text)
    text = re.sub(r"\d+\nLES MANUSCRITS ARABES DE L'ESCURIAL.?\n?", " ", text)

    # join separated words
    text = text.replace("-\n", "")

    # some normalisations
    text = NORM_REGEX.sub(lambda m: NORM_MAPPING[m.group(0)], text)

    # deal with line breaks and spaces
    text = text.replace(".\n", ".LINEBREAK")
    text = re.sub(r"\s+", " ", text)
    text = text.replace("LINEBREAK", "\n\n")
    text = text.replace("\n ", "\n")
    text = text.replace("ap.\n\nJ.-Chr.)", "ap. J.-Chr.)")
    
    return text


if __name__ == "__main__":

    parser = ArgumentParser(
        description="convert json to plain organised txt files")
    parser.add_argument("input", help="path with json files")
    parser.add_argument("output", help="path to save txt files")
    args = parser.parse_args()

    json_path = Path(args.input)
    text_path = Path(args.output)

    text_path.mkdir(parents=True, exist_ok=True)

    json_fpaths = sorted(
        Path(json_path).rglob("*.json"),
        key=lambda x: list(map(int, x.stem.partition("_")[2].split("-")))
    )

    collected = []

    for json_file in tqdm(json_fpaths, desc="read input data"):

        print(f"Input json read from file {json_file}")

        with open(json_file) as fp:
            data = json.load(fp)

        if not data:
            continue

        collected.append(data[0]["text"])

    complete = "\n".join(collected)

    i = 0
    last_num = None
    skip_first_1, skip_first_2 = True, True
    sections, aux = [], []

    for line in complete.splitlines():
        if m := re.match(r"^(\d+)\.$", line):
            num = int(m.group(1))
            if num == 1 and skip_first_1:
                skip_first_1 = False
                continue
            if num == 2 and skip_first_2:
                skip_first_2 = False
                continue
            last_num = num
            if num == 1:
                aux = []
            elif aux and num == last_num:
                if i:
                    sections.append((i, "\n".join(aux)))
                i += 1
                aux = []
            else:
                aux.append(line)
        else:
            aux.append(line)

    
    for i, text in tqdm(sections, desc="Write processed data"):

        id_ = f"{i:04}"
        text = norm(text)

        outfile = text_path / f"{id_}.txt"
        with open(outfile, "w") as outfp:
            outfp.write(text)

    print(f"Output files saved in {text_path}")

