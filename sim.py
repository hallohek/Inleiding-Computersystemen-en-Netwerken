#!/usr/bin/env python3

import sys

from typing import List

from dataclasses import dataclass

@dataclass
class InstructiesNaDecode:       #eerlijk gezegd weet ik gewoon nogsteeds niet zoveel over dataclass aangezien deze import nieuw is voor mij, gelukkig heeft stack overflow e.d. mij erg geholpen deze opdracht
    Type: str
    opcode: int
    rd: int
    rs1: int
    rs2: int

class CPU:
    # Data memory; starts at 10240 (decimal!), size 4096.
    memory_base = 10240
    memory_size = 4096

    # Register file; 16 registers
    nRegs = 16


    def _init_components(self) -> None:
        #
        # Components: refer to the data path in the assignment
        # description.
        #

        # Program memory
        self.program : List[str] = []

        # Data memory: byte addressed.
        self.data_memory = bytearray(CPU.memory_size)

        # Register file.
        # 16 registers, note that R0 is not stored
        self.RegisterFile = [0] * (CPU.nRegs - 1)

        # Program counter
        self.PC = 0

        # Instruction register
        self.IR = ""

        # Instruction counter
        self.instruction_count = 0

    def laad_bestand(self, bestandsnaam):   #laad het bestand
        with open(bestandsnaam, "r") as bestand:    #opent het bestand
            for regel in bestand: #zorgt dat elke regel wordt gelezen
                regel = regel.strip()   #haalt alle overbodige delen van de regel weg (denk aan /n enzo)
                if not regel or regel.startswith("#"):   #slaat lege regels en commentaarregels over
                    continue
                elif regel.startswith("$"):         #slaat alle waardes die beginnen met $ op in het register
                    self._init_register(regel)
                    continue
                else:                               #aangezien al het andere dat in een document kan staan instructies zijn zet ik deze in self.programma
                    self.program.append(regel)
    
    def _init_register(self, regel):
        opdracht = regel[1:].strip() # maakt van "$ R1=2" -> " R1=2" ->"R1=2"
        registernaam, waarde = opdracht.split("=") #geeft registernaam waarde R1 en waar de waarde 2
        Rwaarde = int(waarde)
        #als het programma R0 wil veranderen wordt het genegeerd
        if registernaam == "R0":
            return
        #negeert alles dat niet met een R start
        if not registernaam.startswith("R"):
            return
        registerindexnummer = int(registernaam[1:]) - 1 #geeft me de positie van de registernaam in self.RegisterFile
        #als het bedoelde register niet in mijn mogelijke register limiet van R15 of lager zit wordt het programma genegeerd
        if registerindexnummer < 0 or registerindexnummer >= len(self.RegisterFile):
            return
        self.RegisterFile[registerindexnummer] = Rwaarde #voegt de juiste waarde toe bij de juiste R in de RegisterFile

    def __init__(self):
        self._init_components()

    def dump_registers(self):
        print(f"PC:\t{self.PC}")    #laat zien wat de Program Counter waarde is
        #gaat langs elke R in self.Register om de goeie waarde bij elke R te vinden terwijl deze R0 overslaat
        for rnum in range(1, 16): 
            Rwaarde = self.RegisterFile[rnum-1]
            print(f"R{rnum}:\t{Rwaarde}")

    def fetch(self): 
        self.IR = self.program[self.PC].strip() #haalt de instructies uit self.program en zet deze in de instruction register

    def decode(self): 
        IR = self.IR.strip()
        IRwaarden = [int(waarde.strip()) for waarde in IR.split(",")]
        opcode = IRwaarden[0]
        if opcode in {10, 11, 12}:
            Type = "R"
        #elif opcode in {110, 111, 112}:
            #Type == "I"
        if Type == "R":
            rd = IRwaarden[1]
            rs1 = IRwaarden[2]
            rs2 = IRwaarden[3]
            return InstructiesNaDecode(Type, opcode, rd, rs1, rs2)
        #elif Type == "I"

#Execute: we voeren nu de operatie daadwerkelijk uit en slaan indien nodig het resultaat op in het doelregister (write-back-stap).
    def execute(self, instructies): 
        if InstructiesNaDecode(Type) == "R":
            if InstructiesNaDecode(opcode) == 10:
                        #als het programma R0 wil veranderen wordt het genegeerd
        if registernaam == "R0":
            return
        #negeert alles dat niet met een R start
        if not registernaam.startswith("R"):
            return
        registerindexnummer = int(registernaam[1:]) - 1 #geeft me de positie van de registernaam in self.RegisterFile
        #als het bedoelde register niet in mijn mogelijke register limiet van R15 of lager zit wordt het programma genegeerd
        if registerindexnummer < 0 or registerindexnummer >= len(self.RegisterFile):
            return
        self.RegisterFile[registerindexnummer] = Rwaarde #voegt de juiste waarde toe bij de juiste R in de RegisterFile


    def run(self, ):
        self.instruction_count = 0     #instruction count met 1 verhogen zodat while loop start
        while self.PC < len(self.program): 
            self.fetch()    #fetch
            instructies = self.decode()    #decode
            self.execute(instructies)  #execute
            self.instruction_count += 1 #voegt 1 toe aan de instruction count
            self.PC += 1    #voegt 1 toe aan de program count


def main():
    cpu = CPU()
    cpu.laad_bestand(sys.argv[1])   #leest het programma naar de program memory

    print("initial register state:")
    cpu.dump_registers()
    print("\n")

    print("---- program output --------------")
    cpu.run()
    print("----------------------------------")
    print(f"{cpu.instruction_count} instructions executed.\n")

    print("register state:")
    cpu.dump_registers()


if __name__ == '__main__':
    main()
