export type GridOrientation = 'pointy' | 'flat';

export interface Point2D {
  x: number;
  y: number;
}

// export interface SubTypeDefinition {
//   id: string;
//   name: string;
//   description: string;
//   icon?: string;
//   enabled: boolean;
// }

// export interface BiomeDefinition {
//   id: string;
//   name: string;
//   description: string;
//   hexColor: string;
//   iconColor: string;
//   icon: string;
//   subTypes: SubTypeDefinition[];
// }

export type FrequencyLevel = 0 | 1 | 2 | 3;

export interface SubTypeDefinition {
  id: string;
  name: string;
  description: string;
  icon?: string;
  enabled: boolean;
  frequency: FrequencyLevel; // 0 = None, 1 = Low (1-3), 2 = Med (4-7), 3 = High (8+)
}

export interface BiomeDefinition {
  id: string;
  name: string;
  description: string;
  hexColor: string;
  iconColor: string;
  icon: string;
  frequency: FrequencyLevel; // Setting parent to 0 blocks all child sub-types
  subTypes: SubTypeDefinition[];
}

export interface POIDefinition {
  name: string;
  icon: string;
  color: string;
  description?: string;
}

export interface HomeBaseDefinition {
  name: string;
  icon: string;
  color: string;
}

export interface ThemeDefinition {
  id: string;
  name: string;
  biomes: BiomeDefinition[];
  pois: POIDefinition[];
  homeBase: HomeBaseDefinition;
}

export interface POIData {
  type: string;
  description: string;
  icon: string;
  color: string;
}

export type EdgeFeatureKind = 'road' | 'river' | 'water' | 'wall';

export interface EdgeFeature {
  id: string;
  kind: EdgeFeatureKind;
  edgeIndex: number;
  opacity: number;
  color: string;
  width: number;
}

export interface HexData {
  q: number;
  r: number;
  s: number;
  col: number;
  row: number;
  categoryId: string;
  subTypeId: string;
  biomeId: string;
  seed: number;
  hasPoi: boolean;
  isHomeBase?: boolean;
  poiType?: string;
  poiDescription?: string;
  poi?: POIData;
  edgeFeatures?: EdgeFeature[];
}

export interface SplineCurve {
  id: string;
  type: 'river' | 'highway';
  points: Point2D[];
  width?: number;
}