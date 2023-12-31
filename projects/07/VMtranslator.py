import sys
import os

def parseVMfile2Str(file):
    vmCodeList = []
    with open(file, mode='r') as f:
        lines = f.read().splitlines()
        for line in lines:
            if not line:
                continue
            elif line[0:2] == '//':
                continue
            else:
                if '//' in line:
                    line = line.split('//')[0]
                    vmCodeList.append(line.strip())
                else:
                    vmCodeList.append(line.strip())
    return vmCodeList


def VMcommands2MachineCommands(vmCodeList, fileName):
    if '/' in fileName:
        fileName = fileName.split('/')[-1]

    def opAdd(code):
        machineCommands = []
        machineCommands.append('//' + code)
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=M')
        machineCommands.append('A=A-1')
        machineCommands.append('M=D+M')

        return machineCommands

    def opSub(code):
        machineCommands = []
        machineCommands.append('//' + code)
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=M')
        machineCommands.append('A=A-1')
        machineCommands.append('M=M-D')
        return machineCommands

    def opNeg(code):
        machineCommands = []
        machineCommands.append('//' + code)
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('M=-M')
        machineCommands.append('@SP')
        machineCommands.append('M=M+1')
        return machineCommands

    def opEq(code, index):
        machineCommands = []
        machineCommands.append('//' + code)
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=M')
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=D-M')
        machineCommands.append('@EQUAL' + str(index))
        machineCommands.append('D;JEQ')
        machineCommands.append('D=0')
        machineCommands.append('@FINAL' + str(index))
        machineCommands.append('0;JEQ')
        machineCommands.append('(EQUAL' + str(index) + ')')
        machineCommands.append('D=-1')
        machineCommands.append('(FINAL' + str(index) + ')')
        machineCommands.append('@SP')
        machineCommands.append('A=M')
        machineCommands.append('M=D')
        machineCommands.append('@SP')
        machineCommands.append('M=M+1')
        index += 1
        return machineCommands, index

    def opGt(code, index):
        machineCommands = []
        machineCommands.append('//' + code)
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=M')
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=M-D')
        machineCommands.append('@GREATER_THAN' + str(index))
        machineCommands.append('D;JGT')
        machineCommands.append('D=0')
        machineCommands.append('@END' + str(index))
        machineCommands.append('0;JEQ')
        machineCommands.append('(GREATER_THAN' + str(index) + ')')
        machineCommands.append('D=-1')
        machineCommands.append('(END' + str(index) + ')')
        machineCommands.append('@SP')
        machineCommands.append('A=M')
        machineCommands.append('M=D')
        machineCommands.append('@SP')
        machineCommands.append('M=M+1')
        index += 1
        return machineCommands, index

    def opLt(code, index):
        machineCommands = []
        machineCommands.append('//' + code)
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=M')
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=M-D')
        machineCommands.append('@LESS_THAN' + str(index))
        machineCommands.append('D;JLT')
        machineCommands.append('D=0')
        machineCommands.append('@END' + str(index))
        machineCommands.append('0;JEQ')
        machineCommands.append('(LESS_THAN' + str(index) + ')')
        machineCommands.append('D=-1')
        machineCommands.append('(END' + str(index) + ')')
        machineCommands.append('@SP')
        machineCommands.append('A=M')
        machineCommands.append('M=D')
        machineCommands.append('@SP')
        machineCommands.append('M=M+1')
        index += 1
        return machineCommands, index

    def opAnd(code):
        machineCommands = []
        machineCommands.append('//' + code)
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=M')
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=D&M')
        machineCommands.append('M=D')
        machineCommands.append('@SP')
        machineCommands.append('M=M+1')
        return machineCommands

    def opOr(code):
        machineCommands = []
        machineCommands.append('//' + code)
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=M')
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=D|M')
        machineCommands.append('M=D')
        machineCommands.append('@SP')
        machineCommands.append('M=M+1')
        return machineCommands

    def opNot(code):
        machineCommands = []
        machineCommands.append('//' + code)
        machineCommands.append('@SP')
        machineCommands.append('M=M-1')
        machineCommands.append('A=M')
        machineCommands.append('D=!M')
        machineCommands.append('M=D')
        machineCommands.append('@SP')
        machineCommands.append('M=M+1')
        return machineCommands

    def opPush(code, fileName):
        machineCommands = []
        parsedCode = code.split(" ")
        memorySegmentAccess = parsedCode[1]
        offset = parsedCode[-1]
        memorySegmentDict = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
        machineCommands.append('//' + code)
        if 'constant' in parsedCode:
            machineCommands.append('@' + str(offset))
            machineCommands.append('D=A')
            machineCommands.append('@SP')
            machineCommands.append('A=M')
            machineCommands.append('M=D')
            machineCommands.append('@SP')
            machineCommands.append('M=M+1')
        elif memorySegmentAccess in {'local', 'argument', 'this', 'that'}:
            machineCommands.append('@' + str(offset))
            machineCommands.append('D=A')
            machineCommands.append('@' + memorySegmentDict[memorySegmentAccess])
            machineCommands.append('A=D+M')
            machineCommands.append('D=M')
            machineCommands.append('@SP')
            machineCommands.append('A=M')
            machineCommands.append('M=D')
            machineCommands.append('@SP')
            machineCommands.append('M=M+1')
        elif 'temp' in parsedCode:
            machineCommands.append('@' + str(offset))
            machineCommands.append('D=A')
            machineCommands.append('@5')
            machineCommands.append('A=D+A')
            machineCommands.append('D=M')
            machineCommands.append('@SP')
            machineCommands.append('A=M')
            machineCommands.append('M=D')
            machineCommands.append('@SP')
            machineCommands.append('M=M+1')
        elif 'pointer' in parsedCode:
            if offset == '0':
                accessor = 'THIS'
            else:
                accessor = 'THAT'
            machineCommands.append('@' + accessor)
            machineCommands.append('D=M')
            machineCommands.append('@SP')
            machineCommands.append('A=M')
            machineCommands.append('M=D')
            machineCommands.append('@SP')
            machineCommands.append('M=M+1')
        elif 'static' in parsedCode:
            machineCommands.append('@' + fileName + '.' + str(offset))
            machineCommands.append('D=M')
            machineCommands.append('@SP')
            machineCommands.append('A=M')
            machineCommands.append('M=D')
            machineCommands.append('@SP')
            machineCommands.append('M=M+1')
        return machineCommands

    def opPop(code, fileName):
        machineCommands = []
        parsedCode = code.split(" ")
        memorySegmentAccess = parsedCode[1]
        offset = parsedCode[-1]
        memorySegmentDict = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
        machineCommands.append('//' + code)
        if memorySegmentAccess in {'local', 'argument', 'this', 'that'}:
            machineCommands.append('@' + str(offset))
            machineCommands.append('D=A')
            machineCommands.append('@' + memorySegmentDict[memorySegmentAccess])
            machineCommands.append('D=D+M')
            machineCommands.append('@R13')
            machineCommands.append('M=D')
            machineCommands.append('@SP')
            machineCommands.append('M=M-1')
            machineCommands.append('A=M')
            machineCommands.append('D=M')
            machineCommands.append('@R13')
            machineCommands.append('A=M')
            machineCommands.append('M=D')
        elif 'temp' in parsedCode:
            machineCommands.append('@' + str(offset))
            machineCommands.append('D=A')
            machineCommands.append('@5')
            machineCommands.append('D=D+A')
            machineCommands.append('@R13')
            machineCommands.append('M=D')
            machineCommands.append('@SP')
            machineCommands.append('M=M-1')
            machineCommands.append('A=M')
            machineCommands.append('D=M')
            machineCommands.append('@R13')
            machineCommands.append('A=M')
            machineCommands.append('M=D')
        elif 'pointer' in parsedCode:
            if offset == '0':
                accessor = 'THIS'
            else:
                accessor = 'THAT'
            machineCommands.append('@SP')
            machineCommands.append('M=M-1')
            machineCommands.append('A=M')
            machineCommands.append('D=M')
            machineCommands.append('@' + accessor)
            machineCommands.append('M=D')
        elif 'static' in parsedCode:
            machineCommands.append('@SP')
            machineCommands.append('M=M-1')
            machineCommands.append('A=M')
            machineCommands.append('D=M')
            machineCommands.append('@' + fileName + '.' + str(offset))
            machineCommands.append('M=D')
        return machineCommands
    machineCommandsList = []
    index = 0
    for line in vmCodeList:
        if 'add' in line:
            machineCommands = opAdd(line)
        elif 'sub' in line:
            machineCommands = opSub(line)
        elif 'neg' in line:
            machineCommands = opNeg(line)
        elif 'eq' in line:
            machineCommands, index = opEq(line, index)
        elif 'gt' in line:
            machineCommands, index = opGt(line, index)
        elif 'lt' in line:
            machineCommands, index = opLt(line, index)
        elif 'and' in line:
            machineCommands = opAnd(line)
        elif 'or' in line:
            machineCommands = opOr(line)
        elif 'not' in line:
            machineCommands = opNot(line)
        elif 'push' in line:
            machineCommands = opPush(line, fileName)
        elif 'pop' in line:
            machineCommands = opPop(line, fileName)
        machineCommandsList += machineCommands
    return machineCommandsList


def MachineListToFile(fileName, machineCommands):
    fileName = os.path.splitext(fileName)[0] + '.asm'
    with open(fileName, mode='w') as f:
        for line in machineCommands:
            f.write(line + '\n')


def main():
    if len(sys.argv) == 2:
        VMfilename = sys.argv[1]
        vmCodeList = parseVMfile2Str(VMfilename)
        machineCommands = VMcommands2MachineCommands(
            vmCodeList, VMfilename.split('.')[0])
        MachineListToFile(VMfilename, machineCommands)
    else:
        print("Error: please enter valid filepath as argument")

if __name__ == "__main__":
    main()