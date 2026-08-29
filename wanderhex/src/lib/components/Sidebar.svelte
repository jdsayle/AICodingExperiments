<script lang="ts">
  import { mapStore } from '../state/mapState.svelte';
  import { THEME_CATALOG } from '../themes/themeCatalog';
  import HexInspector from './HexInspector.svelte';
  import TileManagerModal from './TileManagerModal.svelte';
  import type { GridOrientation, FrequencyLevel } from '../types';

  let customSeedInput = $state(mapStore.seed);
  let isTileModalOpen = $state(false);
  let showSubTypes = $state(false); // Controls visibility of sub-types menu

  const themeList = Object.values(THEME_CATALOG);

  function handleThemeChange(e: Event) {
    const val = (e.target as HTMLSelectElement).value;
    mapStore.setTheme(val);
  }

  function handleBoundsChange(e: Event) {
    const size = parseInt((e.target as HTMLSelectElement).value, 10);
    mapStore.setGridDimensions(size, size);
  }

  function handleOrientationChange(e: Event) {
    const val = (e.target as HTMLSelectElement).value as GridOrientation;
    mapStore.setOrientation(val);
  }

  function handleGenerateNew() {
    mapStore.generateFresh();
    customSeedInput = mapStore.seed;
  }

  function handleCustomSeed() {
    mapStore.generateFresh(customSeedInput);
    customSeedInput = mapStore.seed;
  }

  function handleExportPNG() {
    const canvas = document.querySelector('canvas');
    if (!canvas) return;
    const link = document.createElement('a');
    link.download = `hexmap-${mapStore.themeId}-${mapStore.seed}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
  }
</script>

<aside id="sidebar">
  <div class="section header">
    <h1>Tactical Hex Engine</h1>
    <p class="subtitle">Multi-Genre Procedural Cartography</p>
  </div>

  <div class="section">
    <h2>World Genre & Theme</h2>
    <div class="control-group">
      <label for="themeSelect">Theme Preset</label>
      <select id="themeSelect" value={mapStore.themeId} onchange={handleThemeChange}>
        {#each themeList as theme}
          <option value={theme.id}>{theme.name}</option>
        {/each}
      </select>
    </div>

    <div class="section px-0 pb-0 border-none">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <h2>Terrain & Frequency</h2>
        <label style="font-size: 0.75rem; color: #94a3b8; display: flex; align-items: center; gap: 4px; cursor: pointer;">
          <input type="checkbox" bind:checked={showSubTypes} />
          Show Sub-Types
        </label>
      </div>
      
      <div class="sub-type-container">
        {#each mapStore.activeTheme.biomes as biome}
          <div class="biome-group" style="margin-bottom: 12px; border-bottom: 1px solid #242f3d; padding-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <span class="biome-title" style="margin-bottom: 0;">{@html biome.icon} {biome.name}</span>
              <div class="freq-picker">
                {#each [0, 1, 2, 3] as lvl}
                  <button
                    class="freq-btn {biome.frequency === lvl ? 'active' : ''}"
                    onclick={() => mapStore.setBiomeFrequency(biome.id, lvl as FrequencyLevel)}
                  >
                    {lvl}
                  </button>
                {/each}
              </div>
            </div>

            {#if showSubTypes && biome.frequency > 0}
              <div class="sub-type-list" style="padding-left: 16px; margin-top: 6px;">
                {#each biome.subTypes as st}
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                    <span style="font-size: 0.75rem; color: #cbd5e1;">{st.icon ?? '▫️'} {st.name}</span>
                    <div class="freq-picker">
                      {#each [0, 1, 2, 3] as lvl}
                        <button
                          class="freq-btn sub {st.frequency === lvl ? 'active-sub' : ''}"
                          onclick={() => mapStore.setSubTypeFrequency(biome.id, st.id, lvl as FrequencyLevel)}
                        >
                          {lvl}
                        </button>
                      {/each}
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    </div>

    <button class="btn-tile-mgr" onclick={() => (isTileModalOpen = true)}>
      🎨 Manage Custom Tile Textures
    </button>
  </div>

  <div class="section">
    <h2>Grid Geometry</h2>
    <div class="control-group">
      <label for="gridSize">Grid Bounds</label>
      <select id="gridSize" value={mapStore.gridCols} onchange={handleBoundsChange}>
        <option value={6}>6 x 6 Hexes (Compact)</option>
        <option value={7}>7 x 7 Hexes</option>
        <option value={8}>8 x 8 Hexes (Standard)</option>
        <option value={9}>9 x 9 Hexes</option>
        <option value={10}>10 x 10 Hexes (Large)</option>
      </select>
    </div>

    <div class="control-group">
      <label for="orientation">Alignment Orientation</label>
      <select id="orientation" value={mapStore.orientation} onchange={handleOrientationChange}>
        <option value="pointy">Pointy-Topped (Columns Aligned)</option>
        <option value="flat">Flat-Topped (Rows Aligned)</option>
      </select>
    </div>

    <div class="control-group">
      <label for="mapSeed">PRNG Seed</label>
      <input type="text" id="mapSeed" bind:value={customSeedInput} onchange={handleCustomSeed} />
    </div>

    <div class="btn-row">
      <button class="primary" onclick={handleGenerateNew}>Roll New Map</button>
      <button onclick={handleCustomSeed}>Apply Seed</button>
    </div>
  </div>

  <HexInspector />

  <div class="section export-section">
    <button class="primary export-btn" onclick={handleExportPNG}>Export Map as High-Res PNG</button>
  </div>
</aside>

<TileManagerModal isOpen={isTileModalOpen} onClose={() => (isTileModalOpen = false)} />

<style>
  #sidebar {
    width: 340px;
    min-width: 340px;
    max-width: 340px;
    background: var(--panel-bg, #111620);
    border-right: 1px solid var(--panel-border, #242f3d);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    z-index: 10;
    height: 100vh;
    box-sizing: border-box;
  }

  .section {
    padding: 16px;
    border-bottom: 1px solid var(--panel-border, #242f3d);
  }

  .header h1 {
    font-size: 1.15rem;
    color: #fff;
    margin-bottom: 4px;
  }

  .subtitle {
    font-size: 0.8rem;
    color: var(--text-muted, #94a3b8);
  }

  h2 {
    font-size: 0.8rem;
    color: var(--accent, #38bdf8);
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .biome-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-main, #e2e8f0);
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
  }
  
  .control-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 12px;
  }

  input, select, button {
    background: #1c2430;
    border: 1px solid var(--panel-border, #242f3d);
    color: var(--text-main, #e2e8f0);
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.85rem;
    outline: none;
    transition: all 0.15s ease;
  }

  input:focus, select:focus {
    border-color: var(--accent, #38bdf8);
  }

  .freq-picker {
    display: flex;
    gap: 2px;
  }

  .freq-btn {
    padding: 2px 6px;
    font-size: 0.7rem;
    border-radius: 4px;
    background: #1e293b;
    border: none;
    color: #64748b;
  }
  
  .freq-btn.sub {
    padding: 1px 4px;
    font-size: 0.65rem;
  }

  .freq-btn.active {
    background: #3b82f6;
    color: #fff;
    font-weight: bold;
  }

  .freq-btn.active-sub {
    background: #6366f1;
    color: #fff;
    font-weight: bold;
  }

  .btn-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 6px;
  }

  button {
    cursor: pointer;
    font-weight: 600;
  }

  button:hover {
    background: var(--panel-border, #242f3d);
  }

  button.primary {
    background: var(--success, #10b981);
    border-color: var(--success-hover, #059669);
    color: #fff;
  }

  button.primary:hover {
    background: var(--success-hover, #059669);
  }

  .btn-tile-mgr {
    width: 100%;
    margin-top: 4px;
    background: #1b2838;
    border-color: #2e4157;
    color: #7dd3fc;
  }

  .btn-tile-mgr:hover {
    background: #25374d;
  }

  .export-section {
    border-bottom: none;
    margin-top: auto;
  }

  .export-btn {
    width: 100%;
  }
</style>