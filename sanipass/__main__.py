import math
import typer
from pathlib import Path
from Levenshtein import distance as lev_distance
from sanipass.app.image.models.sanipass_image import SanipassImage
from sanipass.app.ocr.ocr_processor import OCRProcessor
from sanipass.logger import init_logger, logger, console
from sanipass import __version__

app = typer.Typer(
    add_completion=False,
    rich_markup_mode='rich',
    context_settings={'help_option_names': ['-h', '--help']},
    pretty_exceptions_show_locals=False
)

TYPER_OPTION_INPUT = typer.Option(
    None,
    '--input',
    '-i',
    exists=True,
    file_okay=True,
    dir_okay=True,
    readable=True,
    resolve_path=True,
    help='Image or directory of images to process'
)

TYPER_OPTION_INPUT_FILE = typer.Option(
    None,
    '--input-file',
    '-if',
    # exists=True,
    # file_okay=True,
    # dir_okay=False,
    # readable=True,
    # resolve_path=True,
    help='File with line-separated list of image files to process'
)
TYPER_OPTION_SENSITIVE_DATA_FILE = typer.Option(
    ...,
    '--sensitive-data',
    '-s',
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    resolve_path=True,
    help='Sensitive data to sanitize from screenshots'
)

TYPER_OPTION_DEBUG = typer.Option(
    False, '--debug', help='Enable [green]DEBUG[/] output'
)

def get_files_to_process(files:Path=None, input_file:typer.FileText=None):
    images = []

    if files:
        if files.is_dir():
            for file in files.iterdir():
                if file.is_file():
                    images.append(file)
        else:
            images.append(files)

    if input_file:
        for line in input_file.read().splitlines():
            images.append(line)

    return images


def load_sensitive_data(input_file):
    # Initialize sensitive data
    sensitive_data = []

    logger.info(f"Loading sensitive data from {input_file}")
    with open(input_file) as f:
        for data in f.read().splitlines():
            if data.strip() != "":
                sensitive_data.append(data)
    return sensitive_data


def validate_options(input, input_file):
    if input == None and input_file == None:
        raise ValueError("Either --input or --input-file must be specified")


def perform_setup(input, input_file, debug):
    init_logger(debug)
    validate_options(input, input_file)


def find_words_with_levenshtein_distance(word, text, max_distance):
    result = []
    for text_word in text.split():
        if lev_distance(word, text_word) <= max_distance:
            result.append(text_word)
    return result


def get_sensitive_images(input_files, sensitive_data_file, max_levenshtein_distance=None):
    sensitive_images = []
    sensitive_data = load_sensitive_data(sensitive_data_file)

    ocr_processor = OCRProcessor(
        user_words=str(sensitive_data_file),
        user_patterns=str(sensitive_data_file))

    for file in input_files:
        logger.info(f'Sanitizing Image: {file}')

        image = SanipassImage(str(file))

        # Process OCR data
        image.add_ocr_entries(ocr_processor.get_ocr_data(image.path))
        logger.info(f'Found {len(image.ocr_entries)} OCR blocks in {image.path}')

        # Find sensitive data
        for ocr_entry in image.ocr_entries:
            for data in sensitive_data:
                is_sensitive = False
                if data in ocr_entry.text:
                    logger.debug(f'Found sensitive data in line: {ocr_entry.text}')
                    ocr_entry.sensitive = True
                    ocr_entry.sensitive_match.append(data)
                else:
                    if max_levenshtein_distance is None:
                        max_distance = math.ceil(len(data) / 8)
                    else:
                        max_distance = max_levenshtein_distance

                    sensitive_words = find_words_with_levenshtein_distance(data, ocr_entry.text, max_distance)
                    for word in sensitive_words:
                        logger.debug(f'Found potentially sensitive data: {word}')
                        ocr_entry.sensitive = True
                        ocr_entry.sensitive_match.append(word)

        number_of_sensitive_entries = len(image.get_sensitive_ocr_entries())
        if number_of_sensitive_entries == 0:
            logger.info(f'No sensitive data found in {file}')
        else:
            logger.info(f'Found {number_of_sensitive_entries} sensitive OCR entries in {file}')
            sensitive_images.append(image)

    logger.info(f'Found {len(sensitive_images)} images containing sensitive information.')
    return sensitive_images


@app.command(no_args_is_help=True, help='sanipass help!')
def main(
    input:Path = TYPER_OPTION_INPUT,
    input_file:typer.FileText = TYPER_OPTION_INPUT_FILE,
    sensitive_data_file:Path = TYPER_OPTION_SENSITIVE_DATA_FILE,
    max_levenshtein_distance: int = typer.Option(
        None,
        '--max-distance',
        '-m',
        help='The maximum Levenshtein distance between a sensitive word and the detected word.'
    ),
    report_only: bool = typer.Option(
        False,
        '--report-only',
        '-r',
        help='Do not modify files, only report files with sensitive data'
    ),
    keep_first: int = typer.Option(
        0,
        '--keep-first',
        '-kf',
        help="Keep the first N characters from being redacted."
    ),
    keep_last: int = typer.Option(
        0,
        '--keep-last',
        '-kl',
        help="Keep the last N characters from being redacted."
    ),
    overwrite: bool = typer.Option(
        False,
        '--overwrite',
        help='Overwrite existing sanitized images'
    ),
    debug:bool = TYPER_OPTION_DEBUG):

    perform_setup(input, input_file, debug)

    input_files = get_files_to_process(input, input_file)
    sensitive_images = get_sensitive_images(input_files, sensitive_data_file, max_levenshtein_distance)

    for image in sensitive_images:
        console.print(image.path)

        if report_only:
            continue
        else:
            # Redact sensitive data
            image.redact_sensitive_data(keep_first=keep_first, keep_last=keep_last)

            # Save sanitized image
            old_path = Path(image.path)
            new_path = str(old_path.absolute()).replace(
                old_path.suffix, f'-sanitized{old_path.suffix}'
            )
            image.save(path=new_path, overwrite=overwrite)


if __name__ == '__main__':
    app(prog_name='sanipass')
