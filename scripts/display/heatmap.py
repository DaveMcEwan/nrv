# Plot a heatmap for any given pair-counter data format.

# Input : List of tuples where each tuple consists of 2 values where at index 0, 
#   we have a string of the comma separated pairs to be plotted on the axes of the 
#   heatmap and at index 1, we have the counter associated with that pair.
#   e.g. [["auipc, addi", 489], ["sw, lw", 79], ...]
# Output : Heatmap figure saved in the filepath provided by the --img flag

# Example to guide use:
# Run the command : python3 scripts/display/heatmap.py \
#                   -j=<input json file> \
#                   -p=<profile for plot axis names> \
#                   -i=<output figure filename>
#   while in the base directory

import numpy as np
import matplotlib.pyplot as plt
import json
import argparse

# Input argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("-j", "--jsondump", help="Filepath/name for input JSON files")
parser.add_argument("-i", "--img", help="Filepath/name for output figure")
parser.add_argument("-p", "--profile", help="Display profile, choose from: \
    insn_pairs or leave empty for default title/axis names. Add your own options \
    by setting up a profile in the heatmap.py script")
args = parser.parse_args()

# Function to parse the instruction pairs and their counters
def parse_pairs_heatmap(pairs_counter_list, size):
    # Mini dictionary containing the elements to be shown on the heatmap
    all_pairs = {}
    # Getting 5 unique leading and following instructions for the axes
    leading_labels = []
    unique_leading = 0
    following_labels = []
    unique_following = 0
    
    # Iterate through all pairs, form the main dictionary and acquire the n initial unique
    #   leading and following instructions
    for pairs_counter in pairs_counter_list:        
        all_pairs[pairs_counter[0]] = int(pairs_counter[1])

        pairs = pairs_counter[0].split()
        lead_instr = pairs[0][:-1]
        following_instr = pairs[1]
        
        if (unique_leading < size and lead_instr not in leading_labels):
            unique_leading += 1
            leading_labels.append(lead_instr)
        
        if (unique_following < size and following_instr not in following_labels):
            unique_following += 1
            following_labels.append(following_instr)

    # Form the numpy array to be plotted on the heatmap
    arr = np.zeros((size, size), int)
    for y in enumerate(leading_labels):
        for x in enumerate(following_labels):
            key_string = y[1]+", "+x[1]
            if key_string in all_pairs:
                arr[y[0]][x[0]] = all_pairs[key_string]

    return arr, leading_labels, following_labels

# https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html
def plot_heatmap(arr, y_labels, x_labels):
    fig, ax = plt.subplots()

    fig.set_size_inches(10,10)
    ax.imshow(arr)

    plt.yticks(np.arange(len(y_labels)), y_labels)
    plt.xticks(np.arange(len(x_labels)), x_labels)
    
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
        rotation_mode="anchor")

    for i in range(len(y_labels)):
        for j in range(len(x_labels)):
            text = ax.text(j, i, arr[i, j],
                        ha="center", va="center", color="w")

    if args.profile == "insn_pairs":
        ax.set_title("Frequency of instruction pairs")
        plt.ylabel('Leading instructions')
        plt.xlabel('Following instructions')
    else:
        ax.set_title("Heatmap")
        plt.ylabel("First value of the pair")
        plt.xlabel("Second value of the pair")

    plt.savefig(args.img)

def main():
    with open(args.jsondump, 'r') as dump:
        data = json.load(dump)
    
    arr, x_labels, y_labels = parse_pairs_heatmap(data, 16)
    plot_heatmap(arr, x_labels, y_labels)

if __name__ == "__main__":
    main()