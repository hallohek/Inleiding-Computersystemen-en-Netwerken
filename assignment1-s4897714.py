#Name: Nathan van de Wetering
#Student ID: s4897714

#!/usr/bin/env python3

#sorry als de comments wat in de war lijken, toen ik begon met dit project zette ik bij letterlijk alles comments en op een gegeven moment toen alles 'smooth' liep ben ik vergeten deze erbij te voegen, ik heb dus een groot deel pas op 21 November toegevoegd

import sys

from typing import List

from dataclasses import dataclass

#Deze R-Type instructies heeft de volgende velden: Type, de opcode en 3 registervelden (rd, rs1, rs2).
@dataclass
class RInstructies:       
    Type: str
    opcode: int
    rd: int
    rs1: int
    rs2: int

#Deze I-Type instructies heeft de volgende velden: Type, de opcode, 2 registervelden (rd, rs1) en een immediate veld (device_ID).
@dataclass
class IInstructies:
    Type: str
    opcode: int
    rd: int
    rs1: int
    device_ID: int

#Deze O-Type instructies heeft de volgende velden: Type, de opcode, een immediate (device_ID) en een registerveld (rs1).
@dataclass
class OInstructies: 
    Type: str
    opcode: int
    device_ID: int
    rs1: int

#Deze B-Type instructies heeft de volgende velden: Type, de opcode, een registerveld (rs1) en een immediate veld (device_ID).
@dataclass
class BInstructies:
    Type: str
    opcode: int
    rs1: int
    device_ID: int

#Deze LS-Type instructies heeft de volgende velden: Type, de opcode, 2 registervelden (R, RM) en een immediate veld (device_ID).
@dataclass
class LSInstructies:
    Type: str
    opcode: int
    R: int
    RM: int
    device_ID: int

#Deze J-Type instructies heeft de volgende velden: Type, de opcode, 2 registervelden (RL, rs1) en een immediate veld (device_ID).
@dataclass
class JInstructies:
    Type: str
    opcode: int
    RL: int
    rs1: int
    device_ID: int

#De CPU klasse die alle onderdelen van de CPU bevat en de functies waarmee deze CPU werkt
class CPU:
    # Data memory; starts at 10240 (decimal!), size 4096.
    memory_base = 10240
    memory_size = 4096

    # Register file; 16 registers
    nRegs = 16

#de opzet (initialisatie) van alle onderdelen van de CPU
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

#laad het bestand en haalt alle vastgestelde waardes eruit en filtert de onnodige regels eruit
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

#laad een mogenlijk 2e bestand na het hoofdbestand, dit 2e bestand is in deze opdracht een data memory bestand en is veel later dan laad_bestand toegevoegd
    def laad_data_memory(self, bestandsnaam):   #laad het bestand
        with open(bestandsnaam, "rb") as bestand:
            data = bestand.read()
            aantal_bytes = min(len(data), CPU.memory_size)
            for plek in range(aantal_bytes):
                self.data_memory[plek] = data[plek]

#deze functie zorgt ervoor dat alle vastgestelde waardes die in laad_bestand zijn gevonden op de juiste plek in het self.RegisterFile worden gezet
    def _init_register(self, regel):
        opdracht = regel[1:].strip() # maakt van "$ R1=2" -> " R1=2" ->"R1=2"
        registernaam, waarde = opdracht.split("=") #geeft registernaam waarde R1 en waar de waarde 2
        Rwaarde = int(waarde) #verzekert dat de waarde een integer is
        #als het programma R0 wil veranderen wordt het genegeerd (R0 is een hardwired zero)
        if registernaam == "R0":
            return
        #negeert alles dat niet met een R start
        if not registernaam.startswith("R"):
            return
        registerindexnummer = int(registernaam[1:]) - 1 #geeft me de positie van de registernaam in self.RegisterFile want R0 bestaat niet in self.RegisterFile dus moet ik -1 doen
        #als het bedoelde register niet in mijn mogelijke register limiet van R15 of lager zit wordt het programma genegeerd, ook als de Rpositie negatief is
        if registerindexnummer < 0 or registerindexnummer >= len(self.RegisterFile): 
            return
        self.RegisterFile[registerindexnummer] = Rwaarde #voegt de juiste waarde toe bij de juiste R in de RegisterFile

#zorgt ervoor dat de functie init_components wordt uitgevoerd bij het gebruik van CPU.
    def __init__(self):
        self._init_components()

#laat de waardes van de registers zien
    def dump_registers(self):
        print(f"PC:\t{self.PC}")    #laat zien wat de Program Counter waarde is
        #gaat langs elke R in self.Register om de goeie waarde bij elke R te vinden terwijl deze R0 overslaat, als er wel naar R0 gevraagd wordt geeft die altijd 0 terug
        for rnum in range(1, 16): 
            Rwaarde = self.RegisterFile[rnum-1]
            print(f"R{rnum}:\t{Rwaarde}")

#haalt de instructies uit de program memory en zet deze in de instruction register(IR)
    def fetch(self): 
        self.IR = self.program[self.PC].strip()

#haalt alle waardes uit self.IR en zet deze in IRwaaarden, daarna wordt de opcode uit IRwaarden gehaald en gekeken welk type instructie het is, daarna worden de waardes in de juiste dataclass(de dataclass is natuurlijk afhankelijk van Type) gezet en teruggegeven
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
        elif opcode in {78, 79}:
            Type = "J"
        else:
            print("Onbekende opcode: ", opcode)
            return None
        if Type == "R":
            rd = IRwaarden[1]
            rs1 = IRwaarden[2]
            rs2 = IRwaarden[3]
            return RInstructies(Type, opcode, rd, rs1, rs2)
        elif Type == "I":
            rd = IRwaarden[1]
            rs1 = IRwaarden[2]
            device_ID = IRwaarden[3]
            return IInstructies(Type, opcode, rd, rs1, device_ID)
        elif Type == "O":
            device_ID = IRwaarden[1]
            rs1 = IRwaarden[2]
            return OInstructies(Type, opcode, device_ID, rs1)
        elif Type == "B":
            rs1 = IRwaarden[1]
            device_ID = IRwaarden[2]
            return BInstructies(Type, opcode, rs1, device_ID)
        elif Type == "LS":
            R = IRwaarden[1]
            RM = IRwaarden[2]
            device_ID = IRwaarden[3]
            return LSInstructies(Type, opcode, R, RM, device_ID)
        elif Type == "J":
            RL = IRwaarden[1]
            rs1 = IRwaarden[2]
            device_ID = IRwaarden[3]
            return JInstructies(Type, opcode, RL, rs1, device_ID)
        else:
            print("niet het juiste type")
            return None

#deze functie is zo groot dat ik hem per Type zal uitleggen, maar in principe gebruikt deze functie de waardes die uit decode() komen om de juiste bewerkingen uit te voeren en de juiste waardes in de registers te zetten
    def execute(self, instructies):
        PC_handelingen = 1 #standaard wordt de PC met 1 verhoogd na elke instructie, tenzij een jump of branch dit veranderd
        if instructies is None: #zonder instructies wordt er niks gedaan naast 1 handeling erbij voor de PC
            return PC_handelingen
        if instructies.Type in ("R", "I"): #voor R en I type instructies wordt er gekeken of er naar R0 geschreven wordt, als dat zo is wordt de instructie genegeerd want R0 bestaat niet in het register en moet dus altijd 0 blijven
            if instructies.rd == 0:
                return PC_handelingen
            registerindexnummer = instructies.rd - 1 #vind de positie van de Rcijfer in self.RegisterFile
            #als het bedoelde register niet in mijn mogelijke register limiet van R15 of lager zit wordt het programma genegeerd
            if registerindexnummer < 0 or registerindexnummer >= len(self.RegisterFile):
                return PC_handelingen
        if instructies.Type == "R":     #hier worden alle R-Type instructies gedaan
            if instructies.rs1 == 0:    #als er naar R0 gevraagd wordt is de waarde altijd 0
                waarde1 = 0
            else:
                rs1_plek = instructies.rs1 - 1  #vind de positie van de rs1cijfer in self.RegisterFile
                waarde1 = self.RegisterFile[rs1_plek] #haalt de waarde van de juiste R uit self.RegisterFile
                if not (0 <= rs1_plek < len(self.RegisterFile)):   #als de rs1plek niet in het register zit wordt de instructie genegeerd
                    return PC_handelingen
            if instructies.rs2 == 0: #zelfde als rs1_plek maar dan voor rs2
                waarde2 = 0
            else:
                rs2_plek = instructies.rs2 - 1
                waarde2 = self.RegisterFile[rs2_plek]
                if not (0 <= rs2_plek < len(self.RegisterFile)):
                    return PC_handelingen
            self.Rwaarde = None #zet Rwaarde op None zodat ik kan checken of er een geldige bewerking is gedaan aan het einde van de if statements
            if instructies.opcode == 10: #telt de waardes van rs1 en rs2 bij elkaar op
                self.Rwaarde = waarde1 + waarde2
            if instructies.opcode == 11: #haalt de waarde van rs2 van die van rs1 af
                self.Rwaarde = waarde1 - waarde2
            if instructies.opcode == 12: #vermenigvuldigt de waardes van rs1 en rs2 met elkaar
                self.Rwaarde = waarde1 * waarde2
            if instructies.opcode == 20: #kijkt of rs1 kleiner is dan rs2
                if waarde1 < waarde2:
                    self.Rwaarde = 1
                else:
                    self.Rwaarde = 0
            if instructies.opcode == 21: #kijkt of rs1 kleiner of gelijk is aan rs2
                if waarde1 <= waarde2:
                    self.Rwaarde = 1
                else:
                    self.Rwaarde = 0
            if instructies.opcode == 22: #kijkt of rs1 groter is dan rs2
                if waarde1 > waarde2:
                    self.Rwaarde = 1
                else:
                    self.Rwaarde = 0
            if instructies.opcode == 23: #kijkt of rs1 groter of gelijk is aan rs2
                if waarde1 >= waarde2:
                    self.Rwaarde = 1
                else:
                    self.Rwaarde = 0
            if instructies.opcode == 24: #kijkt of rs1 gelijk is aan rs2
                if waarde1 == waarde2:
                    self.Rwaarde = 1
                else:
                    self.Rwaarde = 0
            if instructies.opcode == 25: #kijkt of rs1 niet gelijk is aan rs2
                if waarde1 != waarde2:
                    self.Rwaarde = 1
                else:
                    self.Rwaarde = 0
            if self.Rwaarde is not None: #voegt de juiste waarde toe bij de juiste R in de RegisterFile en de self.Rwaarde is niet None dus er is een geldige bewerking gedaan
                self.RegisterFile[registerindexnummer] = self.Rwaarde 
        elif instructies.Type == "I": #hier worden alle I-Type instructies gedaan
            if instructies.rs1 == 0:    #zie rs1 uitleg bij R-Type
                waarde1 = 0
            else:
                rs1_plek = instructies.rs1 - 1
                waarde1 = self.RegisterFile[rs1_plek]
                if not (0 <= rs1_plek < len(self.RegisterFile)):
                    return PC_handelingen
            self.Rwaarde = None #zie uitleg bij R-Type
            if instructies.opcode == 110: #telt de waarde van rs1 en de immediate (device_ID) bij elkaar op
                self.Rwaarde = waarde1 + instructies.device_ID
            if instructies.opcode == 111: #trekt de immediate (device_ID) van de waarde van rs1 af
                self.Rwaarde = waarde1 - instructies.device_ID
            if instructies.opcode == 112: #vermenigvuldigt de waarde van rs1 met de immediate (device_ID)
                self.Rwaarde = waarde1 * instructies.device_ID
            if instructies.opcode == 124: #kijkt of rs1 gelijk is aan de immediate (device_ID)
                if waarde1 == instructies.device_ID:
                    self.Rwaarde = 1
                else: 
                    self.Rwaarde = 0
            if instructies.opcode == 125: #kijkt of rs1 niet gelijk is aan de immediate (device_ID)
                if waarde1 != instructies.device_ID:
                    self.Rwaarde = 1
                else: 
                    self.Rwaarde = 0
            if self.Rwaarde is not None: #zie uitleg bij R-Type
                self.RegisterFile[registerindexnummer] = self.Rwaarde 
        elif instructies.Type == "O": #hier worden alle O-Type instructies gedaan
            if instructies.rs1 == 0:   #zie rs1 uitleg bij R-Type
                waarde1 = 0
            else:
                rs1_plek = instructies.rs1 - 1
                waarde1 = self.RegisterFile[rs1_plek]
                if not (0 <= rs1_plek < len(self.RegisterFile)):
                    return PC_handelingen
            if instructies.opcode == 50: #zorgt ervoor waardes uit het register naar de terminal (device 10) worden geschreven in ASCII
                if instructies.device_ID != 10: #alleen device_ID 10 (terminal) is toegestaan voor output
                    raise ValueError(f"Out-instructie: opcode {instructies.device_ID} niet toegestaan")
                print(chr(waarde1 & 0xFF), end='')
        elif instructies.Type == "B": #hier worden alle B-Type instructies gedaan (dit zijn conditional jumps (oftewel branches))
            if instructies.rs1 == 0:    #zie rs1 uitleg bij R-Type
                waarde1 = 0
            else:
                rs1_plek = instructies.rs1 - 1
                if not (0 <= rs1_plek < len(self.RegisterFile)):
                    return PC_handelingen
                waarde1 = self.RegisterFile[rs1_plek]
            if instructies.opcode == 60: #maakt een jump als de waarde in rs1 gelijk is aan 0
                if waarde1 == 0:
                    PC_handelingen = instructies.device_ID
            if instructies.opcode == 61: #maakt een jump als de waarde in rs1 niet gelijk is aan 0
                if waarde1 != 0:
                    PC_handelingen = instructies.device_ID
        elif instructies.Type == "LS": #hier worden alle LS-Type instructies gedaan
            if instructies.RM == 0: #zie rs1 uitleg bij R-Type aleen is het hier voor RM, het doet alleen nogsteeds hetzelfde
                rmwaarde = 0
            else:
                rm_index = instructies.RM - 1
                rmwaarde = self.RegisterFile[rm_index]
                if not (0 <= rm_index < len(self.RegisterFile)):
                    return PC_handelingen
            effective_address = rmwaarde + instructies.device_ID #berekent het adres in de data memory waar de load of store moet gebeuren
            if effective_address < CPU.memory_base or effective_address >= CPU.memory_size + CPU.memory_base: #checkt of het effectieve adres binnen de data memory valt (zo niet dan wordt de instructie genegeerd)
                return PC_handelingen
            positie_data_memory = effective_address - CPU.memory_base #berekent de positie in de data memory (aangezien de data memory begint bij 10240 moet ik dit eraf halen om de juiste plek te vinden)
            if instructies.opcode == 80: #zorgt ervoor dat er een byte uit de data memory wordt gehaald(geladen) en in het juiste register wordt gezet dit heet de load instructie
                byte_waarde = self.data_memory[positie_data_memory]
                if instructies.R != 0:
                    self.RegisterFile[instructies.R - 1] = byte_waarde
            elif instructies.opcode == 81: #zorgt ervoor dat er een byte uit het juiste register in de data memory wordt gezet (opgeslagen) dit heet de store instructie (het tegenovergestelde van de load instructie)
                if instructies.R == 0:
                    Rwaarde = 0
                else: 
                    Rwaarde = self.RegisterFile[instructies.R - 1]
                self.data_memory[positie_data_memory] = Rwaarde & 0xFF
        elif instructies.Type == "J": #hier worden alle J-Type instructies gedaan
            if instructies.rs1 == 0:   #zie rs1 uitleg bij R-Type
                waarde1 = 0
            else:
                rs1_plek = instructies.rs1 - 1
                waarde1 = self.RegisterFile[rs1_plek]
                if not (0 <= rs1_plek < len(self.RegisterFile)):
                    return PC_handelingen
            if instructies.opcode == 78: #zorgt voor een jump met absolute adressen
                instructies.RL = 0
                PC_handelingen = instructies.device_ID + waarde1 - self.PC
            elif instructies.opcode == 79: #zorgt ook voor een jump met absolute adressen maar slaat ook de return locatie op in RL als RL niet 0 is
                if instructies.RL != 0:
                    PC_handelingen = instructies.device_ID + waarde1 - self.PC
                    RLwaarde = self.PC + 1
                    self.RegisterFile[instructies.RL - 1] = RLwaarde
                else:
                    return PC_handelingen
        return PC_handelingen #zorgt dat de hoeveelheid PC waardes die veranderd moeten worden teruggegeven worden aan de run functie

    def run(self, ):
        self.instruction_count = 0     #reset instruction count (er start een nieuwe run die nog geen instructies heeft uitgevoerd)
        while self.PC < len(self.program): #zolang de Program Counter waarde binnen de program memory valt wordt alles hieronder uitgevoerd
            #volgende drie stappen zijn deel van de typische fetch-decode-execute cyclus van een CPU
            self.fetch()    #fetch
            instructies = self.decode()    #decode
            PC_handelingen = self.execute(instructies)  #execute + krijgt de door hoeveel er bij self.PC opgeteld moet worden terug
            self.instruction_count += 1 #verhoogt de instruction count met 1
            self.PC += PC_handelingen    #verhoogt de Program Counter met het aantal handelingen dat teruggegeven is door execute


def main():
    cpu = CPU()
    cpu.laad_bestand(sys.argv[1])   #leest het eerste programma naar de program memory
    if len(sys.argv) > 2:
        cpu.laad_data_memory(sys.argv[2])  #laadt data memory als er een tweede argument is

    print("initial register state:") #hieronder staan de beginwaardes van de registers (dus de waardes die in het bestand met $ begonnen)
    cpu.dump_registers()
    print("\n") #lege regel voor overzichtelijkheid

    print("---- program output --------------")#hieronder staat de output van het programma als deze er is (O-type instructies)
    cpu.run() #voert het programma uit
    print("----------------------------------")
    print(f"{cpu.instruction_count} instructions executed.\n") #laat zien hoeveel instructies er uitgevoerd zijn

    print("register state:") #hieronder staan de eindwaardes van de registers (dus de waardes na het uitvoeren van het programma)
    cpu.dump_registers() #wordt een 2e keer uitgevoerd maar laat andere dingen zien omdat het programma nu is uitgevoerd


if __name__ == '__main__': 
    main()
