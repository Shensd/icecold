import sys
from args.cmdargparser import CmdArgParser
from scraper.wordlist_site_scraper import WordListSiteScraper
from output.outputcontroller import OutputController
from wordlist.wordlistprocessor import WordListProcessor

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

    command = CmdArgParser(arg_string)
    out = OutputController("", standard_out=True)
    wl_processor = WordListProcessor(out)

    if "url" in command.flags:
        scraper = WordListSiteScraper(command.flags["url"], wl_processor, depth=1)

if __name__ == "__main__":
    main(sys.argv)