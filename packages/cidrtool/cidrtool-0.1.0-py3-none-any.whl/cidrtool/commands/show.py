import click

import netaddr
from netaddr.ip.sets import IPSet
from .common import click_verbose_output, read_args_from_stdin


@click.command()
@click.argument("cidrs", nargs=-1)
@click.option("-v", "--verbose", count=True)
def show(cidrs, verbose):
    """
    Show a group of cidrs, checks overlap and continuity
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

    sorted_net = sorted(
        final_args, key=lambda x: netaddr.IPSet([x]).iprange().sort_key()
    )

    contiguous_ipset = None
    previous_ipset = None
    previous_nets = []
    has_overlap = False
    for net in sorted_net:
        current_ipset = IPSet([net])

        if previous_ipset:
            if previous_ipset.intersection(current_ipset):
                has_overlap = True
                click.echo(
                    click.style(
                        "{} is overlap with {}".format(
                            previous_ipset.iter_cidrs()[0],
                            current_ipset.iter_cidrs()[0],
                        ),
                        fg="red",
                        bold=True,
                    )
                )
        previous_ipset = current_ipset

        if not contiguous_ipset:
            contiguous_ipset = current_ipset
            previous_nets.append(net)
            continue

        new_ipset = contiguous_ipset.copy()
        new_ipset.add(net)
        if new_ipset.iscontiguous():
            previous_nets.append(net)
            contiguous_ipset = new_ipset
            continue
        else:
            print_group(contiguous_ipset, previous_nets)
            contiguous_ipset = None
            previous_nets = []

    if previous_nets:
        print_group(previous_ipset, previous_nets)

    if not has_overlap:
        print("* There is no overlap in this ipset.")


def print_group(ipset, nets):
    nets_len = len(nets)
    for index, net in enumerate(nets):

        if index == len(nets) - 1:
            end = ""
        else:
            end = "\n"

        if index == 0:  # first line
            symbol = "┐"
            padding = "─"
            if nets_len == 1:
                symbol = "─"
        elif index == nets_len - 1:  # last line
            symbol = "┴"
            padding = "─"
        else:  # middle
            symbol = "│"
            padding = " "

        print("{0:{2}<19}{1}".format(net, symbol, padding), end=end)
    for iprange in ipset.iter_ipranges():
        print("── ", end="")
        click.echo(click.style(iprange, fg="yellow"), nl=False)
        click.echo(
            click.style(" ({} total IPs)".format(len(iprange)), fg="magenta"), nl=True
        )
