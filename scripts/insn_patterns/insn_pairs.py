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
#                   -j=<optional json file path> \
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
parser.add_argument("-r", "--rawdump", help="Filepath/name (without a file extension) \
    for the formatted unfiltered output patterns (prior to identifying the local \
    maxima). Two files are produced from this : a readable .txt file and a .JSON file")
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
    
    # Returns a list of tuples where each instruction is associated with their counter
    return pairs_dict

def main():
    minimum_count = 0
    diff_threshold = 3
    # Read in the stdin and store in the instr_trace variable
    instr_trace = sys.stdin.readlines()

    raw_result = track_pairs(instr_trace)
    # Optional raw information prior to the local maxima calculations can
    #   be saved and stored in their own files
    if args.rawdump:
        sorted_raw = sorted(raw_result.items(), key=lambda x: x[1], reverse=True)
        with open(args.rawdump+".JSON", 'w') as dump:
            dump.write(json.dumps(sorted_raw))
        with open(args.rawdump+".txt", 'w') as dump:
            dump.write("Raw most common instruction pairs")
            dump.write(json.dumps(print_pairs(sorted_raw, dump)))

    result = local_maxima(raw_result, minimum_count, diff_threshold, False)
    
    # Dump the list of most common patterns in a .json file to access
    #   it easily in the display scripts
    if args.jsondump:
        with open(args.jsondump, 'w') as dump:
            dump.write(json.dumps(result))

    print("Filtered most common instruction pairs")
    # Print the formatted version to stdout for user readability
    print_pairs(result)


if __name__ == "__main__":
    main()