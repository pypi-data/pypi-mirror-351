import json
from pathlib import Path

part_types = {
    'Balun': {'subcategory': {}},
    'Battery': {'subcategory': {}},
    'Battery Holder': {'subcategory': {}},
    'Bolt': {'subcategory': {}},
    'Bridge Rectifier': {'subcategory': {}},
    'Common Mode Choke': {'subcategory': {}},
    'Capacitor': {
        'subcategory': {
            'Aluminium Electrolytic Capacitor': {'required_parameters': []},
            'MLCC': {'required_parameters': []},
        }
    },
    'Connector': {
        'required_parameters': [],
        'subcategory': {
            'Connector Bus': {'required_parameters': []},
            'Connector Accessory': {'required_parameters': []},
            'Connector IDC': {'required_parameters': []},
            'Connector Terminal Block': {'required_parameters': []},
            'Connector microSD Card': {'required_parameters': []},
            'Connector Pins': {'required_parameters': []}
        },
    },
    'Crystal': {
        'required_fields': [],
        'required_parameters': ['Frequency'],
        'subcategory': {}
    },
    'Crystal Oscillator': {'subcategory': {}},
    'Display': {
        'subcategory': {
            'LCD Display': {'required_parameters': []}
        }
    },
    'Diode': {
        'required_parameters': [],
        'subcategory': {
            'Schottky Diode': {'required_parameters': []},
            'Small Signal Diode': {'required_parameters': []},
            'Zener Diode': {'required_parameters': []},
            'LED': {'required_parameters': []},
            'TVS': {'required_parameters': []}
        }
    },
    'Enclosure': {'subcategory': {}},
    'Enclosure Accessory': {'subcategory': {}},
    'ESD Suppressor': {'subcategory': {}},
    'Fuse': {
        'subcategory': {
            'PTC Fuse': {'required_parameters': []}
        }
    },
    'IC': {
        'required_fields': ["description"],
        'required_parameters': [],
        'subcategory': {
            'IC Voltage Reference': {'required_parameters': []},
            'IC LDO': {'required_parameters': []},
            'IC Voltage Regulator': {'required_parameters': []},
            'IC Voltage Regulator Switching': {'required_parameters': []},
            'IC MCU': {'required_parameters': []},
            'IC Comparator': {'required_parameters': []},
            'IC Opamp': {'required_parameters': []},
            'IC Level translator': {'required_parameters': []},
            'IC Current Sense': {'required_parameters': []},
            'IC Load Switch': {'required_parameters': []},
            'IC RF Amplifier': {'required_parameters': []},
            'IC RF Synthesizer': {'required_parameters': []},
            'IC DAC': {'required_parameters': []},
            'IC ADC': {'required_parameters': []},
            'IC Sensor': {'required_parameters': []},
        }
    },
    'Inductor': {
        'subcategory': {
        }
    },
    'Lightpipe': {
        'required_fields': ["description"],
        'subcategory': {
        }
    },
    'Module': {
        'required_fields': ["description"],
        'subcategory': {}
    },
    'Resistor': {
        'subcategory': {
            'Resistor Thick Film': {'required_parameters': []},
            'Resistor Thin Film': {'required_parameters': []},
            'Resistor Array': {'required_parameters': []}
        }
    },
    'Relay': {'subcategory': {}},
    'Transistor': {
        'required_parameters': [],
        'subcategory': {
            'Transistor MOSFET P': {'required_parameters': []},
            'Transistor MOSFET N': {'required_parameters': []}
        }
    },
    'Surge arrester': {
        'subcategory': {}
    },
    'Switch': {
        'required_fields': ["description"],
        'subcategory': {}
    },
    'Varistor': {'subcategory': {}}
}


def load_part_types():
    part_types_dict = {}
    for item in part_types.keys():
        required_fields = part_types[item]['required_fields'] if 'required_fields' in part_types[item] else []
        required_parameters = part_types[item]['required_parameters'] if 'required_parameters' in part_types[item] else []
        part_types_dict[item] = {
            'required_fields': required_fields,
            'required_parameters': required_parameters
        }
        if 'subcategory' in part_types[item] and len(part_types[item]['subcategory']) > 0:
            for subitem_key in part_types[item]['subcategory']:
                subitem = part_types[item]['subcategory'][subitem_key]
                part_types_dict[subitem_key] = {
                    'required_fields': required_fields + subitem['required_fields'] if 'required_fields' in subitem else [],
                    'required_parameters': required_parameters +  subitem['required_parameters'] if 'required_parameters' in subitem else []
                }
    return set(part_types_dict.keys()), part_types_dict


def load_manufacturers(path: Path):
    with open(path) as f:
        manufacturers = json.load(f)
        return [x['name'] for x in manufacturers] + [x['full_name'] for x in manufacturers if
                                                     x['full_name'] is not None and len(x['full_name']) > 0]


def load_packaging_types():
    return ['Bag', 'Bulk', 'Cut Tape', 'Embossed Tape / Reel', 'Paper Tape / Reel', 'Foil',
            'shrink wrap', 'Tube', 'Tray', '', 'Tape & Reel', '13” Reel', '7" reel']


def load_msl_classification():
    return ['MSL-1 UNLIM',
            'MSL-2 1-YEAR',
            'MSL-2A 4-WEEKS',
            'MSL-3 168-HOURS',
            'MSL-4 72-HOURS',
            'MSL-5 48-HOURS',
            'MSL-5A 24-HOURS',
            'MSL-6 TOL']


def load_files(directory):
    files = Path(directory).rglob('*.json')
    return [x for x in files if not str(x).endswith('_generated.json')]
