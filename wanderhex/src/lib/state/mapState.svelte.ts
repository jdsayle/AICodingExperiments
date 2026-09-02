import { THEME_CATALOG } from '../themes/themeCatalog';
import type {
  ThemeDefinition,
  BiomeDefinition,
  HexData,
  GridOrientation,
  FrequencyLevel
} from '../types';
import { calculateHexGeometry, getRectHexCenter, getHexCorners } from '../math/hexMath';

export interface CanonicalEdge {
  id: string;
  hexA: { col: number; row: number };
  hexB?: { col: number; row: number };
  edgeIndexA: number;
  hasRoad: boolean;
  hasRiver: boolean;
  roadOffset?: number;
  riverOffset?: number;
  v1Key: string;
  v2Key: string;
}

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

  roadLevel = $state<number>(0);
  riverLevel = $state<number>(0);

  hexes = $state<HexData[]>([]);
  canonicalEdges = $state<CanonicalEdge[]>([]);
  hoveredHex = $state<HexData | null>(null);

  curves = $state<never[]>([]);

  showCoordinates = $state<boolean>(true);
  isHudMinimized = $state<boolean>(false);

  constructor() {
    this.generateFresh();
  }

  toggleCoordinates() {
    this.showCoordinates = !this.showCoordinates;
  }

  toggleHud() {
    this.isHudMinimized = !this.isHudMinimized;
  }

  setTheme(id: string) {
    if (this.themes[id]) {
      this.themeId = id;
      this.activeTheme = JSON.parse(JSON.stringify(this.themes[id]));
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

  getBiomeConfig(biomeId: string): BiomeDefinition | undefined {
    return this.activeTheme.biomes.find((b) => b.id === biomeId);
  }

  setRoadLevel(lvl: number) {
    this.roadLevel = lvl;
    this.rebuildEdgeFeatures();
  }

  setRiverLevel(lvl: number) {
    this.riverLevel = lvl;
    this.rebuildEdgeFeatures();
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
    const homeBaseDef = this.activeTheme.homeBase;

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const q = this.orientation === 'pointy' ? c - Math.floor(r / 2) : c;
        const rCoord = this.orientation === 'pointy' ? r : r - Math.floor(c / 2);
        const s = -q - rCoord;

        const activeBiomes = this.activeTheme.biomes.filter((b) => b.frequency > 0);
        let selectedBiomeId = fallbackBiome.id;
        let selectedSubTypeId = fallbackBiome.id;

        if (activeBiomes.length > 0) {
          const biomePool = activeBiomes.map((biome) => ({
            biome,
            weight: FREQUENCY_WEIGHTS[biome.frequency as FrequencyLevel]
          }));

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
          selectedSubTypeId = selectedBiomeId;

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
          hasPoi: false,
          edgeFeatures: []
        });
      }
    }

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

    this.hexes = newHexes;
    this.hoveredHex = null;
    this.rebuildEdgeFeatures();
  };

  rebuildEdgeFeatures() {
    const edgeMap = new Map<string, CanonicalEdge>();

    const geo = calculateHexGeometry(this.orientation, 50);
    const vertexPositions = new Map<string, { x: number; y: number }>();

    const getVertexKey = (x: number, y: number) => {
      const rx = Math.round(x * 10) / 10;
      const ry = Math.round(y * 10) / 10;
      const key = `${rx},${ry}`;
      if (!vertexPositions.has(key)) {
        vertexPositions.set(key, { x: rx, y: ry });
      }
      return key;
    };

    const getEdgeKey = (c1: number, r1: number, e1: number) => {
      let c2 = c1;
      let r2 = r1;

      const offsetsPointy = [[0, -1], [1, 0], [1, 1], [0, 1], [-1, 0], [0, -1]];
      const offset = offsetsPointy[e1];
      c2 += offset[0];
      r2 += offset[1];

      const k1 = `${c1},${r1}`;
      const k2 = `${c2},${r2}`;
      const edgeId = k1 < k2 ? `${k1}:${k2}` : `${k2}:${k1}`;

      if (!edgeMap.has(edgeId)) {
        const center = getRectHexCenter(c1, r1, geo, this.orientation, 0, 0);
        const corners = getHexCorners(center, geo.radius, this.orientation);

        const p1 = corners[e1];
        const p2 = corners[(e1 + 1) % 6];

        const v1Key = getVertexKey(p1.x, p1.y);
        const v2Key = getVertexKey(p2.x, p2.y);

        edgeMap.set(edgeId, {
          id: edgeId,
          hexA: { col: c1, row: r1 },
          hexB: (c2 >= 0 && c2 < this.gridCols && r2 >= 0 && r2 < this.gridRows) ? { col: c2, row: r2 } : undefined,
          edgeIndexA: e1,
          hasRoad: false,
          hasRiver: false,
          v1Key,
          v2Key
        });
      }
      return edgeMap.get(edgeId)!;
    };

    for (const hex of this.hexes) {
      for (let e = 0; e < 6; e++) {
        getEdgeKey(hex.col, hex.row, e);
      }
    }

    const allEdges = Array.from(edgeMap.values());
    const vertexToEdgesMap = new Map<string, CanonicalEdge[]>();

    allEdges.forEach(edge => {
      if (!vertexToEdgesMap.has(edge.v1Key)) vertexToEdgesMap.set(edge.v1Key, []);
      if (!vertexToEdgesMap.has(edge.v2Key)) vertexToEdgesMap.set(edge.v2Key, []);
      vertexToEdgesMap.get(edge.v1Key)!.push(edge);
      vertexToEdgesMap.get(edge.v2Key)!.push(edge);
    });

    const generateVertexWalkPath = (level: number, subSeedOffset: number): CanonicalEdge[] => {
      if (level === 0 || allEdges.length === 0) return [];

      const rng = createPrng(this.seed + subSeedOffset);

      let mainTargetLength = 0;
      if (level === 1) mainTargetLength = Math.floor(rng() * 3) + 4;
      else if (level === 2) mainTargetLength = Math.floor(rng() * 4) + 8;
      else if (level === 3) mainTargetLength = Math.floor(rng() * 5) + 12;

      const visitedEdges = new Set<string>();
      const visitedVertices = new Set<string>();
      const path: CanonicalEdge[] = [];

      let startEdge = allEdges[Math.floor(rng() * allEdges.length)];
      visitedEdges.add(startEdge.id);
      visitedVertices.add(startEdge.v1Key);
      visitedVertices.add(startEdge.v2Key);
      path.push(startEdge);

      let currentVertexKey = rng() < 0.5 ? startEdge.v1Key : startEdge.v2Key;
      let prevVertexKey = currentVertexKey === startEdge.v1Key ? startEdge.v2Key : startEdge.v1Key;

      const pStart = vertexPositions.get(prevVertexKey)!;
      const pCurr = vertexPositions.get(currentVertexKey)!;
      let generalDx = pCurr.x - pStart.x;
      let generalDy = pCurr.y - pStart.y;

      const stepWalk = (
        currKey: string,
        pKey: string,
        targetSteps: number,
        avoidPathEdges: Set<string>,
        allowVertexRevisit = false
      ): { steppedEdges: CanonicalEdge[]; lastVertexKey: string } => {
        const walked: CanonicalEdge[] = [];
        let cKey = currKey;

        for (let i = 0; i < targetSteps; i++) {
          const candidateEdges = (vertexToEdgesMap.get(cKey) || []).filter(edge => {
            if (avoidPathEdges.has(edge.id) || visitedEdges.has(edge.id)) return false;
            const nextKey = edge.v1Key === cKey ? edge.v2Key : edge.v1Key;
            if (!allowVertexRevisit && visitedVertices.has(nextKey)) return false;
            return true;
          });

          if (candidateEdges.length === 0) break;

          const scoredCandidates = candidateEdges.map(edge => {
            const nextKey = edge.v1Key === cKey ? edge.v2Key : edge.v1Key;
            const pC = vertexPositions.get(cKey)!;
            const pN = vertexPositions.get(nextKey)!;

            const stepDx = pN.x - pC.x;
            const stepDy = pN.y - pC.y;

            const dot = stepDx * generalDx + stepDy * generalDy;
            return { edge, nextKey, dot };
          });

          // Sort candidates strictly by dot product (forward movement momentum)
          scoredCandidates.sort((a, b) => b.dot - a.dot);

          // Pick forward-facing step
          const chosen = scoredCandidates[0];

          visitedEdges.add(chosen.edge.id);
          visitedVertices.add(chosen.nextKey);
          walked.push(chosen.edge);

          cKey = chosen.nextKey;
        }

        return { steppedEdges: walked, lastVertexKey: cKey };
      };

      const mainResult = stepWalk(currentVertexKey, prevVertexKey, mainTargetLength - 1, new Set());
      path.push(...mainResult.steppedEdges);

      if (level === 3 && path.length >= 3) {
        const forkStartIndex = Math.floor(rng() * (path.length - 2)) + 1;
        const forkEdge = path[forkStartIndex];

        const forkVertexKey = rng() < 0.5 ? forkEdge.v1Key : forkEdge.v2Key;
        const forkPrevVertexKey = forkVertexKey === forkEdge.v1Key ? forkEdge.v2Key : forkEdge.v1Key;

        const mainPathEdgeIds = new Set(path.map(e => e.id));
        const forkTargetLength = Math.max(2, Math.floor(path.length * 0.4));

        const pF1 = vertexPositions.get(forkPrevVertexKey)!;
        const pF2 = vertexPositions.get(forkVertexKey)!;

        generalDx = -(pF2.y - pF1.y);
        generalDy = pF2.x - pF1.x;
        if (rng() < 0.5) {
          generalDx = -generalDx;
          generalDy = -generalDy;
        }

        const forkResult = stepWalk(forkVertexKey, forkPrevVertexKey, forkTargetLength, mainPathEdgeIds, true);
        path.push(...forkResult.steppedEdges);
      }

      return path;
    };

    // Separate seed offsets ensure road slider adjustments do not mutate river generation
    const roadEdges = generateVertexWalkPath(this.roadLevel, 1000);
    roadEdges.forEach(e => (e.hasRoad = true));

    const riverEdges = generateVertexWalkPath(this.riverLevel, 2000);
    riverEdges.forEach(e => (e.hasRiver = true));

    edgeMap.forEach(edge => {
      if (edge.hasRoad && edge.hasRiver) {
        edge.roadOffset = -2;
        edge.riverOffset = 2;
      } else {
        edge.roadOffset = 0;
        edge.riverOffset = 0;
      }
    });

    this.canonicalEdges = Array.from(edgeMap.values());
  }
}

export const mapStore = new MapStateStore();