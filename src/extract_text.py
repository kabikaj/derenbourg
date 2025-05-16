#!/usr/bin/env python3
#
#    extract_text.py
#
# extract text from Arabic catalogues
#
# MIT License
#
# Copyright (c) 2025 Alicia González Martínez
#
# setup:
#   Install gcloud, authenticate and setup project:
#     $ pip install google-cloud-vision
#     $ gcloud init
#     $ gcloud auth application-default login 
#   Create a project called ocr-arabic-catalogue in
#     https://console.cloud.google.com and enable Cloud Vision API and billing
#
# usage:
#   $ python3 extract_text.py ../data/png ../data/json
#   # 1162 images 24:18 min
#
##############################################################################

import ujson as json
from pathlib import Path
from tqdm import tqdm
from google.cloud import vision
from argparse import ArgumentParser, FileType


def detect_text(
    client: vision.ImageAnnotatorClient,
    input_path: Path,
    output_path: Path
    ) -> None:
    """
    Detects text in file and saves text and coordinates in json output

    """
    print(f"Processing file {input_path}")

    with open(input_path, "rb") as img_fp:
        content = img_fp.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(
        image=image,
        image_context=vision.ImageContext(
            language_hints=["fr", "ar"]
        ),
    )

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )

    texts = response.text_annotations

    doc = [
        {
        "text": t.description,
        "box": [[v.x, v.y] for v in t.bounding_poly.vertices]
            # e.g.:
            # text.bounding_poly.vertices = [
            #     Vertex(x=10, y=10),   # Top-left
            #     Vertex(x=100, y=10),  # Top-right
            #     Vertex(x=100, y=50),  # Bottom-right
            #     Vertex(x=10, y=50)    # Bottom-left
            # ]
        } for t in texts
    ]

    with open(output_path, "w") as outfp:
        json.dump(doc, outfp)

    print(f"Detected text saved in file {output_path}")


if __name__ == "__main__":

    parser = ArgumentParser(
        description="extract text from Arabic catalogues using Google Cloud Vision")
    parser.add_argument("input", help="path with png folder")
    parser.add_argument("output", help="path to save output json files")
    parser.add_argument("--no_skip", action="store_true",
        help="process file even if output file is already created")
    args = parser.parse_args()

    png_path = Path(args.input)
    json_path = Path(args.output)

    json_path.mkdir(parents=True, exist_ok=True)

    client = vision.ImageAnnotatorClient()
    
    for png_file in tqdm(list(Path(png_path).rglob("*.png"))):
                
        json_file = json_path / f"{png_file.stem}.json"

        # skip if output file already exists
        if json_file.exists() and not args.no_skip:
            print(f"skipping already processed file {png_file}")
            continue

        detect_text(client, png_file, json_file)
