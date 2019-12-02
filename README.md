<p align="center">
    <img alt="icecold" src="./logo.png" height="175">
</p>

<h1 align="center">
icecold
</h1>
<p  align="center">
context aware wordlist generation
</p>

### What is This?

Icecold is a tool designed to generate wordlists based on websites, it does this by scraping words and combining and modifying them into forms that are commonly used as passwords.

This is a very CTF-esque tool, as a common CTF category is creating passwords based off a specific theme or topic. It still has applications in real world password recovery, it could have been used that time you found a Raspberry Pi in your closet and you were _pretty sure_ the password was Love Live themed.

Icecold does not take duplicates into account in order to keep ram usage and disk read/write low, if this is of great concern (enough to take the cost of weaker wordlist generation), then [CeWL](https://github.com/digininja/CeWL) is another option. 

### Output Examples

The command `icecold.py https://google.com -d 0 -C "?" --no-smush` will give output that looks similar to the following 

```
...
savings
are
now
live
the
google
store
cyber?monday
monday?savings
savings?are
are?now
now?live
live?the
the?google
cyber?monday?savings
monday?savings?are
savings?are?now
are?now?live
now?live?the
live?the?google
...
```

Icecold has many command line flags to customize the output wordlist. It should be noted that icecold works best when use in tandem with other wordlist generation tools, such as [hashcat](https://hashcat.net/hashcat/) and [John the Ripper](https://www.openwall.com/john/).


### Install

```
git clone https://github.com/Shensd/icecold
pip3 install -r requirements.txt
```

This program is inteded to be used with python3, and compatability with python2 was not taken into account during development.

### Usage

```
usage: icecold.py [url] [options...]
    
  -u, --url	Base url to scrape
  -U, --url-file	Use a file with a list of urls, with one on each line
  -o, --output	Output file location to dump wordlist (default stdout)
  -m, --min-word-len	Minimum word length to accept (default 3)
  -M, --max-word-len	Maximum word length to accept (default 15)
  -c, --chain-len	Maximum length to make word chains (default 3)
  -h, --help	Display this help page
      --ignore-unresponsive	Do not halt program when a website doesn't respond, skip website instead
  -d, --depth	How many links deep to spider pages (default 1)
      --no-leave-domain	Disallow leaving domain while spidering
      --ua	Set the user agent used in requests
  -C, --charset	Charset to use when making word chains, (default '_-')
      --words-only	Do not make word chains, just print single words (macro for -c 1)
      --no-smush	Do not create word chains that only push words together, only use connecting characters
```

###### This project is licensed under the MIT Open Source license, see `LICENSE` for more information