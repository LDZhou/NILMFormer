"""Appliance groups for Pecan Street NILM"""

GROUPS = {
    # Flexible high-power loads
    'hvac': {
        'cols': ['air1', 'air2', 'air3', 'furnace1', 'furnace2', 'airwindowunit1', 
                 'heater1', 'heater2', 'heater3'],
        'threshold': {'min_threshold': 0.1, 'max_threshold': 10},
        'desc': 'Heating & cooling'
    },
    'waterheater': {
        'cols': ['waterheater1', 'waterheater2'],
        'threshold': {'min_threshold': 0.1, 'max_threshold': 10},
        'desc': 'Water heating'
    },
    'ev': {
        'cols': ['car1', 'car2'],
        'threshold': {'min_threshold': 0.2, 'max_threshold': 15},
        'desc': 'EV charging'
    },
    'pool': {
        'cols': ['pool1', 'pool2', 'poolpump1', 'poollight1'],
        'threshold': {'min_threshold': 0.050, 'max_threshold': 5},
        'desc': 'Pool equipment'
    },
    
    # Medium-power flexible
    'laundry': {
        'cols': ['clotheswasher1', 'drye1', 'dryg1', 'clotheswasher_dryg1'],
        'threshold': {'min_threshold': 0.02, 'max_threshold': 8},
        'desc': 'Washer & dryer'
    },
    'dishwasher': {
        'cols': ['dishwasher1'],
        'threshold': {'min_threshold': 0.01, 'max_threshold': 3},
        'desc': 'Dishwasher'
    },
    
    # Baseload
    'refrigeration': {
        'cols': ['refrigerator1', 'refrigerator2', 'freezer1', 'icemaker1', 'winecooler1'],
        'threshold': {'min_threshold': 0.05, 'max_threshold': 5},
        'desc': 'Fridge & freezer'
    },
    'kitchen': {
        'cols': ['oven1', 'oven2', 'range1', 'microwave1', 'disposal1', 'venthood1'],
        'threshold': {'min_threshold': 0.02, 'max_threshold': 8},
        'desc': 'Cooking appliances'
    },
    
    # Other
    'pumps': {
        'cols': ['circpump1', 'pump1', 'sewerpump1', 'sumppump1', 'wellpump1'],
        'threshold': {'min_threshold': 0.050, 'max_threshold': 2.000},
        'desc': 'Various pumps'
    },
    'other': {
        'cols': ['housefan1', 'jacuzzi1', 'sprinkler1', 'battery1', 'aquarium1', 'security1'],
        'threshold': {'min_threshold': 0.020, 'max_threshold': 2.000},
        'desc': 'Misc appliances'
    }
}