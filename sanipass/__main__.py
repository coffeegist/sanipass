import typer
import string
# import matplotlib.pyplot as plt
# import keras_ocr
import pytesseract
from pytesseract import Output
from PIL import Image
from PIL import ImageDraw
from typing_extensions import Annotated
from pathlib import Path
from sanipass.logger import init_logger, logger, console
from sanipass import __version__

app = typer.Typer(
    add_completion=False,
    rich_markup_mode='rich',
    context_settings={'help_option_names': ['-h', '--help']},
    pretty_exceptions_show_locals=False
)

def blacklisted_characters():
    return '\'"`;:/.,\\|[]{}()'

def whitelisted_characters():
    standard_set = string.ascii_letters + string.digits # + string.punctuation
    for character in blacklisted_characters():
        standard_set = standard_set.replace(character, '')

    return standard_set

def sanitize_screenshot(
        image_path, sensitive_data_file:str, confidence_threshold:int=0
    ):

    sanitized = False

    # Load the image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Initialize sensitive data
    sensitive_data = []
    with open(sensitive_data_file) as f:
        sensitive_data = f.read().splitlines()
    logger.debug(sensitive_data)

    # Perform OCR on the image
    config = f'--user-words {sensitive_data_file} --user-patterns {sensitive_data_file} --psm 6 -c preserve_interword_spaces=1'
    config += f' tessedit_char_whitelist=\'{whitelisted_characters()}\''
    logger.debug(f'Config: {config}')
    ocr_data = pytesseract.image_to_data(image, output_type=Output.DICT, config=config)
    logger.debug(ocr_data)

    # Iterate through the OCR text and locate the hash patterns
    n_boxes = len(ocr_data['text'])
    for i in range(n_boxes):
        if int(ocr_data['conf'][i]) > confidence_threshold:
            ocr_text = ocr_data['text'][i]
            for sensitive_word in sensitive_data:
                if sensitive_word in ocr_text:
                    sanitized = True
                    logger.info(f'Found sensitive data: {ocr_text}')

                    if sensitive_word == ocr_text:
                        draw.rectangle([(ocr_data['left'][i], ocr_data['top'][i]), (ocr_data['left'][i] + ocr_data['width'][i], ocr_data['top'][i] + ocr_data['height'][i])], outline="red", fill="black")
                    else:
                        # Get the coordinates of the word
                        left = ocr_data['left'][i]
                        top = ocr_data['top'][i]
                        height = ocr_data['height'][i]

                        # Calculate the bounding box of the sensitive word
                        text_start = ocr_text.index(sensitive_word)
                        text_end = text_start + len(sensitive_word)

                        word_left = left
                        character_width = ocr_data['width'][i] / len(ocr_text)
                        for j in range(text_start):
                            word_left += character_width

                        word_top = top
                        word_width = character_width * len(sensitive_word)
                        word_height = height

                        # Draw a rectangle around the word
                        draw.rectangle([(word_left, word_top), (word_left + word_width, word_top + word_height)], outline="red", fill="black")



    if sanitized:
        # Calculate new image name
        p = Path(image_path)
        new_name = str(p.absolute()).replace(p.suffix, f'-sanitized{p.suffix}')
        logger.info(f'Saving sanitized image to: {new_name}')
        # Save the modified image
        image.save(new_name)
    else:
        logger.info('No sensitive data found')


@app.command(no_args_is_help=True, help='sanipass help!')
def main(
    image: Path = typer.Option(
        ...,
        '--image',
        '-i',
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help='Image to process'
    ),
    sensitive_data_file: Path = typer.Option(
        ...,
        '--sensitive-data',
        '-s',
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help='Sensitive data to sanitize from screenshots'
    ),
    debug: bool = typer.Option(False, '--debug', help='Enable [green]DEBUG[/] output')):

    init_logger(debug)

    logger.info(f'Loading sensitive data from: {sensitive_data_file}')

    if image.is_dir():
        for file in image.iterdir():
            if file.is_file():
                logger.info(f'Sanitizing Image: {file}')
                sanitize_screenshot(str(file), str(sensitive_data_file))
    else:
        sanitize_screenshot(str(image), str(sensitive_data_file))


if __name__ == '__main__':
    app(prog_name='sanipass')
