#   Example program to extract data using `wikwork` package
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

'''Example program to extract data using `wikwork` package

`wikwork` is a Python package written by the author of this package that
extracts data from Wiktionary™ using its REST APIs and parses the pages
for selected languages, including German.

Users will probably want to obtain a MediaWiki™ access token. The program
below assumes this token is stored in the MEDIAWIKI_TOKEN environment
variable. We believe anonymous access without a token is possible, but
the permitted calls per hour is lower and users will have to adjust the
`sleep_time` parameter below accordingly.

There is a `input_subdir_fn` parameter to the `IOOptions` constructor
that may help if a large number of words are downloaded, since large
numbers of files in directories can cause performance problems. However,
we haven't been using this.

Trademark Notice
----------------
Wiktionary and MediaWiki are trademarks of the Wikimedia Foundation and
are used with the permission of the Wikimedia Foundation. We are not
endorsed by or affiliated with the Wikimedia Foundation.
'''

import logging

from wikwork import wrapper, page_media, io_options
import re
import os

logger = logging.getLogger('wikwork')
#logger.setLevel(logging.INFO)
logger.setLevel(logging.WARN)

fh = logging.FileHandler('download_wikwork_example.log', mode='w')
ch = logging.StreamHandler()

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

#------------------------------------------------------------------------------
# Parameters
#------------------------------------------------------------------------------
# Should a text file with a single column of headwords.  The column header
# should match that specifid in `input_words_column_name` below.
INPUT_FILE = 'test_trennbar_input.txt'
OUTPUT_FILE = ''
# The email is because the MediaWiki API documentation says users should
# include some way of contacting them in the header of the API calls.
USER_EMAIL = '----PUT-EMAIL-ADDRESS-HERE----' 
# Top-level directory of the package cache. This directory and the necessary
# subdirectories will be created by the `IOOptions` constructor below if it
# doesn't exist. It's useful to have a second download program that reads 
# from a different input file where cache_mode = CacheMode.WRITE_ONLY.
# This will not read from the cache, resulting in the page being redownloaded.
# So a workflow could be: you download 100s of words with this program, find
# some examples and fix them on Wiktionary, redownload only the words fixed
# other program, and then rerun this program to get the full list, now with
# fixes included.
CACHE_LOCATION = 'cache'
lang_code = 'de'

#------------------------------------------------------------------------------
# Main entry point
#------------------------------------------------------------------------------

access_token = os.environ['MEDIAWIKI_TOKEN']

#    'Authorization': f'Bearer {access_token}',
my_headers = {
    'Authorization': f'Bearer {access_token}',
    'User-Agent': f'(wikwork package) (USER_EMAIL)',
}

io_opts = io_options.IOOptions(
    output_dir=CACHE_LOCATION,
    project='Wiktionary',
    cache_mode = io_options.CacheMode.READ_AND_WRITE,
    sleep_time = 0.8,
    headers=my_headers)

res = wrapper.words_wrapper(
    input_words_filename=INPUT_FILE,
    headword_lang_code=lang_code,
    audio_html_lang_code='de',
    io_options=io_opts,
    input_words_column_name='Word',
    fetch_word_page=True,
    output_all_entries=True,
    output_words_filename=OUTPUT_FILE,
    )
