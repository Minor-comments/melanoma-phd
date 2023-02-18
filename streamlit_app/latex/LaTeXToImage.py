import argparse
import logging

import requests


class LaTeXToImage:
    LATEX_URL = "http://latex.codecogs.com/png.latex"

    def __init__(self):
        pass

    @staticmethod
    def convert(latex_code: str) -> bytes:
        response = requests.get(f"{LaTeXToImage.LATEX_URL}?\dpi{{300}} \huge {latex_code}")
        response.raise_for_status()
        return response.content

    @staticmethod
    def convert_to_file(latex_code: str, image_file: str) -> None:
        bytes = LaTeXToImage.convert(latex_code=latex_code)
        with open(image_file, "wb") as fd:
            fd.write(bytes)

    @staticmethod
    def convert_from_file(latex_file: str, image_file: str) -> None:
        with open(latex_file, "r") as fd:
            latex_code = fd.read()
            LaTeXToImage.convert_to_file(latex_code=latex_code, image_file=image_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LaTeX code to image convertor")
    parser.add_argument("latex_file", help="File with LaTeX code to convert to image")
    parser.add_argument("output_image", help="image file to store the result")
    args = parser.parse_args()

    latex_file = args.latex_file
    output_image = args.output_image
    LaTeXToImage.convert_from_file(latex_file=latex_file, image_file=output_image)
    logging.info(f"LaTeX code from '{latex_file}' converted to image '{output_image}'!")
