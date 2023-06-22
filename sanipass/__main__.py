import typer
from pathlib import Path
from sanipass.app.image.models.sanipass_image import SanipassImage
from sanipass.app.ocr.ocr_processor import OCRProcessor
from sanipass.logger import init_logger, logger
from sanipass import __version__

app = typer.Typer(
    add_completion=False,
    rich_markup_mode='rich',
    context_settings={'help_option_names': ['-h', '--help']},
    pretty_exceptions_show_locals=False
)


def get_files_to_process(input_files:Path):
    images = []

    if input_files.is_dir():
        for file in input_files.iterdir():
            if file.is_file():
                images.append(file)
    else:
        images.append(input_files)

    return images


def load_sensitive_data(input_file):
    # Initialize sensitive data
    sensitive_data = []

    logger.info(f"Loading sensitive data from {input_file}")
    with open(input_file) as f:
        sensitive_data = f.read().splitlines()


    return sensitive_data


@app.command(no_args_is_help=True, help='sanipass help!')
def main(
    input: Path = typer.Option(
        ...,
        '--input',
        '-i',
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        help='Image or directory of images to process'
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
    overwrite: bool = typer.Option(
        False,
        '--overwrite',
        help='Overwrite existing sanitized images'
    ),
    debug: bool = typer.Option(False, '--debug', help='Enable [green]DEBUG[/] output')):

    init_logger(debug)

    sensitive_data = load_sensitive_data(sensitive_data_file)

    ocr_processor = OCRProcessor(
        #sensitive_data_file=str(sensitive_data_file),
        user_words=str(sensitive_data_file),
        user_patterns=str(sensitive_data_file))

    for file in get_files_to_process(input):
        logger.info(f'Sanitizing Image: {file}')

        image = SanipassImage(str(file))

        # Process OCR data
        image.add_ocr_entries(ocr_processor.get_ocr_data(image.path))
        logger.info(f'Found {len(image.ocr_entries)} OCR blocks in {image.path}')

        # Find sensitive data
        for ocr_entry in image.ocr_entries:
            for data in sensitive_data:
                if data in ocr_entry.text:
                    logger.debug(f'Found sensitive data in line: {ocr_entry.text}')
                    ocr_entry.sensitive = True
                    ocr_entry.sensitive_match = data

        number_of_sensitive_entries = len(image.get_sensitive_ocr_entries())
        if number_of_sensitive_entries == 0:
            logger.info(f'No sensitive data found in {file}')
            continue
        else:
            logger.info(f'Found {number_of_sensitive_entries} sensitive OCR entries in {file}')

            # Redact sensitive data
            image.redact_sensitive_data()

            # Save sanitized image
            image.save(
                path=str(file.absolute()).replace(
                    file.suffix, f'-sanitized{file.suffix}'
                ), overwrite=overwrite)


if __name__ == '__main__':
    app(prog_name='sanipass')
