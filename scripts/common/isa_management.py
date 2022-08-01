# Helper functions to manage the conversion of data from .isa CSV files into
#   data structures to be used in scripts

import csv

# Take in the input string detailing the ISA, parse it and grab the needed dictionaries.
# Also take in an optional keys argument which:
#   - can be left empty to indicate that we want all keys and their associated values
#   to be stored in the sub dictionary.
#   - if is a single string, returns a dictionary with only the value associated with
#   the key given by the string in it.
#   - if is a list of strings, returns a dictionary where each instruction key has a
#   sub dictionary where we can access multiple keys from the CSV file from.
def check_isa(isa, keys=None, reg=False):
    all_instrs = {}
    reg_dict = {}

    #           ----- Parsing the XLEN value -----
    XLEN = isa[2:4]
    assert XLEN in ["32", "64"], "XLEN can only be 32 or 64"

    # Include the instructions from the isa of that word length
    all_instrs.update(convert_csv_to_dict("rv"+str(XLEN), keys))
    
    #      ----- Parsing the remaining characters -----
    # Dictionary to track what's been included
    history = { 'm' : False,
                'a' : False,
                'f' : False,
                'd' : False,
                'g' : False,
                'c' : False,
                'p' : False,
                'v' : False }

    # Index 4 - Either 'I' or 'E' or 'G'
    # TODO : Verify that there is no difference between I and E in the 
    #   instructions available.
    # G = IMAFD + Zifencei

    char_four = isa[4].lower()
    assert char_four in ["i", "e", "g"], \
        "The 5th character can only be either i, e or g"

    # Check for 'g' which indicates the multiple extensions need to be included
    if isa[4].lower() == 'i':
        reg_dict.update(convert_reg("rv"+XLEN+"i"))
    elif isa[4].lower() == "e":
        reg_dict.update(convert_reg("rv"+XLEN+"e"))
    elif isa[4].lower() == 'g':
        pass
        # all_instrs.update(convert_csv_to_dict('m', keys))
        # history['m'] = True

        # all_instrs.update(convert_csv_to_dict('a', keys))
        # history['a'] = True

        # all_instrs.update(convert_csv_to_dict('f', keys))
        # history['f'] = True
        # reg_dict.update(convert_reg("f"))

        # all_instrs.update(convert_csv_to_dict('d', keys))
        # history['d'] = True
 
    # Iterate through the remaining characters
    for index in range(5, len(isa)):
        extension = isa[index].lower() # Force lower-case
        # Possible base extensions : MAFCPV
        if (history[extension]): # Extension already detected, ignore
            continue
        else: # New extension, check for combinations
            # Add current extension to dictionary and update history
            all_instrs.update(convert_csv_to_dict(extension, keys))
            history[extension] = True

            # -- History checking, dependent on the isa string having the
            #   instruction in order --

            # Specific cases for instruction inclusion
            if extension == 'd':
                pass
                # d implies the inclusion of f which may or may not be stated
                # all_instrs.update(convert_csv_to_dict('f', keys))
                # history['f'] = True
            elif extension == 'c':
                pass
                # if history['f']:
                #     all_instrs.update(convert_csv_to_dict('fc', keys))
                # if history['d']:
                #     all_instrs.update(convert_csv_to_dict('dc', keys))
            # Expand upon with more combinations as we make them

    if reg:
        return all_instrs, reg_dict
    else:
        return all_instrs

# Function to take in a CSV file and convert it into the desired dictionary format
def convert_csv_to_dict(isa, key=None):
    test_dict = {}
    with open("isa/"+isa+".isa", 'r') as data_file:
        # Read in the data from the CSV file while ignoring comments 
        #   (beginning with a #) and ignoring empty lines
        data = csv.DictReader(filter(lambda row: row[0]!='#', data_file), \
        skipinitialspace=True, delimiter=',')

        for row in data:
            sub_dict = test_dict.get(row["Insn"], dict())
            if not key: # No key/key list given, form dictionary with all information
                for key in row.keys():
                    sub_dict[key] = row[key]
                test_dict[row["Insn"]] = sub_dict
            elif isinstance(key, str):
                test_dict[row["Insn"]] = row[key]
            elif isinstance(key, list):
                for k in key:
                    sub_dict[k] = row[k]
                test_dict[row["Insn"]] = sub_dict

    return test_dict

# Function to take in the reg lists and form the desired dictionary format
def convert_reg(isa_part):
    dict_base = {}
    with open("isa/reg/"+isa_part+".reg", 'r') as reg_file:
        for line in reg_file:
            sub_dict = dict_base[line.strip()] = {}
            sub_dict["rs"] = sub_dict["rd"] = 0

    return dict_base
