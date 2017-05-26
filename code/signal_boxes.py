""" Signal box prefix codes """

import os
import string

import pandas as pd
import requests

from utilities import cdd_rc_dat, load_pickle, save_pickle, get_last_updated_date, parse_table


#
def cdd_sig_box(*directories):
    path = cdd_rc_dat("Other assets", "Signal boxes")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# Scrape signal box prefix codes for the given 'key word' (e.g. a starting letter) ===================================
def scrape_signal_box_prefix_codes(key_word, update=False):
    """
    :param key_word: [str]
    :param update: [bool]
    :return: 
    """
    path_to_file = cdd_sig_box("A-Z", key_word.title() + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        signal_box_prefix_codes = load_pickle(path_to_file)
    else:
        url = 'http://www.railwaycodes.org.uk/signal/signal_boxes{}.shtm'.format(key_word)
        last_updated_date = get_last_updated_date(url)
        source = requests.get(url)
        try:
            # Get table data and its column names
            records, header = parse_table(source, parser='lxml')
            header = [h.replace('Signal box', 'Signal Box') for h in header]
            # Create a DataFrame of the requested table
            data = pd.DataFrame([[x.strip('\xa0') for x in i] for i in records], columns=header)
        except IndexError:
            data = None
            print("No data is available for the key word '{}'.".format(key_word))

        sig_keys = [s + key_word.title() for s in ('Signal_boxes_', 'Last_updated_date_')]
        signal_box_prefix_codes = dict(zip(sig_keys, [data, last_updated_date]))
        save_pickle(signal_box_prefix_codes, path_to_file)

    return signal_box_prefix_codes


# Get all of the available signal box prefix codes ===================================================================
def get_signal_box_prefix_codes(update=False):
    """
    :param update: [bool]
    :return: 
    """
    path_to_file = cdd_sig_box("Signal-box-prefix-codes.pickle")
    if os.path.isfile(path_to_file) and not update:
        signal_box_prefix_codes = load_pickle(path_to_file)
    else:
        # Get every data table
        data = [scrape_signal_box_prefix_codes(i, update) for i in string.ascii_lowercase]

        # Select DataFrames only
        signal_boxes_data = (item['Signal_boxes_{}'.format(x)] for item, x in zip(data, string.ascii_uppercase))
        signal_boxes_data_table = pd.concat(signal_boxes_data, axis=0, ignore_index=True)

        # Get the latest updated date
        last_updated_dates = (item['Last_updated_date_{}'.format(x)] for item, x in zip(data, string.ascii_uppercase))
        last_updated_date = max(d for d in last_updated_dates if d is not None)

        # Create a dict to include all information
        signal_box_prefix_codes = {'Signal_boxes': signal_boxes_data_table, 'Latest_updated_date': last_updated_date}

        save_pickle(signal_box_prefix_codes, path_to_file)

    return signal_box_prefix_codes
