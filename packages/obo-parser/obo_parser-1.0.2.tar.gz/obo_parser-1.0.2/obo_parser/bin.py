import sys
import json

import click

from obo_parser import version_info
from obo_parser.parser import OBO_Parser


CONTEXT_SETTINGS = dict(
    help_option_names=['-?', '-h', '--help'],
    max_content_width=120,
)


@click.group(
    name=version_info['prog'],
    help=click.style(version_info['desc'], italic=True, fg='cyan', bold=True),
    context_settings=CONTEXT_SETTINGS,
    no_args_is_help=True,
    epilog='contact: {author}<{author_email}>'.format(**version_info),
)
@click.version_option(version=version_info['version'], prog_name=version_info['prog'])
def cli():
    pass


__epilog__ = click.style('''                         
\n\b
example:
    obo_parser headers -f tests/hp.obo
    obo_parser headers -f https://raw.githubusercontent.com/obophenotype/human-phenotype-ontology/master/hp.obo
''', fg='green')
@cli.command(
    help='Print the version of the OBO file parser',
    no_args_is_help=True,
    epilog=__epilog__,
)
@click.option('-f', '--path', help='Path or URL to the OBO file', required=True)
@click.option('-o', '--output', help='Output file path')
def headers(path, output):
    obo = OBO_Parser(path)
    out = open(output, 'w') if output else sys.stdout
    headers = obo.headers
    with out:
        out.write(json.dumps(headers, ensure_ascii=False, indent=2))


__epilog__ = click.style('''                         
\n\b
example:
    obo_parser terms -f tests/hp.obo
    obo_parser terms -f https://raw.githubusercontent.com/obophenotype/human-phenotype-ontology/master/hp.obo
    obo_parser terms -f tests/hp.obo -o terms.jl
''', fg='yellow')

@cli.command(
    help='Print the terms of the OBO file',
    no_args_is_help=True,
    epilog=__epilog__,
)
@click.option('-f', '--path', help='Path or URL to the OBO file', required=True)
@click.option('-o', '--output', help='Output file path')
def terms(path, output):
    obo = OBO_Parser(path)
    out = open(output, 'w') if output else sys.stdout
    with out:
        for term in obo.terms:
            line = json.dumps(term, ensure_ascii=False)
            out.write(line + '\n')


def main():
    cli()


if __name__ == '__main__':
    main()
