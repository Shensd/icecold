import requests
import re

from bs4 import BeautifulSoup as bsoup

class WordListSiteScraper:
    """Scapes a given website for text and links

    Attributes:
        url (str): url of website to scrape
        wordlist_processor (WordListProcessor): buffer for writing scaped lines
        depth (int): (default=0) depth of links to read from, 0 reads only
            from current page
        leave_domain (bool): (default=False) if depth is greater than 0, choose
            if the scraper is allowed to leave the top domain
        bank_size (int): (default=100) number of text elements to store in 
            memory before processing and writing to disk
        skip_on_no_connect (bool): (default=False) instead of raising an error
            on no site connect, instead ignore the site and move to the next one
    """

    def __init__(self, url, wordlist_processor, depth=0, leave_domain=False, 
        bank_size=100, skip_on_no_connect=False, user_agent="python-requests"):
        self.url = url
        self._wl_processor = wordlist_processor
        self._depth = depth
        self._leave_domain = leave_domain
        self._bank_size = bank_size
        self._skip_unresponsive = skip_on_no_connect
        self._user_agent = user_agent

        self._scrape_page(
            url, 
            wordlist_processor, 
            depth=depth, 
            buffer_size=bank_size, 
            skip_unresponsive=skip_on_no_connect,
            user_agent=user_agent
        )

    def _get_page_content(self, url, user_agent="python-requests"):
        """Grabs the page content at a given url, raises an exception on 
        load error

        Parameters:
            url (str): url to website 
            user_agent (str): user agent to use in requests

        Returns:
            BeautifulSoup: a parsed BeautifulSoup page object
        """

        try:
            headers = {
                'user-agent' : user_agent
            }

            r = requests.get(url, headers=headers)
        except:
            raise Exception("Unable to connect to given url '{}'".format(url))

        return bsoup(r.text, 'html.parser')

    def _get_word_elements(self, page_content, offset=0, amount=100):
        """Get a given number text elements from a given offset

        Parameters:
            page_content (BeautifulSoup): soup object with page content to parse
            offset (int): (default=0) offset from which to read words from
            amount (int): (default=100) number of text element to grab, note: 
                these are not WORDS, but entire ELEMENTS, so a whole 
                <p></p> element will be returned 

        Returns:
            list (str): a list of text elements, stripped from their containers
        """

        def get_element_string(element):
            return " ".join(element.stripped_strings)

        # this feels kinda :thonk:
        text_element_tags = [
            'p', 'h1', 'h2', 'h3', 
            'h4', 'h5', 'h6', 'a',
            'li', 'th', 'td'
        ]

        tag_position = 0
        tag_queue = []
        for tag in text_element_tags:
            # get all text elements at current tag
            tags = page_content.find_all(tag)
            # filter only for those with inner text
            tags = [ get_element_string(tag) for tag in tags if tag.string != "" ]
            tags_size = len(tags)

            # if out offset is within the range of out current set of tags, 
            # add the amount needed to the queue
            if offset >= tag_position and offset < tag_position + tags_size:
                collection_offset = offset - (tag_position)
                collection_cap = collection_offset + amount

                # this will read from the offset up to max the amount wanted
                tag_queue.extend(
                    tags[collection_offset : collection_cap]
                )

                # if we still need more tags, offset the offset so it will
                # still read in more at the next round
                tag_queue_size = len(tag_queue) 
                if tag_queue_size < amount:
                    offset += tag_queue_size
                else:
                    return tag_queue
            
            tag_position += tags_size

        return tag_queue

    def _is_in_domain(self, parent, child):
        """Returns if a given child url is within the same domain as the parent

        Parameters:
            parent (str): url of parent domain
            child (str): url of child domain to test

        Returns:
            bool: True if inside domain, otherwise False
        """
        
        def get_domain(url):
            # grabs any url with structure "someproto://example.com"
            regex_proto = re.search("^(.*[://])+", url)
            if regex_proto:
                url = url[regex_proto.end():]
            return url.split("/")[0]

        def get_top_domain(url):
            return url.split(".")[0:1]

        return get_top_domain(parent) == get_top_domain(child)

    def _fix_url(self, parent, child):
        """If a given url is a sub url of a parent page, append to parent and 
        return

        Paremeters:
            parent (str): parent url to append to, if necessary
            child (str): child domain to fix in context of parent
        """

        if child.startswith("/"):
            return parent + child
        return child

    def _get_page_links(self, parent_url, page_content, leave_domain=False):
        """Grabs the links from a given page, filtering based on parameters

        Paramters:
            parent_url (str): url of the parent page, used for domain encapsulation
                checks
            page_content (BeautifulSoup): a BeautifulSoup object with the page 
                content
            leave_domain (bool): (default=False) set to true if you wish to grab
                links outside of the current top level domain
        """
        a_elements = page_content.find_all('a')

        def is_id_link(element):
            return element.startswith("#")

        # grab links from a elements
        links = [ element["href"] for element in a_elements if element.get("href") ]

        # remove id links and fix sub-links
        links = [ self._fix_url(parent_url, link) for link in links if not is_id_link(link) ]

        # remove links not in domain if chosen
        if not leave_domain:
            links = [ link for link in links if self._is_in_domain(parent_url, link) ]

        return links
    
    def _scrape_page(self, url, wordlist_buffer, depth=0, buffer_size=100, 
        skip_unresponsive=False, user_agent="python-requests"):
        """Scape a page at a given url for its content and links, reading out
            to the given wordlist processor as it goes

        Parameters:
            url (str): url of page to scrape content from
            wordlist_buffer (WordListProcessor): a wordlist processor to read
                out from as the scraper works through the page
            depth (int): (default=0) how many levels deep to read from the page, 
                if set to 0 then no link scraping is performed, otherwise links 
                and scraped from the page and the scraped themselves recursively
            buffer_size (int): (default=100) number of text elements to read 
                from the page before passing them to the wordlist processor to 
                be processed and written to the output location
            skip_unresponsive (bool): (default=False) if a site is unresponsive,
                skip scraping the site instead of throwing an exception
            user_agent (str): user agent to use when making requests
        """
        try:
            content = self._get_page_content(url, user_agent=user_agent)
        except:
            if skip_unresponsive:
                return
            else:
                print(
                    "[error] Unable to connect to url {}, to ignore unresponsive urls use --ignore-unresponsive".format(url)
                )
                exit(0)

        # read words from the page until 
        read_position = 0
        words = self._get_word_elements(content, offset=0, amount=buffer_size)
        while len(words) > 0:
            # read the set of words to the wordlist buffer for processing
            wordlist_buffer.process(words)

            # offset read position with amount of words and read next set
            read_position += len(words)
            words = self._get_word_elements(content, offset=read_position, amount=buffer_size)

        # only read links from page if the depth is greater than 0, this process
        # is actually vaugely expensive 
        if depth > 0:
            links = self._get_page_links(url, content, leave_domain=self._leave_domain)

            # recursive scrap links on pages
            for link in links:
                depth -= 1
                self._scrape_page(
                    link, 
                    wordlist_buffer, 
                    depth=depth, 
                    buffer_size=buffer_size,
                    skip_unresponsive=skip_unresponsive,
                    user_agent=user_agent
                )