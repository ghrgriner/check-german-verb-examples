# Trademark Notice

Wiktionary is a trademark of the Wikimedia Foundation and is used with the
permission of the Wikimedia Foundation. We are not endorsed by or
affiliated with the Wikimedia Foundation.

# Introduction

This package is designed to read example sentences for verbs from the
German-lanaguage Wiktionary™ and flag those with incorrect formatting.
The standard on this Wiktionary is to highlight (italicize) the headword
in the example by enclosing it in pairs of single quotes (''headword'').
However, this is not always done correctly by Wiktionary authors. With
this program, a Wiktionary editor interested in checking and cleaning
the examples can save time by limiting their review to only the sentences
flagged by this package.

The package works by creating the set of italicized words in the example
(excluding reflexive pronouns) and comparing it to sets from a number of
space-delimited strings. The order of the words in these candidate string
doesn't matter. The starting point for these candidate strings is the
''{{Deutsch Verb Übersicht}}' template on the word's Wiktionary page. For
example, this template typically has the first, second, and third person
singular indicative forms, the first-person singular for the preterite and
Konjunktiv II forms, singular and plural imperatives, the past participle,
and the helper verb.

The `flag_verb_problems` module provides the `flag_verb_problems` function
which returns a dataset that is the input data set with a number of
variables added, the most important of which is `needs_review`, which is
False if a candidate set matched the set of italicized words. Users should
treat other added variables as experimental, that is, their names may
change in the future or they may be dropped.

Lastly, the `check_verb_ex_fmts.py` is an example program with a main
entry point. Users can update the Parameter section and then execute the
file.

# Complications

The task is complicated by the following:

1. (Wiktionary) authors may or may not have highlighted reflexive particles
   and helper verbs in the example sentence.
2. Some verb forms are easily extractable from a headword's page, but this
   is not true for all verb forms.
3. Alternate forms may exist for a verb. For example, 'wenden' has the
   first person preterite singular forms 'wandte' and 'wendete'.
4. Separable verbs may exist in the sentence as separated or attached to
   the verb base.
5. Authors may have used the headword more than once in the example
   sentence and (correctly) highlighted each use.
6. Authors may have used italics for purposes other than highlighting the
   headword.
7. Examples that are quotations might use out-of-date spelling. These
   forms are often not captured in the template with the candidate strings.
8. Examples sometimes contain dialectical variants. Again, these variants
   might be mentioned in the 'Alternative Schreibwesen' section of the
   entry and not in the template from which the candidate strings are
   extracted.
9. Examples might highlight a key prepositional or noun complement in
   addition to the verb form. When reviewing the output, I left such words
   highlighted as long as the definition is limited to that singular
   complement (e.g., see the first example of [abhängen](https://de.wiktionary.org/w/index.php?title=abh%C3%A4ngen&oldid=10540245)).
   It's probably reasonable to highlight such complements, but we note that
   if this was done consistently throughout wiki, we suspect a much larger
   number of examples would be flagged for manual review by our program.
10. The examples sometimes are for a separable verb form even when the
   candidate strings from the verb template indicate an inseparable form
   or vice-versa. 

Generally, this package handles items (1)-(4) above for the most important
cases. See the docstring of `flag_verb_problems` for details. Items (5), (6),
and (8) are not addressed by the package and we ignored such cases when
they were flagged. For (7), one of the benefits of reviewing quotations
separately from author-created examples is so that plausible spelling
variants can simply be ignored in quotations. We do, however, think it's
reasonable to modify author-created examples to use modern spelling.
For (10), when the page has both forms, it's sensible to move the
example to the correct location. However, we did not bother creating a
new separable entry on the page if it didn't already exist.

# Dependencies

The package uses numpy and pandas.

The package assumes the input example data and starting candidate strings
are in a file whose structure is like that of the `wikwork` Python package v1.0.0
(written by the same author of this repository). However, if users extract the
data and format it appropriately some other way, the `wikwork`
package is not needed. We did provide an example download program that uses
`wikwork` for interested users.

See `wikwork` package documentation for its dependencies.

# Program-Generated Warning Messages

The `check_verb_ex_fmts.py` example program is a bit noisy. Running the on all verbs will
generate two or three pages of warnings. These warnings are of four types:

- The example text contains three single quotes.
- The example text contains an 'unclosed' pair of single quotes.
- The third person indicative singular has more than 2 tokens. In such
  cases, the third person plural indicative and the infinitive of the form
  `[prefix]zu[stem]` are not created (although we probably could
  have done so with a little effort).
- The third person preterite singular has more than 2 tokens. In such
  cases, the third person plural is not created.

The warning system is also a bit crude (i.e. simply `print` statements).
Users are encouraged to comment these out if they become annoyed and/or convert
to the `logging` package to more easily manage the output.

