import sys
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

def main(argv):
    arg_string = " ".join(argv)

    cmd_flags = [
        CmdFlag(
            "url",
            "Base url to scrape",
            short_name="u",
            accepted_type="str"
        ),
        CmdFlag(
            "min-word-len",
            "Minimum word length to accept (default 3)",
            short_name="m",
            accepted_type="int"
        ),
        CmdFlag(
            "max-word-len",
            "Maximum word length to accept (default 15)",
            short_name="M",
            accepted_type="int"
        ),
        CmdFlag(
            "chain-len".
            "Maximum length to make word chains (default 3)",
            short_name="c",
            accepted_type="int"
        )
    ]

    default_flags = [
        CmdDefault(
            "url",
            "str"
        )
    ]

    command = CmdArgParser(arg_string, cmd_flags, default_flags=default_flags)
    out = OutputController("", standard_out=True)
    wl_processor = WordListProcessor(out, charset="-_")

    if command.default_flags[0].value:
        scraper = WordListSiteScraper(command.default_flags[0].value, wl_processor, depth=1)

if __name__ == "__main__":
    main(sys.argv)
