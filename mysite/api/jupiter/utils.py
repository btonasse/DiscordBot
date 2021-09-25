import re
from pathlib import Path

class MortemParser:
    '''
    Parses a mortem.txt file generated after a Jupiter Hell run finishes
    '''
    def __init__(self, filepath: str) -> None:
        self._filepath = Path(filepath).resolve()
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
        data['difficulty'] = re.search(line8, self._mortem).groups()[0]

        locpattern = re.compile(r'(CALLISTO .+)\n\nHe killed', re.DOTALL)
        loclines = re.search(locpattern, self._mortem).groups()[0].splitlines()
        data['visited_locations'] = dict()
        order = 0
        for line in loclines:
            line_list = line.split('-')
            left = line_list[0].strip()
            right = line_list[1].strip()
            if not data['visited_locations'].get(left):
                order += 1
                data['visited_locations'][left] = {'order': order, 'event': None}
            if not right.startswith('>'):
                data['visited_locations'][left]['event'] = right.strip()
            else:
                order += 1
                data['visited_locations'][right[1:].strip()] = {'order': order, 'event': None}
        if last_location and last_location not in data['visited_locations']:
            data['visited_locations'][last_location] = {'order': order+1, 'event': None}

        totenemies = re.compile(r'He killed \d+ out of (\d+) enemies.')
        data['total_enemies'] = int(re.search(totenemies, self._mortem).groups()[0])
        
        killpattern = re.compile(r'enemies.\n\n(.+)\nTraits', re.DOTALL)
        kill_lines = re.search(killpattern, self._mortem).groups()[0].splitlines()
        data['kills'] = dict()
        for line in kill_lines:
            line_list = line.split('   ')
            left = line_list[0].strip()
            if len(line_list) > 1:
                right = line_list[-1].strip()
            else:
                right = None
            leftlist = left.split()
            lmonster = ' '.join(leftlist[1:])
            leftnum = leftlist[0]
            data['kills'][lmonster] = leftnum
            if right:
                rightlist = right.split()
                rmonster = ' '.join(rightlist[1:])
                rightnum = rightlist[0]
                data['kills'][rmonster] = rightnum

        traitpattern = re.compile(r'Trait order\n(.+)\s+Equipment', re.DOTALL)
        trait_lines = re.search(traitpattern, self._mortem).groups()[0].splitlines()
        data['traits'] = []
        for line in trait_lines:
            for trait_code in line.strip().split('->'):
                if trait_code:
                    data['traits'].append(trait_code)

        equippattern = re.compile(r'Equipment\n(.+)\s+Inventory', re.DOTALL)
        equip_lines = re.search(equippattern, self._mortem).groups()[0].splitlines()
        data['equipment'] = dict()
        slotno = 0
        for line in equip_lines:
            if line.strip().startswith('Slot'):
                slotno += 1
                #todo



            




        
        

        
        self.data = data
        return data
        

x = MortemParser('test.txt')
data = x.parse()
print(data)