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

<aside id="sidebar" class="w-[340px] min-w-[340px] max-w-[340px] bg-[var(--panel-bg)] border-r border-[var(--panel-border)] flex flex-col overflow-y-auto overflow-x-hidden z-10 h-screen box-border select-none pr-1">
  <div class="p-4 border-b border-[var(--panel-border)]">
    <h1 class="text-base font-bold text-[var(--text-main)] mb-1 tracking-wide">Tactical Hex Engine</h1>
    <p class="text-[0.75rem] text-[var(--text-muted)] tracking-wider uppercase font-medium">Multi-Genre Procedural Cartography</p>
  </div>

  <!-- Map Editing Mode Section -->
  <div class="p-4 border-b border-[var(--panel-border)] transition-colors duration-200 {mapStore.isEditing ? 'bg-emerald-500/10 border-l-4 border-l-[var(--success)]' : 'bg-transparent'}">
    <div class="flex justify-between items-center mb-2">
      <h2 class="text-xs font-bold text-[var(--accent)] uppercase tracking-wider">Map Editor</h2>
      <button 
        type="button" 
        class="text-[0.8rem] px-2.5 py-1 bg-[var(--panel-border)] border border-[var(--panel-border-hover)] text-[var(--text-muted)] rounded transition-all cursor-pointer hover:text-[var(--text-main)] {mapStore.isEditing ? '!bg-[var(--success)] !text-white !border-[var(--success-hover)] font-bold shadow-sm' : ''}" 
        style="font-family: var(--font-scifi-body), sans-serif !important; font-size: 0.8rem !important;"
        onclick={() => mapStore.toggleEditMode()}
      >
        {mapStore.isEditing ? 'Exit Edit Mode' : 'Enter Edit Mode'} <kbd class="bg-[var(--bg-color)] border border-[var(--panel-border)] text-[var(--text-muted)] rounded px-1.5 py-0.5 text-[0.75rem] font-mono ml-1">E</kbd>
      </button>
    </div>

    {#if mapStore.isEditing}
      <p class="text-[0.75rem] text-[var(--success)] mb-2 italic">Click any tile on the map to paint with the selected brush.</p>
      <div class="flex flex-col gap-1.5 max-h-[180px] overflow-y-auto pr-1">
        {#each mapStore.activeTheme.biomes as biome}
          <button
            type="button"
            class="flex items-center gap-2.5 bg-[var(--bg-color)] border border-[var(--panel-border)] px-2.5 py-1.5 rounded cursor-pointer text-left w-full text-[var(--text-main)] text-[0.85rem] transition-colors hover:border-[var(--accent)] hover:bg-[var(--panel-border)] {mapStore.selectedBrushBiomeId === biome.id ? '!bg-[var(--success)]/20 !border-[var(--success)] !text-white font-semibold' : ''}"
            onclick={() => mapStore.setBrushBiome(biome.id)}
            title={biome.name}
          >
            <span class="w-3.5 h-3.5 rounded-sm flex-shrink-0" style="background-color: {biome.hexColor};"></span>
            <span class="truncate">{biome.name}</span>
          </button>
        {/each}
      </div>
    {/if}
  </div>

  <div class="p-4 border-b border-[var(--panel-border)]">
    <h2 class="text-xs font-bold text-[var(--accent)] uppercase tracking-wider mb-2.5">World Genre & Theme</h2>
    <div class="flex flex-col gap-1.5 mb-3.5">
      <label for="themeSelect" class="text-[0.75rem] font-medium text-[var(--text-muted)]">Theme Preset</label>
      <select id="themeSelect" class="bg-[var(--bg-color)] border border-[var(--panel-border)] text-[var(--text-main)] px-3 py-2 rounded-md text-[0.85rem] outline-none transition-colors focus:border-[var(--accent)] cursor-pointer" value={mapStore.themeId} onchange={handleThemeChange}>
        {#each themeList as theme}
          <option value={theme.id}>{theme.name}</option>
        {/each}
      </select>
    </div>

    <!-- Roads & Rivers Sliders -->
    <div class="mt-3.5 pt-3.5 border-t border-[var(--panel-border)]">
      <h2 class="text-xs font-bold text-[var(--accent)] uppercase tracking-wider mb-2.5">Linear Features (Roads & Rivers)</h2>
      
      <div class="flex flex-col gap-1.5 mb-3.5">
        <div class="flex justify-between items-center">
          <label for="roadSlider" class="text-[0.75rem] font-medium text-[var(--text-muted)]">Road Network Level</label>
          <span class="text-[0.85rem] font-bold text-[var(--accent)]">{mapStore.roadLevel}</span>
        </div>
        <input
          id="roadSlider"
          type="range"
          min="0"
          max="3"
          step="1"
          class="accent-[var(--accent)] cursor-pointer"
          value={mapStore.roadLevel}
          oninput={(e) => mapStore.setRoadLevel(parseInt(e.currentTarget.value, 10))}
        />
      </div>

      <div class="flex flex-col gap-1.5 mb-3.5">
        <div class="flex justify-between items-center">
          <label for="riverSlider" class="text-[0.75rem] font-medium text-[var(--text-muted)]">River Network Level</label>
          <span class="text-[0.85rem] font-bold text-[var(--accent)]">{mapStore.riverLevel}</span>
        </div>
        <input
          id="riverSlider"
          type="range"
          min="0"
          max="3"
          step="1"
          class="accent-[var(--accent)] cursor-pointer"
          value={mapStore.riverLevel}
          oninput={(e) => mapStore.setRiverLevel(parseInt(e.currentTarget.value, 10))}
        />
      </div>
    </div>

    <!-- Terrain Frequencies (Single-Tier) -->
    <div class="mt-3.5 pt-3.5 border-t border-[var(--panel-border)]">
      <h2 class="text-xs font-bold text-[var(--accent)] uppercase tracking-wider mb-2.5">Terrain Frequencies</h2>
      <div class="flex flex-col gap-2">
        {#each mapStore.activeTheme.biomes as biome}
          <div class="flex justify-between items-center border-b border-[var(--panel-border)]/50 pb-2 last:border-none">
            <span class="text-[0.85rem] font-semibold text-[var(--text-main)] flex items-center gap-1.5">{biome.name}</span>
            <div class="flex gap-1 bg-[var(--bg-color)] p-0.5 rounded border border-[var(--panel-border)]">
              {#each [0, 1, 2, 3] as lvl}
                <button
                  type="button"
                  class="px-2 py-0.5 text-[0.75rem] rounded bg-transparent border-none text-[var(--text-muted)] cursor-pointer transition-colors hover:text-[var(--text-main)] {biome.frequency === lvl ? '!bg-[var(--accent)] !text-white font-bold shadow-xs' : ''}"
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
  </div>

  <div class="p-4 border-b border-[var(--panel-border)]">
    <h2 class="text-xs font-bold text-[var(--accent)] uppercase tracking-wider mb-2.5">Grid Settings</h2>

    <div class="flex flex-col gap-1.5 mb-3.5">
      <label for="showCoordinates" class="flex items-center gap-2.5 text-[0.85rem] font-medium text-[var(--text-main)] cursor-pointer">
        <input 
          type="checkbox" 
          id="showCoordinates" 
          class="accent-[var(--accent)] cursor-pointer w-4 h-4"
          bind:checked={mapStore.showCoordinates} 
        />
        <span>Show Hex Coordinates <kbd class="bg-[var(--bg-color)] border border-[var(--panel-border)] text-[var(--text-muted)] rounded px-1.5 py-0.5 text-[0.7rem] font-mono ml-1">C</kbd></span>
      </label>
    </div>

    <div class="flex flex-col gap-1.5 mb-3.5">
      <label for="borderStyleSelect" class="text-[0.75rem] font-medium text-[var(--text-muted)]">Hex Border Style</label>
      <select id="borderStyleSelect" class="bg-[var(--bg-color)] border border-[var(--panel-border)] text-[var(--text-main)] px-3 py-2 rounded-md text-[0.85rem] outline-none transition-colors focus:border-[var(--accent)] cursor-pointer" value={mapStore.borderStyle} onchange={handleBorderStyleChange}>
        <option value="standard">Standard (Medium)</option>
        <option value="subtle">Subtle (Faint)</option>
      </select>
    </div>

    <div class="flex flex-col gap-1.5 mb-3.5">
      <label for="gridSize" class="text-[0.75rem] font-medium text-[var(--text-muted)]">Grid Bounds</label>
      <select id="gridSize" class="bg-[var(--bg-color)] border border-[var(--panel-border)] text-[var(--text-main)] px-3 py-2 rounded-md text-[0.85rem] outline-none transition-colors focus:border-[var(--accent)] cursor-pointer" value={mapStore.gridCols} onchange={handleBoundsChange}>
        <option value={6}>6 x 6 Hexes (Compact)</option>
        <option value={7}>7 x 7 Hexes</option>
        <option value={8}>8 x 8 Hexes (Standard)</option>
        <option value={9}>9 x 9 Hexes</option>
        <option value={10}>10 x 10 Hexes (Large)</option>
      </select>
    </div>

    <div class="flex flex-col gap-1.5 mb-3.5">
      <label for="orientation" class="text-[0.75rem] font-medium text-[var(--text-muted)]">Alignment Orientation</label>
      <select id="orientation" class="bg-[var(--bg-color)] border border-[var(--panel-border)] text-[var(--text-main)] px-3 py-2 rounded-md text-[0.85rem] outline-none transition-colors focus:border-[var(--accent)] cursor-pointer" value={mapStore.orientation} onchange={handleOrientationChange}>
        <option value="pointy">Pointy-Topped (Columns Aligned)</option>
        <option value="flat">Flat-Topped (Rows Aligned)</option>
      </select>
    </div>

    <div class="flex flex-col gap-1.5 mb-3.5">
      <label for="mapSeed" class="text-[0.75rem] font-medium text-[var(--text-muted)]">PRNG Seed</label>
      <input type="text" id="mapSeed" class="bg-[var(--bg-color)] border border-[var(--panel-border)] text-[var(--text-main)] px-3 py-2 rounded-md text-[0.85rem] outline-none transition-colors focus:border-[var(--accent)]" bind:value={customSeedInput} onchange={handleCustomSeed} />
    </div>

    <div class="grid grid-cols-2 gap-2.5 mt-3">
      <button type="button" class="bg-[var(--success)] hover:bg-[var(--success-hover)] text-white font-bold py-2 px-3 rounded-md text-[0.85rem] cursor-pointer transition-colors shadow-sm" onclick={handleGenerateNew}>Roll New Map</button>
      <button type="button" class="bg-[var(--bg-color)] border border-[var(--panel-border)] hover:bg-[var(--panel-border)] text-[var(--text-main)] font-bold py-2 px-3 rounded-md text-[0.85rem] cursor-pointer transition-colors" onclick={handleCustomSeed}>Apply Seed</button>
    </div>
  </div>

  <div class="p-4 mt-auto">
    <button type="button" class="w-full bg-[var(--success)] hover:bg-[var(--success-hover)] text-white font-bold py-2.5 px-4 rounded-md text-[0.85rem] cursor-pointer transition-colors shadow-sm" onclick={handleExportPNG}>Export Map as High-Res PNG</button>
  </div>
</aside>

<TileManagerModal isOpen={isTileModalOpen} onClose={() => (isTileModalOpen = false)} />

<style>
  #sidebar {
    width: 340px;
    min-width: 340px;
    max-width: 340px;
    height: 100vh;
    box-sizing: border-box;
  }
</style>