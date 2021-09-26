import re
from pathlib import Path
import json
import os
class MortemParser:
    '''
    Parses a mortem.txt file generated after a Jupiter Hell run finishes
    '''
    def __init__(self, filepath: str = '') -> None:
        if filepath:
            self._filepath = Path(filepath).resolve()
        else:
            self._filepath = Path(os.getenv('JUPITER_MORTEM')).resolve()
        self._mortem = self._load_file()
        self.data = dict()

    def _load_file(self) -> str:
        '''
        Load contents of mortem file onto self.mortem
        '''
        if not self._filepath.is_file():
            raise FileNotFoundError
        if self._filepath.suffix != '.txt':
            raise ValueError('Only txt files accepted.')
        with self._filepath.open('r') as file:
            content = file.read()
        return content

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
        elif name.endswith('s') and not name.endswith('os'):
            name = name[:-1]
        return name

    def parse(self) -> dict:
        '''
        Parses mortem file and populates self.data with all necessary datapoints to create a new character instance
        '''
        data = dict()

        line1 = re.compile(r'(.+), level (\d+) (.+),')
        data['name'], data['level'], data['klass'] = re.search(line1, self._mortem).groups()
        data['level'] = int(data['level'])

        line2 = re.compile(r'killed on (.+) by a (.+)\.')
        match = re.search(line2, self._mortem)
        if match:
            data['won'] = False
            last_location, data['killed_by'] = match.groups()
            
        else:
            data['won'] = True
            last_location = data['killed_by'] = None
            
        line4 = re.compile(r'He survived for (\d+) turns.')
        data['turns_survived'] = int(re.search(line4, self._mortem).groups()[0])

        line5 = re.compile(r'The run time was (\d+)h (\d+)m (\d+)s.')
        data['run_time'] = ':'.join(re.search(line5, self._mortem).groups())

        line6 = re.compile(r'World seed was (\d+).')
        data['seed'] = int(re.search(line6, self._mortem).groups()[0])

        line7 = re.compile(r'He scored (\d+) points.')
        data['points'] = int(re.search(line7, self._mortem).groups()[0])

        line8 = re.compile(r'He took (.+) risks.')
        data['difficulty'] = re.search(line8, self._mortem).groups()[0][0]

        locpattern = re.compile(r'^(\w+(?: \w+)*) -(.*)$', re.MULTILINE)
        loc_groups = re.findall(locpattern, self._mortem)
        data['visited_locations'] = dict()
        order = 0
        for grp in loc_groups:
            left = grp[0].strip()
            right = grp[1].strip()
            if left not in data['visited_locations']:
                order += 1
                data['visited_locations'][left] = {'name': left, 'order': order, 'event': None}
            if right.startswith('>'):
                order += 1
                data['visited_locations'][right[1:].strip()] = {'name': right[1:].strip(), 'order': order, 'event': None}
            else:
                data['visited_locations'][left]['event'] = right
        if last_location and last_location not in data['visited_locations']:
            data['visited_locations'][last_location] = {'name': last_location, 'order': order+1, 'event': None}
        # Convert dict to list
        data['visited_locations'] = list(data['visited_locations'].values())

        awardpattern = re.compile(r'^  (.+?) \((\w+) ', re.MULTILINE)
        award_groups = re.findall(awardpattern, self._mortem)
        data['awards'] = []
        for award in award_groups:
            data['awards'].append({'name': award[0], 'typ': award[1]})

        totenemies = re.compile(r'He killed \d+ out of (\d+) enemies.')
        data['total_enemies'] = int(re.search(totenemies, self._mortem).groups()[0])
        
        killpattern = re.compile(r'(?:^ |\s{3})(\d+)\s{1,2}(\w+(?: \w+)*)', re.MULTILINE)
        kill_groups = re.findall(killpattern, self._mortem)
        data['kills'] = []
        for grp in kill_groups:
            monster_name = self.convert_to_singular(grp[1])
            data['kills'].append({'name': monster_name, 'howmany': grp[0]})

        traitpattern = re.compile(r'(?<=^  |->)*?(\w+)(?=->|\n\nEquipment)', re.MULTILINE)
        traits_list = re.findall(traitpattern, self._mortem)
        # Convert list to deserializable list of dicts
        data['traits'] = []
        traits_count = dict()
        for trait in traits_list:
            if trait not in traits_count:
                traits_count[trait] = 1
            else:
                traits_count[trait] += 1
            data['traits'].append({'short_name': trait, 'order': len(data['traits'])+1, 'level': traits_count[trait]})

        equipattern = re.compile(r'(?:^  Slot #|^  )(\d|Body|Head|Utility|Relic) +:( AV1| AV2| AV3| ENV)? ?(\S+(?: [^ \+ABP]+| AMP)*) ?([\+ABP\d]+)?\n((?:   \* )(?:.+\n)+)?', re.MULTILINE)
        equip_lines = re.findall(equipattern, self._mortem)
        data['equipment'] = []
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
                        level = int(split_name[-1])
                        name = ' '.join(split_name[:-1])
                    except ValueError:
                        level = None
                        name = ' '.join(split_name)
                    perks.append({'name': name, 'level': level})
            data['equipment'].append({'name': equip_name, 'slot': slot, 'rarity': rarity, 'mod_code': mod_code, 'perks': perks})

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
        data['inventory'] = [{'item': k, 'howmany': v} for k,v in inventory.items()]

        self.data = data
        return data
        
if __name__ == '__main__':
    import json
    x = MortemParser()
    data = x.parse()
    print(json.dumps(data, indent=4))
