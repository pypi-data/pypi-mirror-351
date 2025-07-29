import click
import sys

def click_verbose_output(verbose, text):
    if verbose:
        click.echo(click.style(text, fg="yellow"))


def read_args_from_stdin():
    args = []
    for line in sys.stdin:
        striped = line.strip()
        if not striped:
            continue
        splited = striped.split(",")
        for arg in splited:
            striped = arg.strip()
            if not striped:
                continue
            args.append(arg)

    return args
