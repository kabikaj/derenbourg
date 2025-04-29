#!/usr/bin/env python3
#
#    transform.py
#
# use LLM to convert unstructured texts into strcutured json objects
#
# usage:
#   $ python3 transform.py ../data/text_corrected ../data/json_modelled
#     --service openai --ini 1 --end 80
#
#######################################################################

import os
import re
import configparser
import ujson as json
from tqdm import tqdm
from pathlib import Path
from pprint import pprint
from dotenv import dotenv_values
from openai import OpenAI, OpenAIError
from argparse import ArgumentParser


BASEDIR = Path(os.path.abspath(os.path.dirname(__file__)))

config = configparser.ConfigParser()
config.read("config.ini")

SYSTEM_PROMPT = config.get("PROMPT", "SYSTEM")
USER_PROMPT = config.get("PROMPT", "USER")

TEMPERATURE = 0.2
TOP_P = 0.3


if __name__ == "__main__":
    parser = ArgumentParser(description="transform text to structured json objects")
    parser.add_argument("input", help="path with txt files")
    parser.add_argument("output", help="path to store json files")
    parser.add_argument(
        "--ini", type=int, default=0, help="initial mss record to process"
    )
    parser.add_argument("--end", type=int, help="final mss record to process")
    parser.add_argument(
        "--service",
        choices=["openai", "deepseek"],
        required=True,
        help="path to save json outputs",
    )
    parser.add_argument("--temp", type=float, help="model temperature")
    parser.add_argument("--top_p", type=float, help="model top_p")
    parser.add_argument("--debug", action="store_true", help="debug mode")
    args = parser.parse_args()

    if args.service == "openai":
        client = OpenAI(
            api_key=dotenv_values(BASEDIR / ".openai.env")["OPENAI_API_KEY"]
        )
        model = "gpt-4o-mini"

    else:
        client = OpenAI(
            api_key=dotenv_values(BASEDIR / ".deepseek.env")["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com",
        )

        model = "deepseek-chat"

    text_path = Path(args.input)
    json_path = Path(args.output)

    text_fpaths = list(Path(text_path).rglob("*.txt"))

    if not args.end:
        args.end = len(text_fpaths)

    text_fpaths = list(
        filter(lambda f: args.ini <= int(f.name.split(".")[0]) <= args.end, text_fpaths)
    )

    for fpath in tqdm(text_fpaths, desc="process files"):
        with open(fpath) as fp:
            text = fp.read().strip()

        text = re.sub(r"\n+", "\n", text)

        user_prompt = f"{USER_PROMPT}\n\n\n\nInput:\n\n{text}\n\n\nJson Output:\n\n"

        if args.debug:
            print(f"processing file {fpath}")
            print(f"\nprompt:\n\n{user_prompt}")

        try:
            completion = client.chat.completions.create(
                model=model,
                temperature=args.temp or TEMPERATURE,
                top_p=args.top_p or TOP_P,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )

            output = json.loads(completion.choices[0].message.content)

            if args.debug:
                print(
                    f"\noutput:\n\n{json.dumps(output, ensure_ascii=False, indent=5)}"
                )

        except OpenAIError:
            print("Error reading output. Received completion:\n")
            pprint(completion)

        out_fpath = json_path / f"{fpath.stem}.json"

        with open(out_fpath, "w") as outfp:
            json.dump(output, outfp, ensure_ascii=False, indent=4)

        if args.debug:
            print(f"output saved in {out_fpath}")
