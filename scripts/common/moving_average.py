# Script used to only calculate the moving average of any stream of
#   values based on an input argument value that determines the window size

# Input : Raw byte stream 
#   e.g. scripts/bandwidth/load_bw/example-load-bytes.txt
# Output : 
#   - Average byte stream - Printed to stdout
#       e.g. scripts/bandwidth/load_bw/example-load-bytes-avg.txt

# Example to guide use:
# Run the command : python3 scripts/common/moving_average.py \
#       -n=4 \
#       < scripts/bandwidth/load_bw/example-load-bytes.txt \
#       > scripts/bandwidth/load_bw/example-load-bytes-avg.txt
#   while in the base directory

import sys
import argparse
import scipy

# Script arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--window", help="Moving Average window size")
parser.add_argument("-f", "--ignore_first", \
    help="Set to True to ignore the first line")
args = parser.parse_args()

# Moving average window function
def moving_average_scipy(input_stream):
    avg = scipy.convolve(input_stream, [1]*int(args.window), 'same') / int(args.window)
    print( "Byte stream trace, moving average window size = "+args.window)
    print(*avg, sep='\n') # Print each value on a new line
    # return list(avg)

def main():
    input = sys.stdin.readlines()[1:] if args.ignore_first else sys.stdin.readlines()
    input_floats = [float(x) for x in input]
    moving_average_scipy(input_floats)

if __name__ == "__main__":
    main()