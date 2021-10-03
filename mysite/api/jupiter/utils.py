import re
from pathlib import Path
import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List

@dataclass(init=False)
class Mortem:
    name: str
    level: str
    klass: str
    killed_by: str
    won: bool
    turns_survived: int
    run_time: str
    seed: int
    points: int
    difficulty: str
    challenge: str
    visited_locations: List[dict]
    awards: list
    total_enemies: int
    kills: List[dict]
    traits: List[dict]
    equipment: List[dict]
    inventory: List[dict]
    mortem_timestamp: str


class MortemParser:
    '''
    Parses a mortem.txt file generated after a Jupiter Hell run finishes
    '''
    def __init__(self, filepath: str = '') -> None:
        if filepath:
            self._filepath = Path(filepath).resolve()
        else:
            self._filepath = Path(os.getenv('JUPITER_MORTEM')).resolve()
        self._mortem = None
        self._last_modified = None
        self._load_file()
        self.data = Mortem()

    def _load_file(self) -> str:
        '''
        Load contents of mortem file onto self.mortem
        Also loads the file last modified timestamp
        '''
        if not self._filepath.is_file():
            raise FileNotFoundError
        if self._filepath.suffix != '.txt':
            raise ValueError('Only txt files accepted.')
        with self._filepath.open('r') as file:
            content = file.read()
        self._mortem = content
        self._last_modified = datetime.fromtimestamp(self._filepath.stat().st_mtime)


    def convert_to_singular(self, name: str) -> str:
        '''
        Converts a name potentially in plural form to its singular form
        '''
        if name.endswith('i'):
            name = name[:-1] + 'os'
        elif name.endswith('oes'):
            name = name[:-2]
        elif name.endswith('ies'):
            name = name[:-3] + 'y'
        elif name.endswith('ae'):
            name = name[:-1]
        elif name.endswith('s') and not name.endswith('os'):
            name = name[:-1]
        return name

    def parse(self) -> dict:
        '''
        Parses mortem file and populates self.data with all necessary datapoints to create a new character instance
        '''
        line1 = re.compile(r'(.+), level (\d+) (.+),')
        self.data.name, self.data.level, self.data.klass = re.search(line1, self._mortem).groups()
        self.data.level = int(self.data.level)

        line2 = re.compile(r'^(killed on|commited suicide on|defeated the Harbinger) (.+?)(?: by a (.+)\.|\.)$', re.MULTILINE)
        match = re.search(line2, self._mortem)
        if match.groups()[0] == 'defeated the Harbinger':
            self.data.won = True
            last_location = 'Dante Altar'
            self.data.killed_by = None
            
        else:
            self.data.killed_by = match.groups()[2] or 'suicide'
            last_location = match.groups()[1]
            self.data.won = False
            
        line4 = re.compile(r'He survived for (\d+) turns.')
        self.data.turns_survived = int(re.search(line4, self._mortem).groups()[0])

        line5 = re.compile(r'The run time was (?:(\d+)h )?(\d+)m (\d+)s.')
        runtime_list = [grp or '00' for grp in re.search(line5, self._mortem).groups()]
        self.data.run_time = ':'.join(runtime_list)

        line6 = re.compile(r'World seed was (\d+).')
        self.data.seed = int(re.search(line6, self._mortem).groups()[0])

        line7 = re.compile(r'He scored (\d+) points.')
        self.data.points = int(re.search(line7, self._mortem).groups()[0])

        line8 = re.compile(r'(EASY|MEDIUM|HARD|ULTRAVIOLENCE|NIGHTMARE)')
        self.data.difficulty = re.search(line8, self._mortem).groups()[0][0]

        challengepat = re.compile(r'(Angel of Light Travel)')
        challenge = re.search(challengepat, self._mortem)
        if challenge:
            self.data.challenge = challenge.groups()[0]

        locpattern = re.compile(r'^(\w+(?: \w+)*) -(.*)$', re.MULTILINE)
        loc_groups = re.findall(locpattern, self._mortem)
        visited_locations = dict()
        order = 0
        for grp in loc_groups:
            left = grp[0].strip()
            right = grp[1].strip()
            if left not in visited_locations:
                order += 1
                visited_locations[left] = {'name': left, 'order': order, 'event': None}
            if right.startswith('>'):
                order += 1
                visited_locations[right[1:].strip()] = {'name': right[1:].strip(), 'order': order, 'event': None}
            else:
                visited_locations[left]['event'] = right
        if last_location and last_location not in visited_locations:
            visited_locations[last_location] = {'name': last_location, 'order': order+1, 'event': None}
        # Convert dict to list
        self.data.visited_locations = list(visited_locations.values())

        awardpattern = re.compile(r'(?<=Awards\n).+(?=\nHe killed)', re.DOTALL)
        self.data.awards = []
        try:
            award_lines = re.search(awardpattern, self._mortem)[0].splitlines()
            for award in award_lines:
                if not award.startswith('   *'):
                    self.data.awards.append({'name': award.strip()})
        except TypeError: #No matches
            pass

        totenemies = re.compile(r'He killed \d+ out of (\d+) enemies.')
        self.data.total_enemies = int(re.search(totenemies, self._mortem).groups()[0])
        
        killpattern = re.compile(r'(?:^ |\s{3})(\d+)\s{1,2}(\w+(?: \w+)*)', re.MULTILINE)
        kill_groups = re.findall(killpattern, self._mortem)
        self.data.kills = []
        for grp in kill_groups:
            monster_name = self.convert_to_singular(grp[1])
            self.data.kills.append({'name': monster_name, 'howmany': grp[0]})

        traitpattern = re.compile(r'(?<=^  |->)*?(\w+)(?=->|\n\nEquipment)', re.MULTILINE)
        traits_list = re.findall(traitpattern, self._mortem)
        # Convert list to deserializable list of dicts
        self.data.traits = []
        traits_count = dict()
        for trait in traits_list:
            if trait not in traits_count:
                traits_count[trait] = 1
            else:
                traits_count[trait] += 1
            self.data.traits.append({'short_name': trait, 'order': len(self.data.traits)+1, 'level': traits_count[trait]})

        equipattern = re.compile(r'(?:^  Slot #|^  )(\d|Body|Head|Utility|Relic) +:( AV1| AV2| AV3)? ?(\S+(?: [^ \+ABP]+| AMP)*) ?([\+ABP\d]+)?\n((?:   \* )(?:.+\n)+)?', re.MULTILINE)
        equip_lines = re.findall(equipattern, self._mortem)
        self.data.equipment = []
        for line in equip_lines:
            if all(char in '0123456789' for char in line[0]):
                slot = int(line[0])
            else:
                slot = None
            rarity = line[1] or None
            equip_name = line[2]
            mod_code = line[3] or None
            # Build perk list
            perks_raw = [perk.lstrip('   * ') for perk in line[4].split('\n') if perk] 
            # Separte perk name and level
            perks = []
            for perk in perks_raw:
                if perk:
                    split_name = perk.split()
                    try:
                        level = int(split_name[-1].replace('%', ''))
                        name = ' '.join(split_name[:-1])
                    except ValueError:
                        level = None
                        name = ' '.join(split_name)
                    perks.append({'name': name, 'level': level})
            self.data.equipment.append({'name': equip_name, 'slot': slot, 'rarity': rarity, 'mod_code': mod_code, 'perks': perks})

        invpattern = re.compile(r'(?<=Inventory\n)(.+)', re.DOTALL)
        inv_lines = re.search(invpattern, self._mortem).groups()[0].splitlines()
        inventory = dict()
        for line in inv_lines:
            split_line_raw = line.split('(')
            split_line = [item[1:].strip().replace(')','') for item in split_line_raw]
            if not inventory.get(split_line[0]):
                inventory[split_line[0]] = 0
            try:
                inventory[split_line[0]] += int(split_line[1])
            except IndexError:
                inventory[split_line[0]] += 1 # There is no count for this inventory line
        # convert dict to deserializable format
        self.data.inventory = [{'item': k, 'howmany': v} for k,v in inventory.items()]

        # add file creation timestamp
        self.data.mortem_timestamp = datetime.strftime(self._last_modified, '%Y-%m-%dT%H:%M:%S%z')
        
        return asdict(self.data)
        
if __name__ == '__main__':
    import json
    x = MortemParser()
    data = x.parse()
    print(json.dumps(data, indent=4))
