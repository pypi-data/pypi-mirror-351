import click
import sys

import netaddr


@click.command()
@click.argument("cidrs", nargs=-1)
@click.option("-v", "--verbose", count=True)
def merge_cidr(cidrs, verbose):
    """
    Merge CIDR, you can pass the CIDRs from cli arguments or stdin.

    \b
    Example Usage:
    cidrtool merge-cidr 10.0.2.0/24 10.0.2.0/16

    \b
    Or pass from stdin:
    cat cidrs.txt | cidrtool merge-cidr -
    In cidrs.txt file, you should put cidr on each line.
    """
    final_args = []
    for item in cidrs:
        if item == "-":
            stdin_args = read_args_from_stdin()
            click_verbose_output(verbose, "args from stdin: {}".format(stdin_args))
            final_args.extend(stdin_args)
        else:
            final_args.append(item)
    click_verbose_output(verbose, f"Final args: {final_args}")

    ip_addrs = netaddr.cidr_merge(final_args)

    for ip_addr in ip_addrs:
        click.echo(ip_addr)


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
