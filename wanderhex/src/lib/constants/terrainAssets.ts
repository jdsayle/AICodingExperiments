// Import Fantasy Pointy-Topped Terrain Assets (800x924)
import imgFantasyPlains from '../../assets/terrains/modern/pointy/fantasy/1_fantasy_pointy_plains.png';
import imgFantasyDesert from '../../assets/terrains/modern/pointy/fantasy/2_fantasy_pointy_desert.png';
import imgFantasyForestSparse from '../../assets/terrains/modern/pointy/fantasy/3a_fantasy_pointy_sparse.png';
import imgFantasyForestDense from '../../assets/terrains/modern/pointy/fantasy/3b_fantasy_pointy_dense.png';
import imgFantasyHills from '../../assets/terrains/modern/pointy/fantasy/4_fantasy_pointy_hills.png';
import imgFantasyHillsWithForest from '../../assets/terrains/modern/pointy/fantasy/4_fantasy_pointy_hills_w_forest.png';
import imgFantasyJungle from '../../assets/terrains/modern/pointy/fantasy/5_fantasy_pointy_jungle.png';
import imgFantasySwamp from '../../assets/terrains/modern/pointy/fantasy/6_fantasy_pointy_swamp.png';
import imgFantasyMountain from '../../assets/terrains/modern/pointy/fantasy/7_fantasy_pointy_mountain.png';
import imgFantasyMountainWithForest from '../../assets/terrains/modern/pointy/fantasy/7_fantasy_pointy_mountain_w_forest.png';
import imgFantasyWater from '../../assets/terrains/modern/pointy/fantasy/8_fantasy_pointy_water.png';
import imgFantasySubArctic from '../../assets/terrains/modern/pointy/fantasy/9_fantasy_pointy_subarctic.png';

export const TERRAIN_ASSET_MAP: Record<string, Record<string, Record<string, string>>> = {
  fantasy: {
    pointy: {
      fantasy_plains: imgFantasyPlains,
      fantasy_desert: imgFantasyDesert,
      fantasy_forest_sparse: imgFantasyForestSparse,
      fantasy_forest_dense: imgFantasyForestDense,
      fantasy_hills: imgFantasyHills,
      fantasy_hills_with_forest: imgFantasyHillsWithForest,
      fantasy_jungle: imgFantasyJungle,
      fantasy_swamp: imgFantasySwamp,
      fantasy_mountain: imgFantasyMountain,
      fantasy_mountain_with_forest: imgFantasyMountainWithForest,
      fantasy_water: imgFantasyWater,
      fantasy_sub_arctic: imgFantasySubArctic,
    },
    flat: {
      // Add your 924x800 flat-topped assets here when ready
    }
  },
  post_apoc: {
    pointy: {},
    flat: {}
  },
  sci_fi: {
    pointy: {},
    flat: {}
  }
};