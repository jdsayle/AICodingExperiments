import { THEME_CATALOG } from '../themes/themeCatalog';
import type {
  ThemeDefinition,
  BiomeDefinition,
  HexData,
  POIData,
  SplineCurve,
  GridOrientation,
  FrequencyLevel
} from '../types';

function createPrng(seed: number) {
  let s = seed >>> 0;
  return function () {
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const FREQUENCY_WEIGHTS: Record<FrequencyLevel, number> = {
  0: 0,
  1: 1,
  2: 4,
  3: 10
};

export class MapStateStore {
  themes: Record<string, ThemeDefinition> = THEME_CATALOG;
  themeId = $state<string>('post_apoc');
  activeTheme = $state<ThemeDefinition>(THEME_CATALOG.post_apoc);

  customOverrides = $state<Record<string, string>>({});

  gridCols = $state<number>(6);
  gridRows = $state<number>(6);
  orientation = $state<GridOrientation>('pointy');
  seed = $state<number>(12345);

  hexes = $state<HexData[]>([]);
  curves = $state<SplineCurve[]>([]);
  hoveredHex = $state<HexData | null>(null);

  constructor() {
    this.generateFresh();
  }

  setTheme(id: string) {
    if (this.themes[id]) {
      this.themeId = id;
      this.activeTheme = JSON.parse(JSON.stringify(this.themes[id]));
      // Initialize frequencies if missing from catalog definition
      this.activeTheme.biomes.forEach(b => {
        if (b.frequency === undefined) b.frequency = 1;
        b.subTypes.forEach(st => {
          if (st.frequency === undefined) st.frequency = 1;
        });
      });
      this.generateFresh(this.seed);
    }
  }

  setGridDimensions(cols: number, rows: number) {
    this.gridCols = cols;
    this.gridRows = rows;
    this.generateFresh(this.seed);
  }

  setOrientation(newOrientation: GridOrientation) {
    this.orientation = newOrientation;
    this.generateFresh(this.seed);
  }

  setBiomeFrequency(biomeId: string, level: FrequencyLevel) {
    const biome = this.activeTheme.biomes.find((b) => b.id === biomeId);
    if (biome) {
      biome.frequency = level;
      this.generateFresh(this.seed);
    }
  }

  setSubTypeFrequency(biomeId: string, subTypeId: string, level: FrequencyLevel) {
    const biome = this.activeTheme.biomes.find((b) => b.id === biomeId);
    if (biome) {
      const sub = biome.subTypes.find((st) => st.id === subTypeId);
      if (sub) {
        sub.frequency = level;
        this.generateFresh(this.seed);
      }
    }
  }

  setCustomOverride(subTypeId: string, color: string) {
    this.customOverrides[subTypeId] = color;
  }

  getBiomeConfig(biomeId: string): BiomeDefinition | undefined {
    return this.activeTheme.biomes.find((b) => b.id === biomeId);
  }

  generateFresh = (customSeed?: number | string) => {
    if (customSeed !== undefined) {
      const parsed = typeof customSeed === 'string' ? parseInt(customSeed, 10) : customSeed;
      this.seed = isNaN(parsed) ? Math.floor(Math.random() * 100000) : parsed;
    } else {
      this.seed = Math.floor(Math.random() * 100000);
    }

    const rng = createPrng(this.seed);
    const newHexes: HexData[] = [];
    const cols = this.gridCols;
    const rows = this.gridRows;

    const fallbackBiome = this.activeTheme.biomes[0];
    const pois = this.activeTheme.pois;
    const homeBaseDef = this.activeTheme.homeBase;

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const q = this.orientation === 'pointy' ? c - Math.floor(r / 2) : c;
        const rCoord = this.orientation === 'pointy' ? r : r - Math.floor(c / 2);
        const s = -q - rCoord;

        // Collect generated neighbor biomes for clumping bias
        const neighbors = this.orientation === 'pointy' 
          ? [[c-1, r], [c-1, r-1], [c, r-1], [c+1, r], [c, r+1], [c-1, r+1]]
          : [[c-1, r], [c, r-1], [c+1, r-1], [c+1, r], [c, r+1], [c-1, r+1]];
          
        const neighborBiomes = neighbors
          .map(n => newHexes.find(h => h.col === n[0] && h.row === n[1])?.biomeId)
          .filter(Boolean) as string[];

        const activeBiomes = this.activeTheme.biomes.filter((b) => b.frequency > 0);
        let selectedBiomeId = fallbackBiome.id;
        let selectedSubTypeId = fallbackBiome.id;

        if (activeBiomes.length > 0) {
          const biomePool = activeBiomes.map((biome) => {
            let weight = FREQUENCY_WEIGHTS[biome.frequency as FrequencyLevel];
            const matchingNeighbors = neighborBiomes.filter((id) => id === biome.id).length;
            weight += matchingNeighbors * 3; // Clumping modifier
            return { biome, weight };
          });

          const totalWeight = biomePool.reduce((acc, item) => acc + item.weight, 0);
          let randomVal = rng() * totalWeight;
          let selectedBiome = biomePool[0].biome;

          for (const item of biomePool) {
            if (randomVal < item.weight) {
              selectedBiome = item.biome;
              break;
            }
            randomVal -= item.weight;
          }
          selectedBiomeId = selectedBiome.id;

          const activeSubTypes = selectedBiome.subTypes.filter((st) => st.frequency > 0);
          selectedSubTypeId = selectedBiomeId; // Fallback

          if (activeSubTypes.length > 0) {
            const subTypePool = activeSubTypes.map((st) => ({
              st,
              weight: FREQUENCY_WEIGHTS[st.frequency as FrequencyLevel]
            }));
            const totalSubWeight = subTypePool.reduce((acc, item) => acc + item.weight, 0);
            let subRandom = rng() * totalSubWeight;

            for (const item of subTypePool) {
              if (subRandom < item.weight) {
                selectedSubTypeId = item.st.id;
                break;
              }
              subRandom -= item.weight;
            }
          }
        }

        newHexes.push({
          q,
          r: rCoord,
          s,
          col: c,
          row: r,
          categoryId: selectedBiomeId,
          subTypeId: selectedSubTypeId,
          biomeId: selectedBiomeId,
          seed: this.seed,
          hasPoi: false
        });
      }
    }

    // Place Home Base
    if (newHexes.length > 0) {
      const homeIndex = Math.floor(rng() * newHexes.length);
      const targetHex = newHexes[homeIndex];
      targetHex.hasPoi = true;
      targetHex.isHomeBase = true;
      targetHex.poiType = homeBaseDef.name;
      targetHex.poiDescription = `Player starting safe zone: ${homeBaseDef.name}.`;
      targetHex.poi = {
        type: homeBaseDef.name,
        description: targetHex.poiDescription,
        icon: homeBaseDef.icon,
        color: homeBaseDef.color
      };
    }

    // Place Non-Home Base POIs
    if (pois.length > 0) {
      const maxDim = Math.max(cols, rows);
      let minPois = 2;
      let maxPois = 3;
      let uniqueChance = 0.70;

      if (maxDim >= 9) {
        minPois = 2;
        maxPois = 5;
        uniqueChance = 0.90;
      }

      const poiCount = Math.floor(rng() * (maxPois - minPois + 1)) + minPois;
      const availableHexes = newHexes.filter((h) => !h.isHomeBase);

      // Fisher-Yates shuffle to pick distinct locations
      for (let i = availableHexes.length - 1; i > 0; i--) {
        const j = Math.floor(rng() * (i + 1));
        [availableHexes[i], availableHexes[j]] = [availableHexes[j], availableHexes[i]];
      }

      const selectedLocations = availableHexes.slice(0, Math.min(poiCount, availableHexes.length));
      const placedPoiNames: string[] = [];

      for (const hex of selectedLocations) {
        const unplacedPois = pois.filter((p) => !placedPoiNames.includes(p.name));
        let selectedPoiDef = pois[0];

        if (unplacedPois.length > 0 && rng() < uniqueChance) {
          selectedPoiDef = unplacedPois[Math.floor(rng() * unplacedPois.length)];
        } else {
          selectedPoiDef = pois[Math.floor(rng() * pois.length)];
        }

        placedPoiNames.push(selectedPoiDef.name);
        hex.hasPoi = true;
        hex.poiType = selectedPoiDef.name;
        hex.poiDescription = `${selectedPoiDef.name} situated in the region.`;
        hex.poi = {
          type: selectedPoiDef.name,
          description: hex.poiDescription,
          icon: selectedPoiDef.icon,
          color: selectedPoiDef.color
        };
      }
    }

    this.hexes = newHexes;
    this.hoveredHex = null;
    this.generateCurves();
  };

  generateCurves = () => {
    this.curves = [];
  };
}

export const mapStore = new MapStateStore();