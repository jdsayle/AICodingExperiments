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

import imgPostApocPlains from '../../assets/terrains/modern/pointy/postapoc/1a_postapoc_pointy_plains.png';
import imgPostApocBlightedWastes from '../../assets/terrains/modern/pointy/postapoc/1b_postapoc_pointy_blightedwastes.png';
import imgPostApocDesert from '../../assets/terrains/modern/pointy/postapoc/2_postapoc_pointy_desert.png';
import imgPostApocForestSparse from '../../assets/terrains/modern/pointy/postapoc/3a_postapoc_pointy_sparse.png';
import imgPostApocForestDense from '../../assets/terrains/modern/pointy/postapoc/3b_postapoc_pointy_dense.png';
import imgPostApocHills from '../../assets/terrains/modern/pointy/postapoc/4_postapoc_pointy_hills.png';
import imgPostApocHillsWithForest from '../../assets/terrains/modern/pointy/postapoc/4_postapoc_pointy_hills_w_forest.png';
import imgPostApocJungle from '../../assets/terrains/modern/pointy/postapoc/5_postapoc_pointy_jungle.png';
import imgPostApocSwamp from '../../assets/terrains/modern/pointy/postapoc/6_postapoc_pointy_swamp.png';
import imgPostApocMountain from '../../assets/terrains/modern/pointy/postapoc/7_postapoc_pointy_mountain.png';
import imgPostApocWater from '../../assets/terrains/modern/pointy/postapoc/8_postapoc_pointy_water.png';
import imgPostApocSubArctic from '../../assets/terrains/modern/pointy/postapoc/9_postapoc_pointy_subarctic.png';

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
    pointy: {
      postapoc_plains: imgPostApocPlains,
      postapoc_blightedwastes: imgPostApocBlightedWastes,
      postapoc_desert: imgPostApocDesert,
      postapoc_forest_sparse: imgPostApocForestSparse,
      postapoc_forest_dense: imgPostApocForestDense,
      postapoc_hills: imgPostApocHills,
      postapoc_hills_with_forest: imgPostApocHillsWithForest,
      postapoc_jungle: imgPostApocJungle,
      postapoc_swamp: imgPostApocSwamp,
      postapoc_mountain: imgPostApocMountain,
      postapoc_water: imgPostApocWater,
      postapoc_sub_arctic: imgPostApocSubArctic,
    },
    flat: {}
  },
  sci_fi: {
    pointy: {},
    flat: {}
  }
};