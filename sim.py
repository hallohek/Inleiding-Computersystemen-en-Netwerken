#lvl0 t/m 6 = done
#!/usr/bin/env python3

import sys

from typing import List

from dataclasses import dataclass

@dataclass
class RInstructies:       #eerlijk gezegd weet ik gewoon nogsteeds niet zoveel over dataclass aangezien deze import nieuw is voor mij, gelukkig heeft stack overflow e.d. mij erg geholpen deze opdracht
    Type: str
    opcode: int
    rd: int
    rs1: int
    rs2: int

@dataclass
class IInstructies:
    Type: str
    opcode: int
    rd: int
    rs1: int
    immediate: int

@dataclass
class OInstructies: 
    Type: str
    opcode: int
    immediate: int
    rs1: int

@dataclass
class BInstructies:
    Type: str
    opcode: int
    rs1: int
    immediate: int

@dataclass
class LSInstructies:
    Type: str
    opcode: int
    R: int
    RM: int
    immediate: int

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
    def laad_data_memory(self, bestandsnaam):   #laad het bestand
        with open(bestandsnaam, "rb") as bestand:
            data = bestand.read()
            aantal_bytes = min(len(data), CPU.memory_size)
            for plek in range(aantal_bytes):
                self.data_memory[plek] = data[plek]


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
        Type = None
        IR = self.IR.strip()
        IRwaarden = [int(waarde.strip()) for waarde in IR.split(",")]
        opcode = IRwaarden[0]
        if opcode in {10, 11, 12, 20, 21, 22, 23, 24, 25}:
            Type = "R"
        elif opcode in {110, 111, 112, 124, 125}:
            Type = "I"
        elif opcode == 50:
            Type = "O"
        elif opcode in {60, 61}:
            Type = "B"
        elif opcode in {80, 81}:
            Type = "LS"
        if Type == "R":
            rd = IRwaarden[1]
            rs1 = IRwaarden[2]
            rs2 = IRwaarden[3]
            return RInstructies(Type, opcode, rd, rs1, rs2)
        elif Type == "I":
            rd = IRwaarden[1]
            rs1 = IRwaarden[2]
            immediate = IRwaarden[3]
            return IInstructies(Type, opcode, rd, rs1, immediate)
        elif Type == "O":
            immediate = IRwaarden[1]
            rs1 = IRwaarden[2]
            return OInstructies(Type, opcode, immediate, rs1)
        elif Type == "B":
            rs1 = IRwaarden[1]
            immediate = IRwaarden[2]
            return BInstructies(Type, opcode, rs1, immediate)
        elif Type == "LS":
            R = IRwaarden[1]
            RM = IRwaarden[2]
            immediate = IRwaarden[3]
            return LSInstructies(Type, opcode, R, RM, immediate)
        else:
            print("niet het juiste type")
            return None

#Execute: we voeren nu de operatie daadwerkelijk uit en slaan indien nodig het resultaat op in het doelregister (write-back-stap).
    def execute(self, instructies):
        PC_handelingen = 1
        if instructies is None:
            return PC_handelingen
        if instructies.Type in ("R", "I"):
            if instructies.rd == 0:
                return PC_handelingen
            registerindexnummer = instructies.rd - 1
            #als het bedoelde register niet in mijn mogelijke register limiet van R15 of lager zit wordt het programma genegeerd
            if registerindexnummer < 0 or registerindexnummer >= len(self.RegisterFile):
                return PC_handelingen
        if instructies.Type == "R":
            if instructies.rs1 == 0:
                waarde1 = 0
            else:
                rs1_plek = instructies.rs1 - 1
                waarde1 = self.RegisterFile[rs1_plek]
                if not (0 <= rs1_plek < len(self.RegisterFile)):
                    return PC_handelingen
            if instructies.rs2 == 0:
                waarde2 = 0
            else:
                rs2_plek = instructies.rs2 - 1
                waarde2 = self.RegisterFile[rs2_plek]
                if not (0 <= rs2_plek < len(self.RegisterFile)):
                    return PC_handelingen
            self.Rwaarde = None
            if instructies.opcode == 10: #add
                self.Rwaarde = waarde1 + waarde2
            if instructies.opcode == 11: #sub
                self.Rwaarde = waarde1 - waarde2
            if instructies.opcode == 12: #mul
                self.Rwaarde = waarde1 * waarde2
            if instructies.opcode == 20: #SetLT
                if waarde1 < waarde2:
                    self.Rwaarde = 1
                else:
                    self.Rwaarde = 0
            if instructies.opcode == 21: #SetLE
                if waarde1 <= waarde2:
                    self.Rwaarde = 1
                else:
                    self.Rwaarde = 0
            if instructies.opcode == 22: #SetGT
                if waarde1 > waarde2:
                    self.Rwaarde = 1
                else:
                    self.Rwaarde = 0
            if instructies.opcode == 23: #SetGE
                if waarde1 >= waarde2:
                    self.Rwaarde = 1
                else:
                    self.Rwaarde = 0
            if instructies.opcode == 24: #SetEQ
                if waarde1 == waarde2:
                    self.Rwaarde = 1
                else:
                    self.Rwaarde = 0
            if instructies.opcode == 25: #SetNEQ
                if waarde1 != waarde2:
                    self.Rwaarde = 1
                else:
                    self.Rwaarde = 0
            if self.Rwaarde is not None:
                self.RegisterFile[registerindexnummer] = self.Rwaarde #voegt de juiste waarde toe bij de juiste R in de RegisterFile
        elif instructies.Type == "I":
            if instructies.rs1 == 0:
                waarde1 = 0
            else:
                rs1_plek = instructies.rs1 - 1
                waarde1 = self.RegisterFile[rs1_plek]
                if not (0 <= rs1_plek < len(self.RegisterFile)):
                    return PC_handelingen
            self.Rwaarde = None
            if instructies.opcode == 110: #add
                self.Rwaarde = waarde1 + instructies.immediate
            if instructies.opcode == 111: #sub
                self.Rwaarde = waarde1 - instructies.immediate
            if instructies.opcode == 112: #mul
                self.Rwaarde = waarde1 * instructies.immediate
            if instructies.opcode == 124: #SetEQI
                if waarde1 == instructies.immediate:
                    self.Rwaarde = 1
                else: 
                    self.Rwaarde = 0
            if instructies.opcode == 125: #SetNEQI
                if waarde1 != instructies.immediate:
                    self.Rwaarde = 1
                else: 
                    self.Rwaarde = 0
            if self.Rwaarde is not None:
                self.RegisterFile[registerindexnummer] = self.Rwaarde
        elif instructies.Type == "O":
            if instructies.rs1 == 0:
                waarde1 = 0
            else:
                rs1_plek = instructies.rs1 - 1
                waarde1 = self.RegisterFile[rs1_plek]
                if not (0 <= rs1_plek < len(self.RegisterFile)):
                    return PC_handelingen
            if instructies.opcode == 50: #out
                print(chr(waarde1 & 0xFF), end='')
        elif instructies.Type == "B":
            if instructies.rs1 == 0:
                waarde1 = 0
            else:
                rs1_plek = instructies.rs1 - 1
                if not (0 <= rs1_plek < len(self.RegisterFile)):
                    return PC_handelingen
                waarde1 = self.RegisterFile[rs1_plek]
            if instructies.opcode == 60: #BZ
                if waarde1 == 0:
                    PC_handelingen = instructies.immediate
            if instructies.opcode == 61: #BNZ
                if waarde1 != 0:
                    PC_handelingen = instructies.immediate
        elif instructies.Type == "LS":
            if instructies.RM == 0:
                rmwaarde = 0
            else:
                rm_index = instructies.RM - 1
                rmwaarde = self.RegisterFile[rm_index]
            effective_address = rmwaarde + instructies.immediate
            if effective_address < CPU.memory_base or effective_address >= CPU.memory_size + CPU.memory_base:
                return PC_handelingen
            positie_data_memory = effective_address - CPU.memory_base
            if instructies.opcode == 80: #load
                byte_waarde = self.data_memory[positie_data_memory]
                if instructies.R != 0:
                    self.RegisterFile[instructies.R - 1] = byte_waarde
            #elif instructies.opcode == 81: #store
        return PC_handelingen

    def run(self, ):
        self.instruction_count = 0     #instruction count met 1 verhogen zodat while loop start
        while self.PC < len(self.program): 
            self.fetch()    #fetch
            instructies = self.decode()    #decode
            PC_handelingen = self.execute(instructies)  #execute
            self.instruction_count += 1 #voegt 1 toe aan de instruction count
            self.PC += PC_handelingen    #voegt de hoeveelheid PC waardes die uit de execute functie zijn gekomen toe aan de program count


def main():
    cpu = CPU()
    cpu.laad_bestand(sys.argv[1])   #leest het programma naar de program memory
    if len(sys.argv) > 2:
        cpu.laad_data_memory(sys.argv[2])  #laadt data memory als er een tweede argument is

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
