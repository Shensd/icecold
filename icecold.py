#!/usr/bin/python3

import sys
import signal
import os

# local imports
from args.cmdargparser import *
from scraper.wordlist_site_scraper import WordListSiteScraper
from output.output_controller import OutputController
from wordlist.wordlist_processor import WordListProcessor

"""
There are essentailly 3 parts to this project

- cmd argument parser
  - output location
  - remove captials
  - provide list of websites
    - allow/deny outside domain
  - output size cap
  - keep numbers

- site scaper
  - pick meaningful elements
  - if recursive set then find links
    - test if links are outside domain
    - depth of links to search through

- word list generator
  - remove punctuation
  - add specified characters
  - remove/keep capitals
  - remove/keep language/special characters
  - remove/keep numbers

I think we should make a distinct effort to separate functions for this 
project, scraper should not modify text, just find it

the main advantage we want this to have over CeWL is more efficient use of 
memory, this can be done by progressively reading and writing words
- a good method for this would be a variable set number of words would be 
  read, and then they would be passed to the word list generator to be 
  piplined and then written to disk
"""

def print_help(flags):

    def format_flag(flag):
        if not flag.short_name:
            binds = "    --{}".format(flag.name)
        else:
            binds = "-{}, --{}".format(flag.short_name, flag.name)

        return "{}\t{}".format(binds, flag.description)

    header = """icecold - website wordlist generator

usage: icecold.py [url] [options...]
    """

    print(header)

    for flag in flags:
        print("  {}".format(format_flag(flag)))

    print("")
    print("made with love by shensd")


def main(argv):
    arg_string = " ".join(argv)

    cmd_flags = [
        CmdFlag(
            "url",
            "Base url to scrape",
            None,
            short_name="u",
            accepted_type="str"
        ),
        CmdFlag(
            "url-file",
            "Use a file with a list of urls, with one on each line",
            None,
            short_name="U",
            accepted_type="str"
        ),
        CmdFlag(
            "output",
            "Output file location to dump wordlist (default stdout)",
            None,
            short_name="o",
            accepted_type="str"
        ),
        CmdFlag(
            "min-word-len",
            "Minimum word length to accept (default 3)",
            3,
            short_name="m",
            accepted_type="int"
        ),
        CmdFlag(
            "max-word-len",
            "Maximum word length to accept (default 15)",
            15,
            short_name="M",
            accepted_type="int"
        ),
        CmdFlag(
            "chain-len",
            "Maximum length to make word chains (default 3)",
            3,
            short_name="c",
            accepted_type="int"
        ),
        CmdFlag(
            "help",
            "Display this help page",
            False,
            short_name='h'
        ),
        CmdFlag(
            "ignore-unresponsive",
            "Do not halt program when a website doesn't respond, skip website instead",
            False
        ),
        CmdFlag(
            "depth",
            "How many links deep to spider pages (default 1)",
            1,
            short_name="d",
            accepted_type="int"
        ),
        CmdFlag(
            "no-leave-domain",
            "Disallow leaving domain while spidering",
            False
        ),
        CmdFlag(
            "ua",
            "Set the user agent used in requests",
            "python-requests",
            accepted_type="str"
        ),
        CmdFlag(
            "charset",
            "Charset to use when making word chains, (default '_-')",
            "_-",
            short_name="c",
            accepted_type="str"
        )
    ]

    default_flags = [
        CmdDefault(
            "url",
            "str"
        )
    ]

    command = CmdArgParser(arg_string, cmd_flags, default_flags=default_flags)

    if command.flags["help"]:
        print_help(cmd_flags)

        return

    if command.flags["output"] != None:
        out = OutputController(command.flags["output"])
    else:
        out = OutputController("", standard_out=True)

    if command.flags["url"] and command.flags["url-file"]:
        print("[error] Both url and url-file parameters cannot be used at the same time.")
        print_help(cmd_flags)
        return

    wl_processor = WordListProcessor(
        out, 
        max_combo_length=command.flags["chain-len"],
        min_word_length=command.flags["min-word-len"], 
        max_word_length=command.flags["max-word-len"],
        charset=command.flags["charset"]
    )

    if command.flags["url-file"]:
        url_file_name = command.flags["url-file"]

        if not os.path.isfile(url_file_name):
            print("[error] Provided url file does not exist")
            print_help(cmd_flags)
            return

        with open(url_file_name, "r") as url_file:
            urls = url_file.readlines()

            # strip whitespace and newlines at end of lines
            urls = [ str.strip(url) for url in urls ]

            for url in urls:
                # skip empty urls
                if url == "": continue

                scrape_url(url, wl_processor, command)    

        return        

    if command.flags["url"]:
        scrape_url(command.flags["url"], wl_processor, command)
    else:
        print("[error] No url provided.")
        print_help(cmd_flags)

def scrape_url(url, wl_processor, command):
    scraper = WordListSiteScraper(
        url, 
        wl_processor, 
        depth=command.flags["depth"],
        leave_domain=not command.flags["no-leave-domain"],
        skip_on_no_connect=command.flags["ignore-unresponsive"],
        user_agent=command.flags["ua"]
    )

def sigint_handler(sig, frame):
    print("Interrupt caught, exiting...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    main(sys.argv)
