'''
Rei Thao
This program converts MIPS assembly into machine language. It receives a set of instructions, in MIPS assembly, and checks dictionaries to see if each instruction is an I or R type encoding problem. It then checks what type of register is being called in the statement and makes the correct conversion based on the result. Lastly, it checks what is being called again to correctly place the conversions.
import argparse
import re
import sys

R_Code = { #instruction
    "add" : "100000", 
    "sub" : "100010",
    "sll" : "000000",
    "srl" : "000010",
    "slt" : "101010"
}

I_Code = { #opcode
    "addi" : "001000",
    "beq" : "000100",
    "bne" : "000101",
    "lw" : "100011",
    "sw" : "101011"
}

Registers = {
    "$a0", "$a1", "$a2", "$a3",
    "$t0", "$t1", "$t2", "$t3", "$t4", "$t5", "$t6", "$t7", "$t8", "$t9",
    "$v0", "$v1",
    "$s0", "$s1", "$s2", "$s3", "$s4", "$s5", "$s6", "$s7",
    "$ra",
    "$sp",
    "$fp",
    "$gp",
    "$zero", "$0"
}

def convertRegister(register):
    if register[0] == "$":
        register = register[1:]
    if register == '0': return "00000"
    if register == '1': return "00001"
    return f"{int(register):05b}"  

def convertOffset(offset):
    offset = int(offset) 
    if offset == 0: return "0000000000000000"
    if offset < 0: return f"{(65536 + offset) & 0xFFFF:016b}"
    return f"{offset:016b}"

def convertIRegister(input):
    checkValid = input
    if input == "$zero" or input == "$0":
        return f"00000" 
    if checkValid[:3] not in Registers:
        if checkValid[1:].isdigit():
            return convertRegister(checkValid)
        return -1
    register = input[1:]
    if input[1] == 'v':
        return f"{(int(register[1:]) + 2):05b}" 
    elif input[1] == 'a':
        return f"{(int(register[1:]) + 4):05b}"  
    elif input == "$sp":
        return f"{29:05b}"
    elif input[1] == 's':
        return f"{(int(register[1:]) + 16):05b}" 
    elif input == "$gp":
        return f"{28:05b}" 
    elif input == "$fp":
        return f"{30:05b}"
    elif input == "$ra":
        return f"{31:05b}"
    elif input[1] == 't':
        if input[2] == '8':  #t8
            return f"{24:05b}"
        elif input[2] == '9':  #t9
            return f"{25:05b}"
        else:
            return f"{(int(register[1:]) + 8):05b}"
        
def convertInstruction(instruction):
    instruction = instruction.replace(',', ' ')
    instruction = instruction.replace('(', ' ')
    instruction = instruction.replace(')', '')
    mips = instruction.split()
    if len(mips) != 4 or (mips[0] not in R_Code and mips[0] not in I_Code): 
        return "!!! Invalid Input !!!"
    opcode, rd, rs, rt = mips[0], mips[1], mips[2], mips[3]

    if opcode in R_Code:
        function = R_Code[opcode]
        if opcode == 'srl' or opcode == 'sll':
            rd = convertRegister(rd)
            shamt = f"{int(rt):05b}"
            rt = convertRegister(rs)
            rs = "00000"
            return f"000000{rs}{rt}{rd}{shamt}{function}"
        else:
            opcode = "000000"
            shamt = "00000"
            if rs[:3] in Registers: rs = convertIRegister(rs)
            else: rs = convertRegister(rs)

            if rd[:3] in Registers: rd = convertIRegister(rd)
            else: rd = convertRegister(rd)

            if rt[:3] in Registers: rt = convertIRegister(rt)
            else: rt = convertRegister(rt)

            return f"{opcode}{rs}{rt}{rd}{shamt}{function}"
    
    elif opcode in I_Code:
        opcodeB = opcode
        opcode = I_Code[opcode]
        offsetB = 0 
        if rs.isdigit() or rs[0] == '-':
            if int(rs) < -32768 or int(rs) > 32767: return "!!! Invalid Input !!!"
            offsetB = int(rs)/4
            offsetB = convertOffset(offsetB)
            offset = convertOffset(rs)
            rs = convertIRegister(rt)        
            rt = convertIRegister(rd)
            return f"{opcode}{rs}{rt}{offset}"
        
        elif rt.isdigit() or rt[0] == '-':
            if int(rt) < -32768 or int(rt) > 32767: return "!!! Invalid Input !!!"
            offsetB = int(rt)/4
            offsetB = convertOffset(offsetB)
            offset = convertOffset(rt)
            rt = convertIRegister(rs)
            rs = convertIRegister(rd)
            if opcodeB == 'bne' or opcodeB == 'beq': return f"{opcode}{rs}{rt}{offsetB}"
            return f"{opcode}{rt}{rs}{offset}"
        
        if rs == -1 or rt == -1: 
            return "!!! Invalid Input !!!"

def parseInput(input_file, output_file):
    output_file = open(output_file, 'w') 
    with open(input_file, "r") as text_file: 
        for line in text_file: 
                line = line.strip()  
                convertedInstruction = convertInstruction(line)
                output_file.write(convertedInstruction + '\n') 
                if convertedInstruction[0] == "!":
                    sys.exit() 
    output_file.close

def main():
    parser = argparse.ArgumentParser(description = 'Enter a text file to translate.')
    parser.add_argument("--file", type = str, help = 'Input File')
    args = parser.parse_args()

    if args.file is None: args.file = 'in_code.txt'
    output_file = open("out_code.txt", "w")
    output_file.close
    output_file = "out_code.txt"
    parseInput(args.file, output_file)

if __name__ == "__main__":
    main()
