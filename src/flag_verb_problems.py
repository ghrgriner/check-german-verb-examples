#   Flag examples for verbs with formatting problems
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

import numpy as np
import pandas as pd
import re

r'''Flag examples for verbs with formatting problems

See ..\README.md for background.
'''

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------
_VERB_PREFIXES = ['verb_present_1s','verb_present_2s','verb_present_3s',
               'verb_pret_1s','verb_subj_ii','verb_imper_s','verb_imper_p',
               'verb_past_part']

VERB_FIELDS = ( _VERB_PREFIXES +
               [ item + '_af1' for item in _VERB_PREFIXES ] +
               [ item + '_af2' for item in _VERB_PREFIXES ] +
               [ item + '_af3' for item in _VERB_PREFIXES ]
              )

# Dictionary for creating candidate strings from past participle. The key is
# the resulting variable name (or prefix) and the value is an anonymous
# function that takes as input the past participle and returns the candidate
# string.
_PAST_PART_DICT = {
    # Past participle + adjective endings
    'pp_e': lambda x: x + 'e',
    'pp_en': lambda x: x + 'en',
    'pp_es': lambda x: x + 'es',
    'pp_er': lambda x: x + 'er',
    'pp_em': lambda x: x + 'em',
    # Forms of 'haben' + past participle
    'habe_pp': lambda x: 'habe ' + x,
    'hast_pp': lambda x: 'hast ' + x,
    'hat_pp': lambda x: 'hat ' + x,
    'habt_pp': lambda x: 'habt ' + x,
    'haben_pp': lambda x: 'haben ' + x,
    'hatte_pp': lambda x: 'hatte ' + x,
    'hattest_pp': lambda x: 'hattest ' + x,
    'hattet_pp': lambda x: 'hattet ' + x,
    'hatten_pp': lambda x: 'hatten ' + x,
    'hätte_pp': lambda x: 'hätte ' + x,
    'hättest_pp': lambda x: 'hättest ' + x,
    'hättet_pp': lambda x: 'hättet ' + x,
    'hätten_pp': lambda x: 'hätten ' + x,
    # Forms of 'werden' + past participle
    'werde_pp': lambda x: 'werde ' + x,
    'wirst_pp': lambda x: 'wirst ' + x,
    'wird_pp': lambda x: 'wird ' + x,
    'werden_pp': lambda x: 'werden ' + x,
    'wurde_pp': lambda x: 'wurde ' + x,
    'wurdest_pp': lambda x: 'wurdest ' + x,
    'wurdet_pp': lambda x: 'wurdet ' + x,
    'wurden_pp': lambda x: 'wurden ' + x,
    'würde_pp': lambda x: 'würde ' + x,
    'würden_pp': lambda x: 'würden ' + x,
    # Forms of 'sein' + past participle
    'bin_pp': lambda x: 'bin ' + x,
    'bist_pp': lambda x: 'bist ' + x,
    'ist_pp': lambda x: 'ist ' + x,
    'seid_pp': lambda x: 'seid ' + x,
    'sind_pp': lambda x: 'sind ' + x,
    'war_pp': lambda x: 'war ' + x,
    'warst_pp': lambda x: 'warst ' + x,
    'wart_pp': lambda x: 'wart ' + x,
    'waren_pp': lambda x: 'waren ' + x,
    'sein_pp': lambda x: 'sein ' + x,
    'wäre_pp': lambda x: 'wäre ' + x,
    'wärest_pp': lambda x: 'wärest ' + x,
    'wäret_pp': lambda x: 'wäret ' + x,
    'wären_pp': lambda x: 'wären ' + x,
    'sei_pp': lambda x: 'sei ' + x,
    'seiest_pp': lambda x: 'seiest ' + x,
    'seiet_pp': lambda x: 'seiet ' + x,
    'seien_pp': lambda x: 'seien ' + x,
    # Catches 50 hits
    # Word order in returned string doesn't matter, so we don't
    # bother putting the past participle in the middle. That is,
    # properly should be 'ist gegessen worden' and not
    # 'ist worden gegessen'
    'ist_w_pp': lambda x: 'ist worden ' + x,
    'sind_w_pp': lambda x: 'sind worden ' + x,
    'sei_w_pp': lambda x: 'sei worden ' + x,
    'seien_w_pp': lambda x: 'seien worden ' + x,
    'war_w_pp': lambda x: 'war worden ' + x,
    'waren_w_pp': lambda x: 'waren worden ' + x,
    'wäre_w_pp': lambda x: 'wäre worden ' + x,
    'wären_w_pp': lambda x: 'wären worden ' + x,
    'sein_w_pp': lambda x: x + ' worden sein',
    # Infinitives using past part (16 hits)
    'pp_zu_h': lambda x: x + ' zu haben',
    'pp_zu_w': lambda x: x + ' zu werden',
    'pp_zu_sein': lambda x: x + ' zu sein',
    'pp_w_zu_sein': lambda x: x + ' worden zu sein',
    'pp_g_zu_sein': lambda x: x + ' gewesen zu sein',
}

PP_VARS = list(_PAST_PART_DICT.keys())

# Like _PAST_PART_DICT, but for verb forms using infinitive
_INF_DICT = {
    # Forms of 'werden' + infinitive
    'werde_inf': lambda x: 'werde ' + x,
    'wirst_inf': lambda x: 'wirst ' + x,
    'wird_inf': lambda x: 'wird ' + x,
    'werdet_inf': lambda x: 'werdet ' + x,
    'werden_inf': lambda x: 'werden ' + x,
    'werdest_inf': lambda x: 'werdest ' + x,
    'würde_inf': lambda x: 'würde ' + x,
    'würdest_inf': lambda x: 'würdest ' + x,
    'würdet_inf': lambda x: 'würdet ' + x,
    'würden_inf': lambda x: 'würden ' + x,
    # Partizip I (present participle) and adjective endings
    'part1': lambda x: x + 'd',
    'part1_e': lambda x: x + 'de',
    'part1_er': lambda x: x + 'der',
    'part1_es': lambda x: x + 'des',
    'part1_en': lambda x: x + 'den',
    'part1_em': lambda x: x + 'dem',
}

INF_VARS = list(_INF_DICT.keys())

# Can distinguish two types of variables with their names. For example,
# `verb_present_1s` (first-person present) might contain 'komme an', and we
# also want to search for 'ankomme'. In contrast `ist_pp` might contain
# 'ist angekommen', but we don't want to search for 'angekommenist'.
# TODO: should also include pp2_vars - pp4_vars
_NON_INVERT_SET = set(INF_VARS + PP_VARS)

_QUOTE_PAT = re.compile("''.*?''")

# Define translation table for deleting certain characters inside pairs of
# single quotes
_TRANSTAB = str.maketrans('','','.,!?„“”"›‹«»:;' + chr(0x2018) + chr(0x2019) +
                          chr(0x201a))

#------------------------------------------------------------------------------
# Private Functions
#------------------------------------------------------------------------------

def _make_italic_set(x):
    inquotes = _QUOTE_PAT.findall(x)
    list_for_set = [ _clean_for_set(y) for y in inquotes ]
    nested_list = [ y.split(' ') for y in list_for_set ]
    list_for_set = []
    for sublist in nested_list:
        for item in sublist:
            list_for_set.append(item)
    the_set = set(list_for_set)
    return the_set - set(['sich','uns','euch','dir','mir','mich','dich'])

def _clean_for_set(x):
    return x.replace("'",'').translate(_TRANSTAB).lower()

def _onefld(italic_set, var, varname):
    if var:
        list_var = var.split(' ')
        check_split_matches = set(list_var) == italic_set
        if check_split_matches:
            return True
        elif len(list_var) == 2 and varname not in _NON_INVERT_SET:
            # TODO: probably better to make a new data frame variable with the
            # appropriate value. For example, this would then allow one to see
            # how often the 'ankommt' form is used vs the 'kommt an'
            return set([ list_var[1] + list_var[0] ]) == italic_set
        else:
            return False
    else:
        return False

def _make_pret_pl(pret_s):
    if not pret_s:
        return ''
    list_s = pret_s.split(' ')
    len_s = len(list_s)
    if len_s not in [1, 2]:
        print(f'WARNING: skipping preterite plural since > 2 tokens {list_s=}')
        return ''
    elif list_s[0].endswith('te'):
        if len_s == 1:
            return list_s[0] + 'n'
        else:
            return list_s[0] + 'n ' + list_s[1]
    else:
        if len_s == 1:
            return list_s[0] + 'en'
        else:
            return list_s[0] + 'en ' + list_s[1]

def _miscflds(headword, pres_3s):
    pres_3s_list = pres_3s.split(' ')
    if pres_3s == '' or len(pres_3s_list) > 2:
        if len(pres_3s_list) > 2:
            print(f'WARNING: skipping infinitive (containing zu) and '
   f'indicative plural since > 2 tokens {pres_3s_list=}')
        return { 'prefix': '', 'inf': '', 'verb_present_3p': '' }
    elif len(pres_3s_list) == 1:
        prefix = ''
        inf = 'zu ' + headword
        vp_3p = ''
        return { 'prefix': prefix, 'inf': inf, 'verb_present_3p': vp_3p}
    else:
        prefix = pres_3s_list[1]
        non_prefix = headword[len(prefix):]
        inf = prefix + 'zu' + non_prefix
        vp_3p = non_prefix + ' ' + prefix
        return { 'prefix': prefix, 'inf': inf, 'verb_present_3p': vp_3p}

def _makepps(x):
    if not x:
        return {}
    else:
        return { key: value(x) for key, value in _PAST_PART_DICT.items() }

def _makeinfs(x):
    if not x:
        return {}
    else:
        return { key: value(x) for key, value in _INF_DICT.items() }

#------------------------------------------------------------------------------
# Public Functions
#------------------------------------------------------------------------------

def flag_verb_problems(df):
    '''Flag example sentences for verbs with formatting problems.

    See `..\\README.md` for backgroud and overview. This function creates
    sets to check for matches with `italic_set` using the following
    candidate strings:

    1. The infinitive itself 

    2. All variables in `VERB_FIELDS`. These are the variables in 
    _VERB_PREFIXES and any alternate forms: 1st/2nd/3rd-person
    singular indicative, 1st-person singular preterite, Konjunktiv II
    1st-person singular, imperative singular and plural, past
    participle. If the verb is separable, these fields are in
    Hauptsatzkonjugation. That is, the prefix is separated and follows the
    stem.

    2. Third person plural indicative. For separable verbs this is  
    the prefix extracted from 3rd person singular indicative (2nd field).
    If there are more than two fields, a warning is printed and the form
    is not used. This is also done for any alternate form provided.

    3. Infinitive as either 'zu [inf]' or '[prefix]zu[stem]' for
    inseparable verbs and separable verbs, respectively. The prefix is
    identified as in (2).

    4. Candidate strings constructed from the past participle and either
    adjective endings or helper verbs. See `_PAST_PART_DICT` for list.

    5. Candidate strings constructed from the infinitve and helper verbs.
    See `_INF_DICT` for list.

    6. The Nebensatzkonjugation of any of the above in (2)-(3) if the
    variable contains a ' '. That is, these are strings of the form
    '[prefix][stem]' instead of '[stem] [prefix]'.

    Careful readers will note that the above does not include all possible
    verb forms. For example, the following are omitted:
    - all 'ihr' forms except the imperative
    - 2nd-person singular preterite 
    - Konjunktiv I forms
    - Konjunktiv II forms, excluding 1st person singular
    - etc.

    Parameters
    ----------
    df : pd.DataFrame
        Data frame, one record per headword per entry per example. The
        variable names should mostly match those output by the PyPI
        `wikwork` package v1.0.0. The variable `example_text` (not from
        that package) should contain the example.

    Returns
    -------
    The input data frame with a number of variables added, the most
    important of which is `needs_review`, which is False if a candidate set
    matched the set of italicized words and True otherwise. Users should
    treat other added variables as experimental, that is, their names may
    change in the future or they may be dropped.
    '''

    out_df = df.copy()
    out_df['sep_verb_YN'] = np.where(
        (~df.headword.str.contains(' ') &
        df.verb_present_3s.str.contains(' ')),'Y','N')
    out_df['italic_set'] = out_df.example_text.map(_make_italic_set)
    out_df['sep_verb_flag'] = False
    res = [ _miscflds(headword, f1) for headword, f1 in
            out_df[['headword','verb_present_3s']].values]

    for var in ['prefix','inf','verb_present_3p']:
        out_df[var] = [ x.get(var, '') for x in res ]

    out_df['past_pl'] = out_df.verb_pret_1s.map(_make_pret_pl)
    # Not too important: catches 15 more hits of the 25-30k examples checked
    out_df['past_pl2'] = out_df.verb_pret_1s_af1.map(_make_pret_pl)
    out_df['past_pl3'] = out_df.verb_pret_1s_af2.map(_make_pret_pl)
    out_df['past_pl4'] = out_df.verb_pret_1s_af3.map(_make_pret_pl)

    pp_res = out_df.verb_past_part.map(_makepps)
    # Also not too important: alternate forms catch 16 more hits
    pp2_res = out_df.verb_past_part_af1.map(_makepps)
    pp3_res = out_df.verb_past_part_af2.map(_makepps)
    pp4_res = out_df.verb_past_part_af3.map(_makepps)
    columns_to_add = {}
    for var in PP_VARS:
        columns_to_add[var] = [ x.get(var, '') for x in pp_res ]
        columns_to_add[var + '_af1' ] = [ x.get(var, '') for x in pp2_res ]
        columns_to_add[var + '_af2' ] = [ x.get(var, '') for x in pp3_res ]
        columns_to_add[var + '_af3' ] = [ x.get(var, '') for x in pp4_res ]
    out_df = pd.concat(
        [out_df, pd.DataFrame(columns_to_add, index=out_df.index)], axis = 1)

    pp2_vars = [ var + '_af1' for var in PP_VARS ]
    pp3_vars = [ var + '_af2' for var in PP_VARS ]
    pp4_vars = [ var + '_af3' for var in PP_VARS ]

    inf_res = out_df.headword.map(_makeinfs)
    for var in INF_VARS:
        out_df[var] = [ x.get(var, '') for x in inf_res ]

    for var in (['headword','inf','verb_present_3p'] +
                ['past_pl','past_pl2','past_pl3','past_pl4'] +
               PP_VARS + pp2_vars + pp3_vars + pp4_vars +
               INF_VARS + VERB_FIELDS):
        out_df['tmp'] = [ _onefld(italic_set, v1, var) for italic_set, v1 in
                          out_df[['italic_set',var]].values ]
        out_df['sep_verb_flag'] = (out_df.tmp | out_df.sep_verb_flag)

    out_df['needs_review'] = ~out_df.sep_verb_flag

    return out_df

