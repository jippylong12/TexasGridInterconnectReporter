#!/usr/bin/env python3
"""
Constants and mappings for ERCOT GIM data.
Contains fuel type and technology acronym definitions.
"""

# Fuel Type Acronyms
# Source: ERCOT Generator Interconnection and Modeling (GIM) Reports
FUEL_TYPES = {
    'BIO': 'Biomass',
    'COA': 'Coal',
    'GAS': 'Gas',
    'GEO': 'Geothermal',
    'HYD': 'Hydrogen',
    'NUC': 'Nuclear',
    'OIL': 'Fuel Oil',
    'OTH': 'Other',
    'PET': 'Petcoke',
    'SOL': 'Solar',
    'WAT': 'Water',
    'WIN': 'Wind'
}

# Technology Type Acronyms
# Source: ERCOT Generator Interconnection and Modeling (GIM) Reports
TECHNOLOGY_TYPES = {
    'BA': 'Battery Energy Storage',
    'CC': 'Combined-Cycle',
    'CE': 'Compressed Air Energy Storage',
    'CP': 'Concentrated Solar Power',
    'EN': 'Energy Storage',
    'FC': 'Fuel Cell',
    'GT': 'Combustion (Gas) Turbine',
    'HY': 'Hydroelectric Turbine',
    'IC': 'Internal Combustion Engine',
    'OT': 'Other',
    'PV': 'Photovoltaic Solar',
    'ST': 'Steam Turbine',
    'WT': 'Wind Turbine'
}


def normalize_fuel_type(fuel_code: str) -> str:
    """
    Convert fuel type acronym to full name.
    
    Args:
        fuel_code: Fuel type acronym (e.g., 'SOL', 'WIN')
        
    Returns:
        Full fuel type name, or the original code if not found
    """
    if not fuel_code or str(fuel_code).strip() == '':
        return 'Unknown'
    
    fuel_code = str(fuel_code).strip().upper()
    return FUEL_TYPES.get(fuel_code, fuel_code)


def normalize_technology_type(tech_code: str) -> str:
    """
    Convert technology type acronym to full name.
    
    Args:
        tech_code: Technology type acronym (e.g., 'PV', 'WT', 'BA')
        
    Returns:
        Full technology type name, or the original code if not found
    """
    if not tech_code or str(tech_code).strip() == '':
        return 'Unknown'
    
    tech_code = str(tech_code).strip().upper()
    return TECHNOLOGY_TYPES.get(tech_code, tech_code)
