# Analyse the instruction trace input through stdin
# Identify the most common instruction pairs

# Input : Trimmed down instruction trace
# Output :  -  JSON file giving the list of tuples where each instruction
#   pair is stored with a counter giving how often that pair has
#   occured. To then be passed into display files. (Optional)
#           -  Formatted list giving the instruction pairs and a counter 
#   detailing how often they've appeared.

# Example to guide use:
# Run the command : python3 scripts/insn_patterns/insn_pairs.py \
#                   -j=<optional json file path>
#                   < scripts/example-printf.trc
#   while in the base directory

import sys
import json
import os
import argparse

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from common.pattern_detection import local_maxima, print_pairs

# Input argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-j", "--jsondump", help="Filepath/name for output JSON files")
args = parser.parse_args()

#   Iterate through the instruction stream and calculate the most frequent instruction pairs
def track_pairs(instr_trace):
    pairs_dict = {}
    previous_instr = instr_trace[0].split()[4] # Set the first instruction first 

    for line in instr_trace[1:]:
        insn_name = line.split()[4]

        key_string = f'{previous_instr}, {insn_name}'

        if (key_string in pairs_dict):
            pairs_dict[key_string] += 1
        else:
            pairs_dict[key_string] = 1
        
        previous_instr = insn_name
    
    # Sort based on the corresponding counter values
    sorted_pairs = sorted(pairs_dict.items(), key=lambda x: x[1], reverse=True)

    # Returns a list of tuples where each instruction is associated with their counter
    return pairs_dict

def main():
    minimum_count = 5
    diff_threshold = 3
    # Read in the stdin and store in the instr_trace variable
    instr_trace = sys.stdin.readlines()

    result = local_maxima(track_pairs(instr_trace), minimum_count, diff_threshold, False)
    
    # Dump the list of most common patterns in a .json file to access
    #   it easily in the display scripts
    if (args.jsondump):
        with open(args.jsondump, 'w') as dump:
            dump.write(json.dumps(result))

    # Print the formatted version to stdout for user readability
    print_pairs(result)


if __name__ == "__main__":
    main()