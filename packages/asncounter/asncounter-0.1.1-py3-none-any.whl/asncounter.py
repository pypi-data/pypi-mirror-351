#!/usr/bin/python

"""collect hits per ASN and netblock"""

__epilog__ = r"""
Examples, tracking all traffic from tcpdump except one and ARP:

tcpdump -q -i eth0 -n -Q in "(udp or tcp)" | asncounter.py --input-format=tcpdump

Rough (but slower) equivalent with scapy:

asncounter.py --interface eth0

Extracting IP addresses from access logs:

awk '{print $1}' access.log | asncounter.py

Basic RIB database takes 250MB just to load, memory size probably
scales linearily with the number of ASN and prefixes recorded.

Can likely not sustain a full gigabit DDOS, in testing could barely
sustain 200k tcpdump lines per second (about 100mbps at 64 byte per
packet) on a Intel 12th gen, although that is fine for a gigabit with
1500 byte packets."""

# similar tools:
# https://jpastuszek.net/asn/
# https://github.com/projectdiscovery/asnmap
# https://github.com/nitefood/asn
# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1055284#37

# TODO:
# - upstream parts of this: https://github.com/hadiasghari/pyasn/issues/82
#
# - scapy is eating too much CPU. 10-25% of a core (and 100% without
#   the layers filter), while doing the tcpdump pipe takes virtually
#   nothing. possible optimization:
#   https://askldjd.wordpress.com/2014/01/15/a-reasonably-fast-python-ip-sniffer/
#
# - count sizes? probably requires fixing the above to not go crazy
#   with tcpdump regexes, and "two fields" approach for the simpler
#   "one per line" parser
#
# - reload databases on change

import argparse
import code
import json
import logging
import os
import re
import sys
import threading
from collections import Counter
from functools import partial
from pathlib import Path
from signal import SIGHUP, signal
from subprocess import CalledProcessError, run
from typing import Any, Callable, TextIO

try:
    import prometheus_client

    prometheus_client_available = True

except ImportError:
    prometheus_client_available = False


import pyasn

try:
    from scapy.config import conf
    from scapy.interfaces import get_working_if
    from scapy.layers.inet import IP
    from scapy.packet import Packet
    from scapy.sendrecv import sniff

    scapy_available = True
    conf.layers.filter([IP])
except ImportError:
    Packet = Any  # type: ignore
    scapy_available = False


args = argparse.Namespace()

RIBFILE_GLOB = r"rib.*"
DATFILE_GLOB = r"ipasn_*"

TCPDUMP_REGEX = re.compile(
    r"""
^[^ ]+  # datetime
[ ]IP6?[ ]
(?:\[[^]]+][ ]\(invalid\)[ ])?  # anomalies like "[total length 52 > length 44] (invalid)"
(?P<src>[0-9a-fA-F:.]+)  # source, e.g. 203.0.113.42.62122
[ ]>[ ]  # seperator, e.g. " > "
(?P<dst>[0-9a-fA-F:.]+)  # destination, e.g. 2001:DB8::2.443
:.* # whatever else follows
""",
    re.VERBOSE,
)


class Recorder:
    asndb = None
    asnamesdb = None

    def record(self, asn: int | None, prefix: str | None) -> None:
        raise NotImplementedError()

    def display_results(self, stream: TextIO = sys.stdout) -> None:
        raise NotImplementedError()

    def lookup_address(self, address: str) -> tuple[int | None, str | None]:
        """lookup the given address in the ASN database

        This automatically loads the DB if not done yet.
        """
        if self.asndb is None:
            datfile = str(find_cachefiles(DATFILE_GLOB)[-1].absolute())
            logging.info("loading datfile %s...", datfile)
            self.asndb = pyasn.pyasn(datfile)

        return self.asndb.lookup(address)

    def lookup_asn(self, asn: int) -> str | None:
        """lookup the AS name based on the number

        This automatically loads the JSON file if not already loaded.
        """
        if self.asnamesdb is None:
            asfile = Path(args.cache_directory) / "asnames.json"
            if not asfile.exists():
                download_asnames()
            logging.info("loading %s", str(asfile))
            with asfile.open() as fp:
                self.asnamesdb = json.load(fp)

        return self.asnamesdb.get(str(asn))


class CollectionsRecorder(Recorder):
    def __init__(self) -> None:
        self.asn_counter: Counter = Counter()
        # optimise with pyradix, if necessary
        self.prefix_counter: Counter = Counter()

    def record(self, asn: int | None, prefix: str | None) -> None:
        """record a hit for the match in regular collection counters

        This *could* be optimized a little further, by moving the "if"s
        upwards, because we're called from inside our hot loop.
        """
        # record the ASN, if relevant
        if not args.no_asn:
            self.asn_counter[asn] += 1
        # record the prefix, if relevant
        if not args.no_prefixes:
            self.prefix_counter[prefix] += 1
        # we resolve ASNs later, on display, in this pattern

    def display_results(self, stream: TextIO = sys.stdout) -> None:
        """display results for our regular collections counters

        This takes care of showing a tab-separated table of results for
        ASNs and prefix counters.

        This is where we lookup the ASNs in our regular, non-Prometheus
        case.
        """
        if not args.no_asn:
            if not args.no_resolve_asn:
                try:
                    # test lookups:
                    self.lookup_asn(1)
                except (CalledProcessError, json.JSONDecodeError) as e:
                    logging.warning(
                        "failed to download or read asnames.json, disabling resolver: %s",
                        e,
                    )
                    args.no_resolve_asn = False
            total = self.asn_counter.total()
            if not args.no_resolve_asn:
                print("count\tpercent\tASN\tAS", file=stream)
                for asn, count in self.asn_counter.most_common(args.top):
                    ratio = round(count / total * 100, 2)
                    print(
                        count, ratio, asn, self.lookup_asn(asn), sep="\t", file=stream
                    )
            else:
                print("count\tASN", file=stream)
                for asn, count in self.asn_counter.most_common(args.top):
                    ratio = round(count / total * 100, 2)
                    print(count, ratio, asn, sep="\t", file=stream)
            print("total:", total, file=stream)

        if not args.no_prefixes:
            total = self.prefix_counter.total()
            print("count\tpercent\tprefix\tASN\tAS", file=stream)
            for prefix, count in self.prefix_counter.most_common(args.top):
                if prefix:
                    address, _ = prefix.split("/")
                    asn, _ = self.lookup_address(address)
                    asname = self.lookup_asn(asn)
                else:
                    asn = asname = ""
                ratio = round(count / total * 100, 2)
                print(count, ratio, prefix, asn, asname, sep="\t", file=stream)
            print("total:", total, file=stream)


class PrometheusRecorder(Recorder):

    def __init__(self) -> None:
        self.asn_metrics_counter = prometheus_client.Counter(
            "asncounter_asn", "hits per AS number", ["asn", "name"]
        )
        self.prefix_metrics_counter = prometheus_client.Counter(
            "asncounter_prefix", "hits per CIDR prefix", ["cidr", "asn", "name"]
        )

    def record(self, asn: int | None, prefix: str | None) -> None:
        """record a hit for the match in Prometheus

        This probably needs to be optimized, as it's inside a hot loop and
        has many checks.
        """
        # lookup ASN, if relevant
        #
        # we do not seem to have the option to resolve those on display
        # and, anyways, because of the way Prometheus works, we'd be
        # constantly resolving those, so it seems better to store those
        # here.
        name = None
        if not args.no_resolve_asn and asn:
            name = self.lookup_asn(asn)
        if name is None:
            name = ""

        # record the ASN, if relevant
        if not args.no_asn:
            self.asn_metrics_counter.labels(asn, name).inc()

        # record the prefix, if relevant
        if not args.no_prefixes:
            self.prefix_metrics_counter.labels(
                prefix, asn if not args.no_asn else "", name
            ).inc()

    def display_results(self, stream: TextIO = sys.stdout) -> None:
        """display results from the Prometheus metrics

        This is really just a stub for the `generate_latest` function,
        that we dump on stdout.
        """
        # extract only our metric names from the registry
        our_metrics = [
            metric
            for metric in prometheus_client.REGISTRY._names_to_collectors.keys()
            if metric.startswith("asncounter")
        ]
        # make a special registry just for our metrics
        #
        # this removes the `python_*` metrics from the output, which makes
        # it more suitable for node-exporter textfile collector output,
        # and generally more readable for standard output as well
        #
        # the webserver output retains those, however
        registry = prometheus_client.REGISTRY.restricted_registry(our_metrics)
        # there's a bug in the upstream lib here: generate_latest()
        # expects a CollectorRegistry but we're told to do this to
        # restrict the output
        output = prometheus_client.generate_latest(registry).decode("utf-8")  # type: ignore
        print(output, file=stream, end="")


class Collector:
    def __init__(self, recorder: Recorder) -> None:
        self.recorder = recorder

    def _collect(
        self,
        stream: TextIO = sys.stdin,
        parser: Callable[[str], str | None] | None = None,
    ) -> None:
        raise NotImplementedError()

    def collect(
        self,
        stream: TextIO = sys.stdin,
        parser: Callable[[str], str | None] | None = None,
    ) -> None:
        try:
            self._collect(stream, parser)
        except KeyboardInterrupt:
            pass
        logging.info("finished reading data")


class ScapyCollector(Collector):
    def _collect(
        self,
        stream: TextIO = sys.stdin,
        parser: Callable[[Packet], str | None] | None = None,  # type: ignore[override]
    ) -> None:
        if parser is None:
            parser = self._parse
        if args.interface:
            logging.info("reading packets from interface %s", args.interface)
            sniff(
                filter=args.scapy_filter,
                prn=parser,
                store=False,
                iface=args.interface,
            )
        else:
            logging.info("reading packets stream %s", getattr(stream, "name", stream))
            sniff(
                filter=args.scapy_filter,
                prn=parser,
                store=False,
                offline=args.input,
            )

    def _parse(
        self,
        packet: Packet,
    ) -> None:
        """callback for the scapy sniffer

        Essentially just lookup the packet's IP address and do the rest of
        the normal checks.
        """
        address = packet[IP].src
        try:
            asn, prefix = self.recorder.lookup_address(address)
        except ValueError as e:
            logging.warning(
                "failed to lookup address %s (%s), skipped packet %s",
                address,
                e,
                packet.summary(),
            )
            return
        # too hot, about 1ms / 1k packets
        # logging.debug("IP %s matched to ASN %s prefix %s", address, asn, prefx)
        self.recorder.record(asn, prefix)


class LineCollector(Collector):
    def _collect(
        self,
        stream: TextIO = sys.stdin,
        parser: Callable[[str], str | None] | None = None,
    ) -> None:
        """record IP addresses from stream, with the given parser

        By default, the parser is a noop, that is each line is an IP
        address, but parse_tcpdump can be used to extract the source IP
        address.
        """
        if parser is None:

            def parser(address: str | None = None):
                return address

        logging.info("collecting addresses from %s", getattr(stream, "name", stream))
        for line in stream:
            line = line.strip()
            address = parser(line)
            if not address:
                logging.warning("failed to parse line, skipped: %s", line)
                continue
            try:
                asn, prefix = self.recorder.lookup_address(address)
            except ValueError as e:
                logging.warning(
                    "failed to lookup address %s (%s), skipped line: %s",
                    address,
                    e,
                    line,
                )
                continue
            # too hot, about 1ms / 1k packets
            # logging.debug("IP %s matched to ASN %s prefix %s", address, asn, prefx)
            self.recorder.record(asn, prefix)


class TcpdumpLineCollector(LineCollector):
    def _collect(
        self,
        stream: TextIO = sys.stdin,
        parser: Callable[[str], str | None] | None = None,
    ) -> None:
        """record IP addresses from stream, with the tcpdump parser

        By default, the parser is a noop, that is each line is an IP
        address, but parse_tcpdump can be used to extract the source IP
        address.
        """
        if parser is None:
            parser = self.parse
        super()._collect(stream, parser)

    def parse(self, line: str) -> str | None:
        """parse a tcpdump line for source/destination IP addresses"""
        m = TCPDUMP_REGEX.match(line)
        if not m:
            logging.warning("cannot parse tcpdump line %s, ignoring", line.strip())
            return None

        # we split out the port at the end, because it's too complicated
        # to do that in the regex directly, especially in IPv4 mode
        # because the separator is the same
        for address_port in (m.group("src"), m.group("dst")):
            split = address_port.rsplit(".", maxsplit=1)
            return split[0]
        return None


def find_datfile() -> str:
    """find a valid datfile, downloading if missing"""
    datfiles = find_cachefiles(DATFILE_GLOB)
    if datfiles:
        return datfiles[-1].name

    ribfiles = find_cachefiles(RIBFILE_GLOB)
    if ribfiles:
        # special case: ribfile, not datfile
        ribfile = ribfiles[-1].name
        datfile = guess_datfile(ribfile)
        datfile_path = Path(args.cache_directory) / datfile
        # this is not normally reachable because the
        # find_cachefiles(DATFILE_GLOB) above should find it, but just
        # in case
        if datfile_path.exists():
            return str(datfile_path)
        logging.info(
            "ribfile %s found but not datfile %s, converting", ribfile, datfile
        )
        return convert_ribfile(ribfile)
    logging.info(
        "no rib file caches found in %s/%s", args.cache_directory, RIBFILE_GLOB
    )
    return refresh_datfile()


def refresh_datfile() -> str:
    """download a ribfile and convert into a datfile unconditionnally"""
    try:
        ribfile = download_ribfile()
        return convert_ribfile(ribfile)
    except CalledProcessError as e:
        logging.error("failed to download or convert ribfiles: %s", e)
        sys.exit(1)


def find_cachefiles(glob: str) -> list[Path]:
    """find files in the cache directory matching a pattern"""
    target_path = Path(args.cache_directory)
    ribfiles = sorted(target_path.glob(glob))
    logging.debug("%d matching files found in %s/%s", len(ribfiles), target_path, glob)
    return ribfiles


def guess_datfile(ribfile: str) -> str:
    """guess the datfile related to the ribfile"""
    # rib.20250522.1400.bz2
    _, date, time, suffix = ribfile.split(".")
    return f"ipasn_{date}.{time}.dat.gz"


def download_ribfile() -> str:
    """download a ribfile in the cache directory

    This does *not* convert it. It's a stub because we hope we move
    this upstream.

    This raises CalledProcessError, or assertion.
    """
    cmd = ["pyasn_util_download.py", "--latestv46"]
    logging.info("downloading rib file with: %s", " ".join(cmd))
    run(cmd, cwd=args.cache_directory, check=True)
    ribfiles = find_cachefiles(RIBFILE_GLOB)
    assert ribfiles, "no rib file found"
    return ribfiles[-1].name


def download_asnames():
    """download the AS mapping file in the cache directory"""
    cmd = ["pyasn_util_asnames.py", "--output", "asnames.json"]
    logging.info("downloading AS names mappings with: %s", " ".join(cmd))
    run(cmd, cwd=args.cache_directory, check=True)


def convert_ribfile(ribfile: str):
    """convert the given ribfile into a datfile"""
    datfile = guess_datfile(ribfile).removesuffix(".gz")
    cmd = ["pyasn_util_convert.py", "--compress", "--single", ribfile, datfile]
    logging.info("converting file %s to %s with: %s", ribfile, datfile, cmd)
    # pyasn_util_convert.py --single rib.20250522.1400.bz2 ipasn_20250522.1400.dat
    run(cmd, cwd=args.cache_directory, check=True)
    return str(Path(args.cache_directory) / datfile)


def parse_args() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=__epilog__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--cache-directory",
        "-C",
        default=os.environ.get("XDG_CACHE_HOME", os.environ["HOME"] + "/.cache")
        + "/pyasn",
        help="where to store pyasn cache files, default: %(default)s",
    )
    parser.add_argument(
        "--no-prefixes",
        action="store_true",
        help="count by prefix, default: enabled",
    )
    parser.add_argument(
        "--no-asn",
        action="store_true",
        help="count by ASN, default: enabled",
    )
    parser.add_argument(
        "--no-resolve-asn",
        action="store_true",
        help="resolve AS numbers into names in output, default: enabled",
    )
    parser.add_argument(
        "--top",
        "-t",
        type=int,
        default=10,
        metavar="N",
        help="only show top N entries, default: %(default)s",
    )
    parser.add_argument(
        "--input",
        "-i",
        default=sys.stdin,
        type=argparse.FileType(mode="r"),
        help="input file, default: stdin",
    )
    parser.add_argument(
        "--input-format",
        "-I",
        default="line",
        choices=["line", "tcpdump", "scapy"],
        help="input format, default: %(default)s",
    )
    parser.add_argument(
        "--scapy-filter",
        default="ip and not src host 0.0.0.0 and not src net 192.168.0.0/24",
        help="BPF filter to apply to incoming packets, default: %(default)s",
    )
    parser.add_argument(
        "--interface",
        nargs="?",
        const=get_working_if() if scapy_available else "eth0",
        help="open an interface instead of stdin for packets, implies -I scapy, auto-detects by default",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=argparse.FileType(mode="w"),
        default=sys.stdout,
        help="write stats or final prometheus metrics to the given file, default: stdout",
    )
    parser.add_argument(
        "--output-format",
        "-O",
        default="tsv",
        choices=["tsv", "prometheus", "null"],
        help="output format, choices: %(choices)s, default: %(default)s",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        nargs="?",
        const=8999,
        default=argparse.SUPPRESS,
        help="start a prometheus server on the given port, default disabled, port %(const)s if unspecified",
    )
    parser.add_argument(
        "--refresh",
        "-R",
        action="store_true",
        help="download a recent RIB cache file and exit",
    )
    parser.add_argument(
        "--repl",
        action="store_true",
        help="run a REPL thread in main loop",
    )
    parser.add_argument("--debug", action="store_true", help="more debugging output")
    parser.parse_args(namespace=args)

    if args.output_format == "prometheus":
        if not prometheus_client_available:
            parser.error("failed to load prometheus_client library")

    if args.interface:
        args.input_format = "scapy"

    if args.input_format == "scapy" and not scapy_available:
        parser.error("failed to load scapy library")

    if args.no_asn:
        args.no_resolve_asn = True


def main() -> None:
    parse_args()

    logging.basicConfig(
        level="DEBUG" if args.debug else "INFO", format="%(levelname)s: %(message)s"
    )

    if not Path(args.cache_directory).exists():
        Path(args.cache_directory).mkdir(parents=True)

    if args.refresh:
        refresh_datfile()
        sys.exit(0)

    # download missing files before we start, instead of on first hit.
    logging.info("using datfile %s", find_datfile())

    # setup display procedures and prom server
    prom_server = None
    recorder: Recorder = CollectionsRecorder()
    if args.output_format == "prometheus":
        recorder = PrometheusRecorder()
        if getattr(args, "port"):
            try:
                prom_server, prom_thread = prometheus_client.start_http_server(
                    args.port
                )
            except TypeError:
                # older prometheus_client libraries don't return the server object
                pass
            logging.info("Prometheus metrics exposed on port %s", args.port)
    if args.output_format != "null":
        signal(SIGHUP, lambda s, f: recorder.display_results())

    if args.input_format == "tcpdump":
        cls: type[Collector] = TcpdumpLineCollector
    elif args.input_format == "line":
        cls = LineCollector
    elif args.input_format == "scapy":
        cls = ScapyCollector
    else:
        # not reached
        raise ValueError("invalid input format: %s" % args.input_format)

    collector = partial(cls(recorder=recorder).collect, stream=args.input)

    # main read loop
    if args.repl:
        collect_thread = threading.Thread(target=collector, daemon=True)
        collect_thread.start()

        sys.stdin = open("/dev/tty")  # reopen terminal to get a fresh stdin
        logging.info(
            "starting interactive console, use recorder.display_results() to show current results",
        )
        if not args.output_format == "prometheus":
            logging.info(
                "recorder.asn_counter and .prefix_counter dictionnaries have the full data"
            )

        # need to extract the namespace before we enter the thread,
        # which runs with different locals
        namespace = locals() | globals()
        repl_thread = threading.Thread(
            target=lambda: code.interact(local=namespace), daemon=True
        )
        repl_thread.start()
        try:
            repl_thread.join()
        except KeyboardInterrupt:
            pass
    else:
        collector()

    if prom_server:
        prom_server.shutdown()
        prom_thread.join()

    if args.output_format != "null":
        # done collecting results, show a final stats dump
        recorder.display_results(args.output)


if __name__ == "__main__":  # pragma: nocover
    main()
