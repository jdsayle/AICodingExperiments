<script lang="ts">
  import { mapStore, type BorderStyle } from '../state/mapState.svelte';
  import { THEME_CATALOG } from '../themes/themeCatalog';
  import TileManagerModal from './TileManagerModal.svelte';
  import type { GridOrientation, FrequencyLevel } from '../types';
  import { onMount, onDestroy } from 'svelte';

  let customSeedInput = $state(mapStore.seed);
  let isTileModalOpen = $state(false);

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

  function handleBorderStyleChange(e: Event) {
    const val = (e.target as HTMLSelectElement).value as BorderStyle;
    mapStore.setBorderStyle(val);
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

  // Global Keydown Listener for 'E' Key
  function handleGlobalKeyDown(e: KeyboardEvent) {
    const target = e.target as HTMLElement | null;
    if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)) {
      return;
    }
    if (e.key === 'e' || e.key === 'E') {
      e.preventDefault();
      mapStore.toggleEditMode();
    }
  }

  onMount(() => {
    window.addEventListener('keydown', handleGlobalKeyDown);
  });

  onDestroy(() => {
    window.removeEventListener('keydown', handleGlobalKeyDown);
  });
</script>

<aside id="sidebar">
  <div class="section header">
    <h1>Tactical Hex Engine</h1>
    <p class="subtitle">Multi-Genre Procedural Cartography</p>
  </div>

  <!-- Map Editing Mode Section -->
  <div class="section edit-mode-section" class:active-edit={mapStore.isEditing}>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
      <h2>Map Editor</h2>
      <button 
        type="button" 
        class="edit-toggle-btn {mapStore.isEditing ? 'active' : ''}" 
        onclick={() => mapStore.toggleEditMode()}
      >
        {mapStore.isEditing ? 'Exit Edit Mode' : 'Enter Edit Mode'} <kbd class="shortcut-tag">E</kbd>
      </button>
    </div>

    {#if mapStore.isEditing}
      <p class="edit-hint">Click any tile on the map to paint with the selected brush.</p>
      <div class="brush-palette">
        {#each mapStore.activeTheme.biomes as biome}
          <button
            type="button"
            class="brush-item {mapStore.selectedBrushBiomeId === biome.id ? 'selected' : ''}"
            onclick={() => mapStore.setBrushBiome(biome.id)}
            title={biome.name}
          >
            <span class="color-badge" style="background-color: {biome.hexColor};"></span>
            <span class="brush-name">{biome.name}</span>
          </button>
        {/each}
      </div>
    {/if}
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

    <!-- Roads & Rivers Sliders -->
    <div class="section px-0 pb-0 border-none" style="margin-top: 12px; border-top: 1px solid #242f3d; padding-top: 12px;">
      <h2>Linear Features (Roads & Rivers)</h2>
      
      <div class="control-group">
        <div style="display: flex; justify-content: space-between;">
          <label for="roadSlider">Road Network Level</label>
          <span class="level-indicator">{mapStore.roadLevel}</span>
        </div>
        <input
          id="roadSlider"
          type="range"
          min="0"
          max="3"
          step="1"
          value={mapStore.roadLevel}
          oninput={(e) => mapStore.setRoadLevel(parseInt(e.currentTarget.value, 10))}
        />
      </div>

      <div class="control-group">
        <div style="display: flex; justify-content: space-between;">
          <label for="riverSlider">River Network Level</label>
          <span class="level-indicator">{mapStore.riverLevel}</span>
        </div>
        <input
          id="riverSlider"
          type="range"
          min="0"
          max="3"
          step="1"
          value={mapStore.riverLevel}
          oninput={(e) => mapStore.setRiverLevel(parseInt(e.currentTarget.value, 10))}
        />
      </div>
    </div>

    <!-- Terrain Frequencies (Single-Tier) -->
    <div class="section px-0 pb-0 border-none">
      <h2>Terrain Frequencies</h2>
      <div class="terrain-frequency-container">
        {#each mapStore.activeTheme.biomes as biome}
          <div class="biome-group" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #242f3d; padding-bottom: 6px;">
            <span class="biome-title" style="margin-bottom: 0; font-size: 0.8rem;">{biome.name}</span>
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
        {/each}
      </div>
    </div>

    <button class="btn-tile-mgr" onclick={() => (isTileModalOpen = true)}>
      🎨 Manage Custom Tile Textures
    </button>
  </div>

  <div class="section">
    <h2>Grid Settings</h2>

    <div class="control-group toggle-group">
      <label for="showCoordinates" class="toggle-label">
        <input 
          type="checkbox" 
          id="showCoordinates" 
          bind:checked={mapStore.showCoordinates} 
        />
        <span>Show Hex Coordinates <kbd class="shortcut-tag">C</kbd></span>
      </label>
    </div>

    <div class="control-group">
      <label for="borderStyleSelect">Hex Border Style</label>
      <select id="borderStyleSelect" value={mapStore.borderStyle} onchange={handleBorderStyleChange}>
        <option value="standard">Standard (Medium)</option>
        <option value="subtle">Subtle (Faint)</option>
      </select>
    </div>

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

  .edit-mode-section {
    background: rgba(16, 185, 129, 0.03);
    transition: background 0.2s ease;
  }

  .edit-mode-section.active-edit {
    background: rgba(16, 185, 129, 0.08);
    border-left: 3px solid #10b981;
  }

  .edit-toggle-btn {
    font-size: 0.75rem;
    padding: 4px 8px;
    background: #1e293b;
    border: 1px solid #334155;
    color: #94a3b8;
    border-radius: 4px;
    cursor: pointer;
  }

  .edit-toggle-btn.active {
    background: #10b981;
    color: #fff;
    border-color: #059669;
    font-weight: bold;
  }

  .edit-hint {
    font-size: 0.75rem;
    color: #34d399;
    margin-bottom: 8px;
    font-style: italic;
  }

  .brush-palette {
    display: flex;
    flex-direction: column;
    gap: 4px;
    max-height: 180px;
    overflow-y: auto;
    padding-right: 4px;
  }

  .brush-item {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #182230;
    border: 1px solid #242f3d;
    padding: 6px 8px;
    border-radius: 4px;
    cursor: pointer;
    text-align: left;
    width: 100%;
    color: #cbd5e1;
    font-size: 0.8rem;
  }

  .brush-item:hover {
    background: #223043;
    border-color: #38bdf8;
  }

  .brush-item.selected {
    background: #0f3d31;
    border-color: #10b981;
    color: #fff;
    font-weight: 600;
  }

  .color-badge {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    flex-shrink: 0;
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

  .level-indicator {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--accent, #38bdf8);
  }

  .biome-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-main, #e2e8f0);
    display: flex;
    align-items: center;
    gap: 6px;
  }
  
  .control-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 12px;
  }

  .toggle-group {
    margin-bottom: 14px;
  }

  .toggle-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    color: var(--text-main, #e2e8f0);
    cursor: pointer;
  }

  .shortcut-tag {
    background: #1e293b;
    border: 1px solid #334155;
    color: #94a3b8;
    border-radius: 4px;
    padding: 1px 5px;
    font-size: 0.7rem;
    font-family: monospace;
    margin-left: 4px;
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

  input[type="range"] {
    accent-color: var(--accent, #38bdf8);
    cursor: pointer;
    padding: 0;
  }

  input[type="checkbox"] {
    width: auto;
    padding: 0;
    cursor: pointer;
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
    cursor: pointer;
  }

  .freq-btn.active {
    background: #3b82f6;
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