#!/bin/bash
#
#    pdf2png.sh
#
# convert pdf to png images
#
# MIT License
#
# Copyright (c) 2025 Alicia González Martínez
#
# usage:
#   $ bash pdf2png.sh ../data/pdf ../data/png
#
##################################################

if ! command -v pdftoppm &> /dev/null; then
	echo "Error: pdftoppm is not installed."
	exit 1
fi

if [ "$#" -ne 2 ]; then
	echo "Usage: $0 <input_path_with_pdfs> <output_path_to_save_pngs>"
	exit 1
fi

INPUT_PATH="$1"
OUTPUT_PATH="$2"

mkdir -p "$OUTPUT_PATH"

for pdf in "$INPUT_PATH"/*.pdf; do

	# skip if no pdf files are found
	[ -e "$pdf" ] || continue

	base_name=$(basename -- "$pdf" .pdf)
    
	echo "processing $pdf"
	pdftoppm -png "$pdf" "$OUTPUT_PATH/$base_name"

	echo "all images created!"

done

echo "conversion complete. PNGs saved in '$OUTPUT_PATH'."
