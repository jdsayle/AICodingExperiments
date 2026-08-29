import type { ThemeDefinition } from '../types';

export const THEME_CATALOG: Record<string, ThemeDefinition> = {
  post_apoc: {
    id: 'post_apoc',
    name: 'Post-Apocalyptic',
    biomes: [
      {
        id: 'the_blights',
        name: 'The Blights',
        description: 'Distorted psychic resonance and rad flats',
        hexColor: '#CCFF00',
        iconColor: '#000000',
        icon: 'blighted_waste',
        frequency: 1,
        subTypes: [
          { id: 'radioactive_badlands', name: 'Radioactive Badlands', description: 'Raw ionizing radiation zones', icon: 'radioactive_badlands', enabled: true, frequency: 1 },
          { id: 'plains_of_glass', name: 'Plains of Glass', description: 'Fleshy and fused silica expanses', icon: 'plains_of_glass', enabled: true, frequency: 1 },
          { id: 'blighted_waste', name: 'Blighted Waste', description: 'Decaying psychic residue flats', icon: 'blighted_waste', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'techno_ruins',
        name: 'Techno-Ruins',
        description: 'Cold glass, silicon, and chemical decay',
        hexColor: '#3A506B',
        iconColor: '#ffffff',
        icon: 'toxic_zone',
        frequency: 1,
        subTypes: [
          { id: 'toxic_dead_zones', name: 'Toxic Dead Zones', description: 'Corrosive chemical industrial decay', icon: 'toxic_zone', enabled: true, frequency: 1 },
          { id: 'slow_fire_machines', name: 'Slow Fire Machine Environments', description: 'Endlessly burning automated cores', icon: 'slow_fire', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'shattered_cities',
        name: 'Shattered Cities & Highways',
        description: 'Collapsing metropolitan layers and debris',
        hexColor: '#5C626D',
        iconColor: '#ffffff',
        icon: 'ruined_sprawl',
        frequency: 1,
        subTypes: [
          { id: 'ruined_urban_sprawl', name: 'Ruined Urban Sprawl', description: 'Collapsed concrete high-rises', icon: 'ruined_sprawl', enabled: true, frequency: 1 },
          { id: 'garbage_commons', name: 'Garbage Commons', description: 'Vast debris fields and scrap yards', icon: 'garbage_commons', enabled: true, frequency: 1 },
          { id: 'broken_highway', name: 'The Broken Highway', description: 'Elevated interstate wreckage', icon: 'broken_highway', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'scorched_barrens',
        name: 'Scorched & Black Dust Barrens',
        description: 'Burnt soot, ash, and choked riverbeds',
        hexColor: '#382A25',
        iconColor: '#ffffff',
        icon: 'scorched_wasteland',
        frequency: 1,
        subTypes: [
          { id: 'scorched_wastelands', name: 'Scorched Wastelands', description: 'Charred earth plains', icon: 'scorched_wasteland', enabled: true, frequency: 1 },
          { id: 'black_dust_barrens', name: 'Black Dust Barrens', description: 'Soot fields and ash dunes', icon: 'black_dust', enabled: true, frequency: 1 },
          { id: 'choked_riverbeds', name: 'Choked Riverbeds', description: 'Dry, silt-clogged water channels', icon: 'choked_riverbed', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'resurgent_wilds',
        name: 'Mutated & Resurgent Wilds',
        description: 'Aggressive post-collapse nature and overgrowth',
        hexColor: '#6B8E23',
        iconColor: '#000000',
        icon: 'resurgent_wilds',
        frequency: 1,
        subTypes: [
          { id: 'mutated_forests', name: 'Mutated Overgrown Forests', description: 'Twisted, bioluminescent timberlands', icon: 'mutated_forest', enabled: true, frequency: 1 },
          { id: 'resurgent_wilds', name: 'Resurgent Wilds', description: 'Aggressively reclaiming greenery', icon: 'resurgent_wilds', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'biological_horrors',
        name: 'Biological Horrors',
        description: 'Bruised charcoal void and mutation zones',
        hexColor: '#1A1625',
        iconColor: '#ffffff',
        icon: 'necrotic_sprawl',
        frequency: 1,
        subTypes: [
          { id: 'necrotic_sprawl', name: 'Necrotic Sprawl', description: 'Decaying organic slime expanses', icon: 'necrotic_sprawl', enabled: true, frequency: 1 },
          { id: 'dormant_megafauna', name: 'Dormant Mega-Fauna Roosts', description: 'Nesting grounds of colossal entities', icon: 'dormant_megafauna', enabled: true, frequency: 1 }
        ]
      }
    ],
    pois: [
      { name: 'The Ruins', icon: 'ruined_sprawl', color: '#71717a' },
      { name: 'The Survivor Settlement', icon: 'default_icon', color: '#10b981' },
      { name: 'The Wasteland Landmark', icon: 'toxic_zone', color: '#f59e0b' },
      { name: 'The Resource Site', icon: 'garbage_commons', color: '#3b82f6' }
    ],
    homeBase: {
      name: 'Safe Haven / Home Base',
      icon: 'default_icon',
      color: '#eab308'
    }
  },
  fantasy: {
    id: 'fantasy',
    name: 'High Fantasy',
    biomes: [
      {
        id: 'forests',
        name: 'Sylvan Forests',
        description: 'Deep woodlands and enchanted canopies',
        hexColor: '#1e532b',
        iconColor: '#ffffff',
        icon: '🌲',
        frequency: 1,
        subTypes: [
          { id: 'deep_woods', name: 'Deep Canopy Woods', description: 'Dense, shaded ancient timber', icon: '🌲', enabled: true, frequency: 1 },
          { id: 'fey_groves', name: 'Fey-Touched Groves', description: 'Glowing enchanted flora', icon: '🌸', enabled: true, frequency: 1 },
          { id: 'petrified_timbers', name: 'Petrified Timbers', description: 'Ancient calcified woodland', icon: '🪵', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'mountains',
        name: 'Highland Peaks',
        description: 'Jagged crags and snow-capped peaks',
        hexColor: '#64748b',
        iconColor: '#ffffff',
        icon: '🏔️',
        frequency: 1,
        subTypes: [
          { id: 'snow_peaks', name: 'Snow-Capped Ridges', description: 'Freezing high-altitude passes', icon: '❄️', enabled: true, frequency: 1 },
          { id: 'craggy_cliffs', name: 'Granite Precipices', description: 'Steep sheer rock faces', icon: '⛰️', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'hills',
        name: 'Rolling Hills',
        description: 'Grasslands, downs, and ancient mounds',
        hexColor: '#84cc16',
        iconColor: '#000000',
        icon: '🌾',
        frequency: 1,
        subTypes: [
          { id: 'green_downs', name: 'Verdant Downs', description: 'Open pasture and barrows', icon: '🌾', enabled: true, frequency: 1 },
          { id: 'stone_tumuli', name: 'Ancient Barrow Mounds', description: 'Prehistoric burial sites', icon: '🪨', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'swamps',
        name: 'Mire & Swamps',
        description: 'Boggy wetlands and treacherous fens',
        hexColor: '#3f6212',
        iconColor: '#ffffff',
        icon: '🐊',
        frequency: 1,
        subTypes: [
          { id: 'rotting_fens', name: 'Rotting Fens', description: 'Stagnant brackish marshes', icon: '🧟', enabled: true, frequency: 1 },
          { id: 'misty_bayous', name: 'Misty Bayous', description: 'Choked waterways and cypress roots', icon: '🌫️', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'volcanic_wastes',
        name: 'Volcanic Wastes',
        description: 'Ash fields and molten basalt flows',
        hexColor: '#7f1d1d',
        iconColor: '#ffffff',
        icon: '🌋',
        frequency: 1,
        subTypes: [
          { id: 'basalt_flats', name: 'Basalt Crag Flats', description: 'Cooling magma fields', icon: '🪨', enabled: true, frequency: 1 },
          { id: 'lava_veins', name: 'Active Lava Veins', description: 'Flowing magma channels', icon: '🔥', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'cavern_entrances',
        name: 'Underdark Chasm Entrances',
        description: 'Descents into subterranean realm subterranean complexes',
        hexColor: '#334155',
        iconColor: '#ffffff',
        icon: '🕳️',
        frequency: 1,
        subTypes: [
          { id: 'sinkhole_descent', name: 'Great Sinkholes', description: 'Vertical drop chasms', icon: '⛏️', enabled: true, frequency: 1 },
          { id: 'grotto_mouths', name: 'Grotto Passages', description: 'Carved natural cave mouths', icon: '🦇', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'oceans',
        name: 'Coastal & Open Seas',
        description: 'Deep oceanic trenches and shorelines',
        hexColor: '#0284c7',
        iconColor: '#ffffff',
        icon: '🌊',
        frequency: 1,
        subTypes: [
          { id: 'coastal_shallows', name: 'Coastal Reef Shallows', description: 'Navigable coastal waters', icon: '🏝️', enabled: true, frequency: 1 },
          { id: 'abyssal_deep', name: 'Abyssal Trenches', description: 'Unfathomable deep ocean', icon: '🦑', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'cities',
        name: 'Fortified Cities & Settlements',
        description: 'Trade hubs, castles, and walled bastions',
        hexColor: '#d97706',
        iconColor: '#000000',
        icon: '🏰',
        frequency: 1,
        subTypes: [
          { id: 'walled_metropolis', name: 'Walled Metropolis', description: 'High stone curtain walls', icon: '🏰', enabled: true, frequency: 1 },
          { id: 'sprawling_bazaars', name: 'Market Outposts', description: 'bustling frontier trade centers', icon: '🎪', enabled: true, frequency: 1 }
        ]
      }
    ],
    pois: [
      { name: 'The Dungeon', icon: '🕳️', color: '#ef4444' },
      { name: 'The Settlement', icon: '🏘️', color: '#3b82f6' },
      { name: 'The Ancient Site', icon: '🏛️', color: '#8b5cf6' },
      { name: 'The Lair', icon: '🐉', color: '#f59e0b' }
    ],
    homeBase: {
      name: 'Sanctuary / Citadel',
      icon: '🏰',
      color: '#3b82f6'
    }
  },
  sci_fi: {
    id: 'sci_fi',
    name: 'Sci-Fi',
    biomes: [
      {
        id: 'cyber_metropolis',
        name: 'Metropolitan Arcologies',
        description: 'High-density neon megastructures',
        hexColor: '#0ea5e9',
        iconColor: '#ffffff',
        icon: '🏙️',
        frequency: 1,
        subTypes: [
          { id: 'upper_concourse', name: 'Corporate Skyward Concourse', description: 'Polished high-rise plazas', icon: '🌆', enabled: true, frequency: 1 },
          { id: 'under_sprawl', name: 'Sub-Level Sprawl', description: 'Neon-lit rain-soaked alleys', icon: '🚇', enabled: true, frequency: 1 },
          { id: 'data_server_farms', name: 'Data Vault Enclaves', description: 'Cooling supercomputer blocks', icon: '💾', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'industrial_complexes',
        name: 'Off-World Industrial Sectors',
        description: 'Refineries, automated plants, and foundries',
        hexColor: '#f97316',
        iconColor: '#000000',
        icon: '🏭',
        frequency: 1,
        subTypes: [
          { id: 'automated_foundries', name: 'Automated Smelters', description: 'Robotic assembly plants', icon: '⚙️', enabled: true, frequency: 1 },
          { id: 'chemical_reactors', name: 'Reactor Complexes', description: 'Plasma containment hubs', icon: '☢️', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'alien_frontiers',
        name: 'Alien Planetary Frontiers',
        description: 'Uncharted exo-world ecosystems',
        hexColor: '#a855f7',
        iconColor: '#ffffff',
        icon: '🪐',
        frequency: 1,
        subTypes: [
          { id: 'bioluminescent_basins', name: 'Bioluminescent Basins', description: 'Fluorescent fungal groves', icon: '🍄', enabled: true, frequency: 1 },
          { id: 'crystal_flats', name: 'Silica Crystal Beds', description: 'Resonant crystalline fields', icon: '💎', enabled: true, frequency: 1 },
          { id: 'methane_seas', name: 'Methane Sludge Bays', description: 'Toxic gas estuaries', icon: '🧪', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'barren_wastes',
        name: 'Cratered Lunar Badlands',
        description: 'Airless, sun-bleached dust plains',
        hexColor: '#475569',
        iconColor: '#ffffff',
        icon: '🌑',
        frequency: 1,
        subTypes: [
          { id: 'impact_craters', name: 'Meteor Impact Basins', description: 'Deep glassified craters', icon: '☄️', enabled: true, frequency: 1 },
          { id: 'regolith_dunes', name: 'Dust Regolith Dunes', description: 'Low-gravity dust storms', icon: '💨', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'orbital_zones',
        name: 'Orbital & Transit Hubs',
        description: 'Spaceports, docks, and shipyards',
        hexColor: '#14b8a6',
        iconColor: '#000000',
        icon: '🛸',
        frequency: 1,
        subTypes: [
          { id: 'orbital_docks', name: 'Orbital Shipyards', description: 'Zero-g vessel assembly docks', icon: '🛰️', enabled: true, frequency: 1 },
          { id: 'launch_pads', name: 'Surface Launch Terminals', description: 'Heavy freighter pads', icon: '🚀', enabled: true, frequency: 1 }
        ]
      },
      {
        id: 'derelict_wastes',
        name: 'Derelict Ship Graveyards',
        description: 'Scrapped starships and radioactive wreckage',
        hexColor: '#292524',
        iconColor: '#ffffff',
        icon: '🛰️',
        frequency: 1,
        subTypes: [
          { id: 'hull_breach_fields', name: 'Hulk Debris Fields', description: 'Scattered starship hulls', icon: '🧲', enabled: true, frequency: 1 },
          { id: 'scrap_commons', name: 'Salvage Commons', description: 'Scavenger processing camps', icon: '🔧', enabled: true, frequency: 1 }
        ]
      }
    ],
    pois: [
      { name: 'The Colony / Outpost', icon: '🛸', color: '#06b6d4' },
      { name: 'The Derelict', icon: '🛰️', color: '#64748b' },
      { name: 'The Resource Site', icon: '⚡', color: '#eab308' },
      { name: 'The Anomaly', icon: '🌀', color: '#a855f7' }
    ],
    homeBase: {
      name: 'Command Hub / Safe Sector',
      icon: '⭐',
      color: '#06b6d4'
    }
  }
};