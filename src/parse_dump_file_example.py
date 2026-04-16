#   Example program to parse (German) Wiktionary dump file
#   Copyright (C) 2026 Ray Griner (rgriner_fwd@outlook.com)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

'''Example program to parse (German) Wiktionary dump file

This uses the Python libraries bz2 and xml.etree.ElementTree to extract
pages from the zipped XML file. The wikitext on the pages is then parsed
using the `wikwork` Python package. In this example, pages that are
adjectives are selected, parsed and exported. For other pages, some
simple statistics are collected and printed to stdout. Users that want to
process all pages might have to be more careful about memory (in that all
the `GermanWord` objects are stored in a single list before being written
to a text file).

While there are cautionary tales online regarding the time it takes to
parse Wikipedia dump files, the Wiktionaries are smaller. This program
runs on a low-end laptop in two minutes.

It would probably take 4-5 hours to download the same number of
adjectives using the `wikwork` package. However, `wikwork` is still
useful to get the updated page information for fixes a user might make
based on this dump file. That is, a reasonable workflow is: identify
fixes using the dump file, make the fixes, get the fixes using `wikwork`
and check them.

Trademark Notice
----------------
Wiktionary and Wikipedia are trademarks of the Wikimedia Foundation and
are used with the permission of the Wikimedia Foundation. We are not
endorsed by or affiliated with the Wikimedia Foundation.
'''

import bz2
import xml.etree.ElementTree as ET
from wikwork import german, wrapper

from collections import Counter

# This can be extracted programmatically, but we just hardcode it
XMLNS = '{http://www.mediawiki.org/xml/export-0.11/}'
# This file isn't uploaded to the repository.
INPUT_FILE = 'large/dewiktionary-20260401-pages-articles-multistream.xml.bz2'
MAX_PAGES = None # int or None (no maximum)

def fetch_from_xml_dump(word, elem):
    revision_elem = elem.find(f'{XMLNS}revision')
    word.revision = int(revision_elem.find(f'{XMLNS}id').text)
    word.timestamp = revision_elem.find(f'{XMLNS}timestamp').text
    word.wikitext = revision_elem.find(f'{XMLNS}text').text
    # In wikwork v1.0.0, the below is a private function, but in a future
    # wikwork version we will likely add `fetch_from_xml_dump` as a method
    # to GermanWord
    word._parse_wikitext()

def process_bz2_xml_dump(filename):
    page_counter = 0
    main_page_counter = 0
    german_entry_counter = 0
    verb_counter = 0
    noun_counter = 0
    adj_counter = 0
    oth_counter = 0
    example_counter = 0
    other_entry_list = []
    adjectives = []

    with bz2.open(filename, "rb") as f:
        context = ET.iterparse(f, events=("end",))
        
        _, root = next(context) 
        
        for event, elem in context:
            if event == 'end' and elem.tag == f'{XMLNS}page':
                page_counter = page_counter + 1
                title = elem.find(f'{XMLNS}title').text
                #print(title)
                
                if page_counter % 10000 == 0:
                    print(f'{page_counter=}')
                if MAX_PAGES is not None:
                    if page_counter == MAX_PAGES:
                        break

                # limit to pages in the main namespace. That is, the pages for
                # words and their definitions. Omits pages like
                # 'Hilfe:Beispiele', etc.
                if ':' not in title:
                    main_page_counter = main_page_counter + 1
                    gword = german.GermanWord(headword=title, lang_code='de')
                    fetch_from_xml_dump(gword, elem)
                    if gword.entries:
                        german_entry_counter = german_entry_counter + 1
                        has_verb = any('|Verb|' in entry.entry_line for entry in gword.entries)
                        if has_verb:
                            verb_counter = verb_counter + 1

                        has_noun = any('|Substantiv|' in entry.entry_line for entry in gword.entries)
                        if has_noun:
                            noun_counter = noun_counter + 1

                        has_adj = any('|Adjektiv|' in entry.entry_line for entry in gword.entries)
                        if has_adj:
                            adj_counter = adj_counter + 1
                            adjectives.append(gword)
                        if not (has_verb or has_noun or has_adj):
                            oth_counter = oth_counter + 1
                            for entry in gword.entries:
                                other_entry_list.append(entry.entry_line)
                    #print(gword)

                # Clear element once it's processed
                elem.clear()
                # Root will keep references to all of its already-cleared
                # children until it is also cleared
                root.clear() 

    print(f'\n{page_counter=}')
    print(f'{main_page_counter=}')
    print(f'{german_entry_counter=}')
    print(f'{noun_counter=}')
    print(f'{verb_counter=}')
    print(f'{adj_counter=}')
    print(f'{oth_counter=}\n')

    counts = Counter(other_entry_list)
    for item, count in counts.most_common():
        print(f"{item}: {count}")

    wrapper.write_output_files(adjectives,
                       output_all_entries=True,
                       output_words_filename='adj_output.txt',
                       output_audios_filename=None,
                       output_wikitext_filename=None,
                       )

process_bz2_xml_dump(INPUT_FILE)

