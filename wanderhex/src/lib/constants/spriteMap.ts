export interface SpriteCoord {
  col: number; // 0 to 3
  row: number; // 0 to 3
}

export const SPRITE_MAP: Record<string, SpriteCoord> = {
  // Shattered Cities / Urban
  broken_highway: { col: 0, row: 2 },
  ruined_sprawl: { col: 2, row: 1 },
  garbage_commons: { col: 3, row: 1 },
  
  // Techno-Ruins & Hazards
  toxic_zone: { col: 0, row: 1 },
  slow_fire: { col: 1, row: 1 },
  radioactive_badlands: { col: 0, row: 0 },

  // Blights & Wastes
  blighted_waste: { col: 2, row: 0 },
  plains_of_glass: { col: 1, row: 0 },
  scorched_wasteland: { col: 1, row: 2 },
  black_dust: { col: 2, row: 2 },
  choked_riverbed: { col: 3, row: 2 },

  // Mutated & Bio
  mutated_forest: { col: 0, row: 3 },
  resurgent_wilds: { col: 1, row: 3 },
  necrotic_sprawl: { col: 2, row: 3 },
  dormant_megafauna: { col: 3, row: 3 },

  // Default / Fallback
  default_icon: { col: 3, row: 0 }
};