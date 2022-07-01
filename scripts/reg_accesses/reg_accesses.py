# Analyse the instruction trace input through stdin
# Measure how frequently specific registers are accessed

# Input : Trimmed down instruction trace
# Output : TODO

# Example to guide use:
# Run the command : python3 scripts/reg_accesses/reg_accesses.py < scripts/example.trc
#   while in the base directory

import sys
import argparse
import csv

# Input argument parsing (to detect the ISA)
parser = argparse.ArgumentParser()
parser.add_argument("--isa", help="RISC-V ISA string")
args = parser.parse_args() # ISA argument stored in args.isa

# Function to take in a CSV file and convert it into the desired dictionary format
def convert_reg_only(isa_part):
    test_dict = {}
    with open("isa/"+isa_part+".isa", 'r') as data_file:
        data = csv.DictReader(filter(lambda row: row[0]!='#', data_file), skipinitialspace=True, delimiter=',')
        for row in data:
            # Initialise subdirectory
            sub_dict = test_dict.get(row["Insn"], dict())
            # Also want to include information on the instruction type
            #   to understand what the immediate is actually being used for
            sub_dict["Type"] = row["Type"]
            sub_dict["Format"] = row["Format"]

            test_dict[row["Insn"]] = sub_dict

    return test_dict

# Take in the input string detailing the ISA, parse it and grab the needed dictionaries
def check_isa(isa):
    all_instrs = {}

    # Determine base instruction set based on the XLEN
    if int(isa[2:4]) == 32:
        all_instrs.update(convert_reg_only("rv32"))
    else:
        # No file yet made for this condition
        all_instrs.update(convert_reg_only("rv64"))
    
    # Include relevant instructions based on the remaining instructions
    for index in range(5, len(isa)):
        all_instrs.update(convert_reg_only(isa[index]))
    # TODO : Consider extensions such as the bit manip ones which won't be 
    #   represented by just single characters; also need to consider
    #   CSV files which are combinations of extensions

    return all_instrs

# Helper function that checks if an item is in the input dictionary and increments
#   if it is or creates a key if it doesn't exist
def append_to_counter_dict(dict, insn_name):
    if(insn_name in dict):
        dict[insn_name] += 1
    else:
        dict[insn_name] = 1

# Iterate through the instruction trace and measure the frequency at which
#   registers are accessed
def track_regs(instr_trace, all_instrs):
    # Initialise variables and dictionaries
    rs_dict = {}
    rd_dict = {}
    imm_dict = {}
    
    # Dictionary storing regular offsets such as those of loads and stores
    offset_dict = {}
    # Dictionary storing the offsets of jumps and branches
    branch_offset_dict = {}
    # Dictionary storing the shift sizes
    shift_dict = {}

    counter = 0
    # Parse lines on stdin
    for line in instr_trace:
        counter += 1
        line_list = line.split()
        insn_name = line_list[2]

        # Check for instruction in overall dictionary
        if insn_name in all_instrs:
            print()
            print(str(counter) + ": " + str(line_list[2:]))
            # Check what the register operand format is and assign variables accordingly
            insn_subdict = all_instrs[insn_name]
            if insn_subdict["Format"] == "R":
                # rd, rs1, rs2
                print("R Format")
                rd, rs1, rs2 = line_list[3:5]
                print("rd="+rd, "rs1="+rs1, "rs2="+rs2)

                append_to_counter_dict(rd_dict, line_list[3][:-1])
                append_to_counter_dict(rs_dict, line_list[4][:-1])
                append_to_counter_dict(rs_dict, line_list[5])
            elif insn_subdict["Format"] == "I":
                # rd, imm(rs)
                print("I Format")
                append_to_counter_dict(rd_dict, line_list[3][:-1])
                # Parse the second part of the assembly register format
                remaining_string = line_list[4].replace("(", " ", 1)[:-1].split()
                # Not converting immediates to ints as we may get immediates as hex values
                append_to_counter_dict(imm_dict, remaining_string[0])
                append_to_counter_dict(rs_dict, remaining_string[1])

                print("rd="+line_list[3][:-1], "imm="+remaining_string[0], "rs="+remaining_string[1])
                # If this instruction is a shift instruction, increase it's corresponding 
                #   counter in the shift dictionary
                if (insn_subdict["Type"] == "shift"):
                    print("Shift detected")
                    append_to_counter_dict(shift_dict, remaining_string[0])
                elif(insn_subdict["Type"] == "load"):
                    print("Load detected")
                    append_to_counter_dict(offset_dict, remaining_string[0])
            elif insn_subdict["Format"] == "S":
                # rs1, imm(rs2)
                print("S Format")

                append_to_counter_dict(rs_dict, line_list[3][:-1])
                remaining_string = line_list[4].replace("(", " ", 1)[:-1].split()
                append_to_counter_dict(imm_dict, remaining_string[0])
                append_to_counter_dict(offset_dict, remaining_string[0])
                append_to_counter_dict(rs_dict, remaining_string[1])

                print("rs1="+line_list[3][:-1], "imm/offset="+remaining_string[0], "rs2="+remaining_string[1])
            elif insn_subdict["Format"] == "U":
                # rd, imm
                print("U Format")

                append_to_counter_dict(rd_dict, line_list[3][:-1])
                append_to_counter_dict(imm_dict, line_list[4])

                print("rd="+line_list[3][:-1], "imm="+line_list[4])
            elif insn_subdict["Format"] == "SB":
                # rs1, rs2, pc + imm
                print("SB Format")

                append_to_counter_dict(rs_dict, line_list[3][:-1])
                append_to_counter_dict(rs_dict, line_list[4][:-1])
                append_to_counter_dict(imm_dict, line_list[6]+line_list[7])
                append_to_counter_dict(branch_offset_dict, line_list[6]+line_list[7])

                print("rs1="+line_list[3][:-1], "rs2="+line_list[4][:-1], "imm/branch offset="+line_list[6]+line_list[7])

            elif insn_subdict["Format"] == "UJ":
                # pc + imm
                print("UJ Format")
                append_to_counter_dict(rd_dict, "ra") # Return Address register
                append_to_counter_dict(imm_dict, line_list[4]+line_list[5])
                append_to_counter_dict(branch_offset_dict, line_list[4]+line_list[5])

                print("rd=ra", "imm/branch offset="+line_list[4]+line_list[5])

            elif insn_subdict["Format"] == "CR":     # Compressed formats
                # rs/d, rs
                print("CR Format")

                if(insn_name=="c.jr" or insn_name=="c.jalr"):
                    # rs
                    append_to_counter_dict(rs_dict, line_list[3])
                    print("rs="+line_list[3])
                    continue

                first_reg = line_list[3][:-1]
                append_to_counter_dict(rd_dict, first_reg)
                append_to_counter_dict(rs_dict, line_list[4])

                print("rd="+first_reg, "rs="+line_list[4])

                # Cases where the destination register is also being read from
                if(insn_name=="c.add" or insn_name=="c.addw" or insn_name=="c.sub"):
                    append_to_counter_dict(rs_dict, first_reg)
                    print("rs="+first_reg)

            elif insn_subdict["Format"] == "CI":
                # rs/d, imm,
                print("CI Format")

                first_reg = line_list[3][:-1]
                append_to_counter_dict(rd_dict, first_reg)

                if(insn_name=="c.lwsp" or insn_name=="c.ldsp" or insn_name=="c.lqsp"):
                    # rd, imm(rs)
                    remaining_string = line_list[4].replace("(", " ", 1)[:-1].split()
                    append_to_counter_dict(imm_dict, remaining_string[0])
                    append_to_counter_dict(rs_dict, remaining_string[1])
                    print("rd="+first_reg, "imm="+remaining_string[0], "rs="+remaining_string[1])
                    continue

                append_to_counter_dict(imm_dict, line_list[4])

                print("rd="+first_reg, "imm="+line_list[4])

                # Cases where the dest register is also read from
                if(insn_name == "c.addi" or 
                    insn_name == "c.addiw" or 
                    insn_name == "c.addi16sp" or
                    insn_name == "c.slli"):
                    append_to_counter_dict(rs_dict, first_reg)
                    print("rs="+first_reg)

            elif insn_subdict["Format"] == "CSS":
                # rs, imm(sp)
                print("CSS Format")

                append_to_counter_dict(rs_dict, line_list[3][:-1])
                append_to_counter_dict(imm_dict, line_list[4].split("(")[0])
                append_to_counter_dict(rs_dict, "sp")
        
                print("rs1="+line_list[3][:-1], "imm="+line_list[4].split("(")[0], "rs2=sp")

            elif insn_subdict["Format"] == "CIW":
                # rd, sp, imm
                print("CIW Format")

                append_to_counter_dict(rd_dict, line_list[3][:-1])
                append_to_counter_dict(rs_dict, "sp")
                append_to_counter_dict(imm_dict, line_list[5])

                print("rd="+line_list[3][:-1], "rs=sp, ", "imm="+line_list[5])

            elif insn_subdict["Format"] == "CL":
                # rd, imm(rs) - can merge with  'I'
                print("CL Format")

                append_to_counter_dict(rd_dict, line_list[3][:-1])
                remaining_string = line_list[4].replace("(", " ", 1)[:-1].split()
                append_to_counter_dict(imm_dict, remaining_string[0])
                append_to_counter_dict(rs_dict, remaining_string[1])

                print("rd="+line_list[3][:-1], "imm="+remaining_string[0], "rs="+remaining_string[1])

            elif insn_subdict["Format"] == "CS":
                # rs1, imm(rs2) - can merge with 'S'
                print("CS Format")

                append_to_counter_dict(rs_dict, line_list[3][:-1])
                remaining_string = line_list[4].replace("(", " ", 1)[:-1].split()
                append_to_counter_dict(imm_dict, remaining_string[0])
                append_to_counter_dict(rs_dict, remaining_string[1])
            
                print("rs1="+line_list[3][:-1], "imm="+remaining_string[0], "rs2="+remaining_string[1])

            elif insn_subdict["Format"] == "CA":
                pass # TODO
            elif insn_subdict["Format"] == "CB":
                # rs, pc + imm
                print("CB Format")
                append_to_counter_dict(rs_dict, line_list[3][:-1])
                append_to_counter_dict(imm_dict, line_list[6])

                print("rs="+line_list[3][:-1], "imm="+line_list[6])
            elif insn_subdict["Format"] == "CJ":
                # pc + imm
                print("CJ Format")
                # TODO : Add specific case for 'jumpl' instruction types where
                #   the return address is added to the rd dictionary
                if(insn_name=="c.jal"):
                    append_to_counter_dict(rd_dict, "ra") # Return Address register
                append_to_counter_dict(imm_dict, line_list[4]+line_list[5])

                print("rd=ra", "imm="+line_list[4]+line_list[5])
            else:
                pass # Do nothing if the column has nothing
    

    print("rs")
    print(rs_dict)
    print("rd")
    print(rd_dict)
    print("imm")
    print(imm_dict)
    print("offset_dict")
    print(offset_dict)
    print("branch_offset")
    print(branch_offset_dict)
    print("shift dict")
    print(shift_dict)

def main():
    # Read in the stdin and store in the instr_trace variable
    instr_trace = sys.stdin.readlines()
    track_regs(instr_trace, check_isa(args.isa))

if __name__ == "__main__":
    main()