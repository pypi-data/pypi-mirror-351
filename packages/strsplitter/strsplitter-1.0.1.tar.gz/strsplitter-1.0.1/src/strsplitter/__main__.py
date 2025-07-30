from strsplitter.splitter import SplitByAnyChar
from .strsplitter import split
import click
import sys


@click.command()
@click.option(
	'--delimiters',
	'-d',
	default=' \n\t\r\f',
	help='Delimiters to use for splitting the input string.',
)
@click.argument('input_file', nargs=1)
def main(delimiters: str, input_file: str):
	"""Splits the content of the input file by the specified delimiters."""
	try:
		with open(input_file, 'r', encoding='utf-8') as file:
			content = file.read()
	except FileNotFoundError:
		print(f"Error: File '{input_file}' not found.", file=sys.stderr)
		sys.exit(1)
	_delimiters = bytes(delimiters, 'utf-8').decode('unicode_escape')
	result = split(content, SplitByAnyChar(_delimiters))

	for part in result:
		click.echo(part)


if __name__ == '__main__':
	main()
