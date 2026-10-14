import type { ThemeDefinition } from '../types';

export const THEME_CATALOG: Record<string, ThemeDefinition> = {
  post_apoc: {
    id: 'post_apoc',
    name: 'Post-Apocalyptic',
    biomes: [
      { id: 'postapoc_plains', name: 'Plains', description: 'Open expanses of waste and dirt', hexColor: '#CCFF00', iconColor: '#000000', icon: 'blighted_waste', frequency: 1 },
      { id: 'postapoc_desert', name: 'Desert', description: 'Sun-baked arid wasteland dunes', hexColor: '#382A25', iconColor: '#ffffff', icon: 'scorched_wasteland', frequency: 1 },
      { id: 'postapoc_forest_sparse', name: 'Forest - Sparse', description: 'Thinly scattered dead or mutated trees', hexColor: '#6B8E23', iconColor: '#000000', icon: 'mutated_forest', frequency: 1 },
      { id: 'postapoc_forest_dense', name: 'Forest - Dense', description: 'Thick overgrown mutated thickets', hexColor: '#1e532b', iconColor: '#ffffff', icon: 'resurgent_wilds', frequency: 1 },
      { id: 'postapoc_hills', name: 'Hills', description: 'Rolling mounds of rubble and dirt', hexColor: '#5C626D', iconColor: '#ffffff', icon: 'garbage_commons', frequency: 1 },
      { id: 'postapoc_hills_with_forest', name: 'Hills with Forest', description: 'Rubble hills choked with overgrowth', hexColor: '#3A506B', iconColor: '#ffffff', icon: 'toxic_zone', frequency: 1 },
      { id: 'postapoc_jungle', name: 'Jungle', description: 'Fleshy, humid biological infestation zones', hexColor: '#1A1625', iconColor: '#ffffff', icon: 'necrotic_sprawl', frequency: 1 },
      { id: 'postapoc_swamp', name: 'Swamp', description: 'Radioactive toxic fens and sludge pools', hexColor: '#3f6212', iconColor: '#ffffff', icon: 'choked_riverbed', frequency: 1 },
      { id: 'postapoc_mountain', name: 'Mountain', description: 'Towering jagged slag and concrete peaks', hexColor: '#64748b', iconColor: '#ffffff', icon: 'broken_highway', frequency: 1 },
      { id: 'postapoc_mountain_with_forest', name: 'Mountain with Forest', description: 'Rugged crags blanketed by mutated canopy', hexColor: '#334155', iconColor: '#ffffff', icon: 'slow_fire', frequency: 1 },
      { id: 'postapoc_water', name: 'Water', description: 'Choked waterways and chemical basins', hexColor: '#0284c7', iconColor: '#ffffff', icon: '🌊', frequency: 1 },
      { id: 'postapoc_sub_arctic', name: 'Sub-Arctic', description: 'Frozen fallout and nuclear winter zones', hexColor: '#cbd5e1', iconColor: '#000000', icon: '❄️', frequency: 1 }
    ],
    pois: [
      { name: 'The Ruins', icon: 'ruined_sprawl', color: '#71717a', description: 'Crumbled structures from a forgotten era, scavenged for lost tech.' },
      { name: 'The Survivor Settlement', icon: 'default_icon', color: '#10b981', description: 'A fortified outpost providing safe haven and trade opportunities.' },
      { name: 'The Wasteland Landmark', icon: 'toxic_zone', color: '#f59e0b', description: 'A distinct geographical feature emitting high levels of radiation.' },
      { name: 'The Resource Site', icon: 'garbage_commons', color: '#3b82f6', description: 'An area rich in raw scrap metal and usable industrial parts.' }
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
      { id: 'fantasy_plains', name: 'Plains', description: 'Verdant open downs and grasslands', hexColor: '#84cc16', iconColor: '#000000', icon: '🌾', frequency: 1 },
      { id: 'fantasy_desert', name: 'Desert', description: 'Vast sun-scorched sand dunes', hexColor: '#d97706', iconColor: '#000000', icon: '☀️', frequency: 1 },
      { id: 'fantasy_forest_sparse', name: 'Forest - Sparse', description: 'Open woodlands and light groves', hexColor: '#1e532b', iconColor: '#ffffff', icon: '🌲', frequency: 1 },
      { id: 'fantasy_forest_dense', name: 'Forest - Dense', description: 'Deep canopy ancient timberlands', hexColor: '#14532d', iconColor: '#ffffff', icon: '🌳', frequency: 1 },
      { id: 'fantasy_hills', name: 'Hills', description: 'Rolling grassy hills and barrows', hexColor: '#65a30d', iconColor: '#ffffff', icon: '⛰️', frequency: 1 },
      { id: 'fantasy_hills_with_forest', name: 'Hills with Forest', description: 'Wooded rolling uplands', hexColor: '#166534', iconColor: '#ffffff', icon: '🏕️', frequency: 1 },
      { id: 'fantasy_jungle', name: 'Jungle', description: 'Dense tropical canopies and vines', hexColor: '#065f46', iconColor: '#ffffff', icon: '🌴', frequency: 1 },
      { id: 'fantasy_swamp', name: 'Swamp', description: 'Boggy wetlands and treacherous fens', hexColor: '#3f6212', iconColor: '#ffffff', icon: '🐊', frequency: 1 },
      { id: 'fantasy_mountain', name: 'Mountain', description: 'Jagged snow-capped peaks', hexColor: '#64748b', iconColor: '#ffffff', icon: '🏔️', frequency: 1 },
      { id: 'fantasy_mountain_with_forest', name: 'Mountain with Forest', description: 'Highland slopes with pine timber', hexColor: '#475569', iconColor: '#ffffff', icon: '🌲', frequency: 1 },
      { id: 'fantasy_water', name: 'Water', description: 'Coastal waters, lakes, and rivers', hexColor: '#0284c7', iconColor: '#ffffff', icon: '🌊', frequency: 1 },
      { id: 'fantasy_sub_arctic', name: 'Sub-Arctic', description: 'Frozen tundras and glacial wastes', hexColor: '#e2e8f0', iconColor: '#000000', icon: '❄️', frequency: 1 }
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
      { id: 'scifi_plains', name: 'Plains', description: 'Flat cleared tarmac and flatlands', hexColor: '#475569', iconColor: '#ffffff', icon: '🪐', frequency: 1 },
      { id: 'scifi_desert', name: 'Desert', description: 'Cratered lunar dust badlands', hexColor: '#334155', iconColor: '#ffffff', icon: '🌑', frequency: 1 },
      { id: 'scifi_forest', name: 'Forest', description: 'Bioluminescent synthetic flora basins', hexColor: '#a855f7', iconColor: '#ffffff', icon: '🍄', frequency: 1 },
      { id: 'scifi_hills_natural', name: 'Hills - Natural', description: 'Untamed exo-terrain ridges', hexColor: '#64748b', iconColor: '#ffffff', icon: '⛰️', frequency: 1 },
      { id: 'scifi_hills_developed', name: 'Hills - Developed', description: 'Terraced platform foundations', hexColor: '#0284c7', iconColor: '#ffffff', icon: '🏗️', frequency: 1 },
      { id: 'scifi_city', name: 'City', description: 'High-density neon arcology towers', hexColor: '#0ea5e9', iconColor: '#ffffff', icon: '🏙️', frequency: 1 },
      { id: 'scifi_tech_district', name: 'Tech District', description: 'Data server farms and quantum hubs', hexColor: '#6366f1', iconColor: '#ffffff', icon: '💾', frequency: 1 },
      { id: 'scifi_slums', name: 'Slums', description: 'Sub-level neon-soaked alleys and shanties', hexColor: '#f97316', iconColor: '#000000', icon: '🚇', frequency: 1 },
      { id: 'scifi_mountains', name: 'Mountains', description: 'Towering mineral spires and ridges', hexColor: '#1e293b', iconColor: '#ffffff', icon: '⛰️', frequency: 1 },
      { id: 'scifi_water', name: 'Water', description: 'Methane seas and cooling coolant bays', hexColor: '#06b6d4', iconColor: '#000000', icon: '🧪', frequency: 1 }
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