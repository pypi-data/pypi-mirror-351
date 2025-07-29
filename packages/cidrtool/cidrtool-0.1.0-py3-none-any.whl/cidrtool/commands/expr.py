import io
import click
from netaddr import IPAddress, IPNetwork, IPSet, cidr_merge


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument(
    "expressions",
    nargs=-1,
)
@click.option("-v", "--verbose", count=True)
def expr(expressions, verbose):
    """
    CIDR calulation.
    \b
    Example Usage:

    \b
    Merge multiple CIDRs:
        cidrtool expr 192.168.0.0/22 +192.168.4.0/22 +192.168.22.0/22

    \b
    Exclude IP from CIDR:
        cidrtool expr 192.168.0.0/22 -192.168.2.11

    """
    if len(expressions) < 2:
        raise click.UsageError("At least two expressions")

    base_cidr = expressions[0]
    base_ipset = IPSet([base_cidr])

    if verbose:
        debug_buffer = io.StringIO()
        debug_buffer.write(
            click.style(
                "base cidr: ".format(),
                fg="blue",
                bold=True,
            )
        )
        debug_buffer.write(debug_cidr(base_cidr))

        click.echo(debug_buffer.getvalue())

    for expression in expressions[1:]:
        operator = expression[0]
        cidr = expression[1:]
        debug_buffer = io.StringIO()

        if verbose:
            debug_buffer.write(
                click.style(
                    "operator: {}, ".format(
                        operator,
                    ),
                    fg="blue",
                    bold=True,
                )
            )

        if operator == "-":
            if verbose:
                debug_buffer.write(debug_cidr(cidr))
            base_ipset = base_ipset - IPSet([cidr])

        if operator == "+":
            if verbose:
                debug_buffer.write(debug_cidr(cidr))
            base_cidrs = list(base_ipset.iter_cidrs())
            base_cidrs.append(cidr)
            merged_cidrs = cidr_merge(base_cidrs)
            base_ipset = IPSet(merged_cidrs)

        if verbose:
            click.echo(debug_buffer.getvalue())

    for item in base_ipset.iter_cidrs():
        print(item)


def debug_cidr(cidr):
    try:
        ipnetwork = IPNetwork(cidr)

        return click.style(
            "cidr: {}, {} ~ {}".format(
                cidr,
                IPAddress(ipnetwork.first).format(),
                IPAddress(ipnetwork.last).format(),
            ),
            fg="yellow",
        )
    except:
        return click.style(cidr)
