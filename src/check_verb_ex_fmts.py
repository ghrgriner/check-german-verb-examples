#------------------------------------------------------------------------------
# File: check_verb_ex_fmts.py
# Desc: Process German Wiktionary examples and make flag for bad formatting
#------------------------------------------------------------------------------

'''Process German Wiktionary examples and make flag for bad formatting

In particular, this is meant to check verbs. See ../README.md for
background.

This is an example program to illustrate processing of the data before
`flag_verb_problems` is called. However, it's not a working example file
in the sense that we have not uploaded an input file in the repository.
Users will have to create their own by running `wikwork` or create
similar output.

In this example, we process separable and inseparable in separate calls to
`create_example_subset`. We also process examples that were probably
authored by Wiktionary authors separately from examples that are
quotations. (The previous sentence is qualified with 'probably' because
sometimes quotations in Wiktionary don't have the '<ref>' tag that we use
in our filter.)

We find it useful to review quotations separately because they are more
likely to use spelling variants than author-created examples.

In the example below, we don't review all verbs in the input file. For
example, examples where `verb_template_parsed == False` are never selected
by the `make_eligible_flag` function in these examples, because the result
for these is that `needs_review` is always True.

Note that our manual review files are saved without a row of column
headers to facilitate loading into our flashcard software, which doesn't
support them in this manner. Users who want such headers should modify
the appropriate `to_csv` parameter.
'''

import pandas as pd
import numpy as np
import csv
import re

import sys
sys.path.append('/home/yar/pywork/check_german_verb_examples/src')

from flag_verb_problems import flag_verb_problems

#------------------------------------------------------------------------------
# trennbar: filter by sep_verb_YN == 'Y' and needs_review == 'Y'. This might
#   have excluded a few too many, as there are a few separable verbs where
#   sep_verb_YN == 'N' (e.g., impersonal verbs where the 3rd person present
#   isn't in the verb template)
# untrennbar: filter by sep_verb_YN != 'Y' and `verb_template_parsed == True
#   and needs_review == 'Y'.
#   A separate review can then be done for `verb_template_parsed == False`, if
#   desired. These will all have needs_review == True, but there's currently
#   only a handful.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Parameters / functions for user modification
#------------------------------------------------------------------------------
OUTDIR = 'results_verb_review'

UNTR_FROM_WIKT_FILE = '/path/to/wikwork/output/file'
UNTR_ALL_REF_OUTPUT_FILE = f'{OUTDIR}/untrennbar_examples_refs.txt'
UNTR_MANREV_REF_OUTPUT_FILE = f'{OUTDIR}/load_flashcard_un.txt'

def untr_make_eligible_flag(df):
    return df.prob_user_example

def untr_make_manrev(df):
    return df[ (df.needs_review) & (df.sep_verb_YN == 'N')
                 & (df.verb_template_parsed == 'True')
                 & (df.entry_line.str.contains(r'\|Verb\|'))]

UNTR_ALL_USER_OUTPUT_FILE = f'{OUTDIR}/untrennbar_examples.txt'
UNTR_MANREV_USER_OUTPUT_FILE = f'{OUTDIR}/load_flashcard_user_un.txt'

TR_FROM_WIKT_FILE = '/home/yar/wikwork/de_vocab/trennbar_output.txt'
TR_ALL_REF_OUTPUT_FILE = f'{OUTDIR}/trennbar_examples_refs.txt'
TR_MANREV_REF_OUTPUT_FILE = f'{OUTDIR}/load_flashcard.txt'
TR_ALL_USER_OUTPUT_FILE = f'{OUTDIR}/trennbar_examples.txt'
TR_MANREV_USER_OUTPUT_FILE = f'{OUTDIR}/load_flashcard_user.txt'

def tr_make_manrev(df):
    return df[ (df.needs_review) & (df.sep_verb_YN == 'Y')]

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------

REF_PAT = re.compile("<ref>.*?</ref>")

def _braces_to_class(x, html_class) -> str:
    """Replace braces with HTML span statement with specified `class`.
    """
    return x.replace('{',f'<span class={html_class}>').replace('}','</span>')

def _clean_example(x):
    x = x.replace('; ==== {{Übersetzungen}} ====','')
    if '{{Beispiele fehlen' in x or x in ['[1] ', ' ', '\t']:
        x = ''
    x = re.sub(REF_PAT, '', x)

    # If the field contains a tab, will need to (1) be fixed on Wiktionary and
    # the input file redownloaded or (2) manually handled in a statement above
    # or (3) elig_example updated so that fields with tabs are not eligible
    if '\t' in x:
        raise ValueError(f'tab in: {x=}')
    return x

# TODO: rework this. I reused some code from internal examples where I am
# careful not to include braces. Later, the braces are converted to CSS tags.
# But, these examples sometimes do include braces (e.g., wikitext templates).
# So, it would be better to go straight from quote pairs to CSS.
def _single_quote_pairs_to_braces(x):
    if "'''" in x:
        print(f"WARNING: three single quotes in: {x}")
    is_start = True
    while "''" in x:
        if is_start:
            x = x.replace("''", '{', count=1)
        else:
            x = x.replace("''", '}', count=1)
        is_start = not is_start
    if not is_start:
        print(f"WARNING: unclosed double quotes in: {x}")
    return x

def _ex_to_raw_list(x):
    if not x:
        return []
    else:
        x_list = x.split('; :[')

        y_list = []
        for pos, x in enumerate(x_list):
            if pos == 0:
                # remove leading character, which should be ':'
                y_list.append(x[1:])
            else:
                # `split` above removed the '[', so add it back
                y_list.append('[' + x)
        return y_list

def _load_wikt_data(from_wikt_file, make_eligible_flag):
    wikt_df = pd.read_csv(from_wikt_file, engine='python',
        sep='\t', na_filter=False, quoting=csv.QUOTE_MINIMAL)
    wikt_df['example_raw_text'] = wikt_df.examples.map(_ex_to_raw_list)

    ex_df = wikt_df.explode('example_raw_text')
    ex_df['example_raw_text'] = ex_df.example_raw_text.fillna('')
    ex_df['prob_user_example'] = ( (ex_df.example_raw_text != '') &
             ~( (~ex_df.example_raw_text.str.contains('<ref')) &
                (~ex_df.example_raw_text.str.contains('Projekt Gutenberg'))
              )
                                 )
    ex_df['eligible'] = make_eligible_flag(ex_df)

    elig_df = ex_df[ ex_df.eligible ].copy()
    elig_df['example_text'] = elig_df.example_raw_text.map(_clean_example)

    elig_df['ex_seqno'] = elig_df.groupby(
        ['headword','entry_no']).cumcount() + 1

    final_df = elig_df[elig_df.example_text != ''].copy()

    final_df['keep'] = ''

    return final_df

def create_example_subset(from_wikt_file,
                       make_eligible_flag,
                       make_manrev_frame,
                       all_output_file,
                       manrev_output_file):
    '''Flag example sentences for verbs with formatting problems.

    Parameters
    ----------
    from_wikt_file : str
        Name of the text file with data extracted from Wiktionary, one
        row per headword per entry. The expected variable names match
        those output by the `wikwork` Python package.
    make_eligible_flag : function(pd.DataFrame) -> pd.Series
        A function that takes a data frame as input (generated by reading
        the `from_wikt_file` file and reformatting the data frame so that
        every example is its own row) and returns a boolean series whether
        the example is eligible for review. This series is then used to
        filter the input data.
    make_manrev_frame : function(pd.DataFrame) -> pd.DataFrame
        A function that takes a data frame as input and returns a data
        frame that is a subset on the input frame. The returned data frame
        are the records to be manually reviewed.
    all_output_file : str
        File name of a tab-delimited output file. This contains the data
        frame generated by `make_eligible_flag`.
    manrev_output_file : str
        File name of a tab-delimited output file. This contains the data
        frame generated by `make_manrev_frame`.
    
    Returns 
    ------- 
    None
    '''
    final_set = _load_wikt_data(from_wikt_file, make_eligible_flag)

    final_set = final_set.sort_values(['headword','entry_no','ex_seqno'])
    final_set = flag_verb_problems(final_set)

    print(final_set.needs_review.value_counts())

    final_set = final_set[['headword','revision','entry_no','keep','ex_seqno',
       'example_text','sep_verb_YN','needs_review',
       'entry_line','verb_template_present','verb_template_parsed',
                     ]]

    final_set.to_csv(all_output_file, sep='\t', quoting=csv.QUOTE_MINIMAL,
                 index=False)

    final_set['fmt_example'] = final_set.example_text.map(
        _single_quote_pairs_to_braces)
    final_set['css_example'] = final_set.fmt_example.map(
        lambda x: _braces_to_class(x, 'highlight'))
    final_set = final_set.reset_index()

    manrev_set = make_manrev_frame(final_set)

    manrev_set[['index','headword','css_example']].to_csv(manrev_output_file,
            sep='\t', quoting=csv.QUOTE_NONE, index=False, header=False)

#------------------------------------------------------------------------------
# Main Entry Point
#------------------------------------------------------------------------------
if __name__ == '__main__':
    create_example_subset(UNTR_FROM_WIKT_FILE,
                   untr_make_eligible_flag, untr_make_manrev,
                   UNTR_ALL_REF_OUTPUT_FILE, UNTR_MANREV_REF_OUTPUT_FILE)

    create_example_subset(UNTR_FROM_WIKT_FILE,
                   lambda df: ~df.prob_user_example,
                   untr_make_manrev,
                   UNTR_ALL_USER_OUTPUT_FILE, UNTR_MANREV_USER_OUTPUT_FILE)

    create_example_subset(TR_FROM_WIKT_FILE,
                   lambda df: df.prob_user_example, tr_make_manrev,
                   TR_ALL_REF_OUTPUT_FILE, TR_MANREV_REF_OUTPUT_FILE)

    create_example_subset(TR_FROM_WIKT_FILE,
                   lambda df: ~df.prob_user_example, tr_make_manrev,
                   TR_ALL_USER_OUTPUT_FILE, TR_MANREV_USER_OUTPUT_FILE)
