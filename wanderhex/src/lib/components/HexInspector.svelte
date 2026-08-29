<!-- <script lang="ts">
  import { mapStore } from '../state/mapState.svelte';

  const hoveredHex = $derived(mapStore.hoveredHex);
  
  const biome = $derived(
    hoveredHex
      ? mapStore.activeTheme.biomes.find(b => b.id === hoveredHex.biomeId)
      : null
  );

  const subType = $derived(
    biome && hoveredHex
      ? biome.subTypes.find(st => st.id === hoveredHex.subTypeId)
      : null
  );
</script>

<div class="inspector-section">
  <h3>Hex Inspector</h3>
  {#if hoveredHex && biome}
    <div class="inspector-card">
      <div class="inspector-header">
        <span class="color-badge" style="background: {biome.hexColor};"></span>
        <span class="biome-name">{biome.icon} {biome.name}</span>
      </div>
      <p class="biome-desc">{biome.description}</p>

      {#if subType}
        <div class="subtype-block">
          <span class="subtype-name">{subType.icon ?? '▫️'} {subType.name}</span>
          <p class="subtype-desc">{subType.description}</p>
        </div>
      {/if}

      <div class="data-row">
        <span class="data-label">Coordinates:</span>
        <span class="data-value">[Col {hoveredHex.col}, Row {hoveredHex.row}]</span>
      </div>
      <div class="data-row">
        <span class="data-label">Point of Interest:</span>
        <span class="data-value">{hoveredHex.poi ? hoveredHex.poi.type : 'None'}</span>
      </div>
    </div>
  {:else}
    <div class="empty-state">
      <p>Hover over any hex on the grid to inspect tactical biome data.</p>
    </div>
  {/if}
</div>

<style>
  .inspector-section {
    padding: 16px;
    border-bottom: 1px solid var(--panel-border, #242f3d);
    flex: 1;
  }

  h3 {
    font-size: 0.8rem;
    color: var(--accent, #38bdf8);
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .inspector-card {
    background: #0d121c;
    border: 1px solid var(--panel-border, #242f3d);
    border-radius: 6px;
    padding: 12px;
  }

  .inspector-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: bold;
    font-size: 0.95rem;
    color: #fff;
    margin-bottom: 6px;
  }

  .color-badge {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid rgba(0, 0, 0, 0.4);
    flex-shrink: 0;
  }

  .biome-desc {
    font-size: 0.8rem;
    color: var(--text-muted, #94a3b8);
    margin-bottom: 10px;
    line-height: 1.3;
  }

  .subtype-block {
    margin-bottom: 10px;
    padding: 8px;
    background: rgba(255, 255, 255, 0.03);
    border-left: 2px solid var(--accent, #38bdf8);
    border-radius: 0 4px 4px 0;
  }

  .subtype-name {
    display: block;
    font-size: 0.85rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 2px;
  }

  .subtype-desc {
    font-size: 0.75rem;
    color: #94a3b8;
    margin: 0;
    line-height: 1.25;
  }

  .data-row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 0.8rem;
  }

  .data-row:last-child {
    border-bottom: none;
  }

  .data-label {
    color: var(--text-muted, #94a3b8);
  }

  .data-value {
    font-weight: 600;
    color: #fff;
  }

  .empty-state p {
    font-size: 0.8rem;
    color: var(--text-muted, #94a3b8);
    font-style: italic;
  }
</style> -->

<script lang="ts">
  import { mapStore } from '../state/mapState.svelte';
  import SpriteIcon from './SpriteIcon.svelte';

  const hoveredHex = $derived(mapStore.hoveredHex);
  
  const biome = $derived(
    hoveredHex
      ? mapStore.activeTheme.biomes.find(b => b.id === hoveredHex.biomeId)
      : null
  );

  const subType = $derived(
    biome && hoveredHex
      ? biome.subTypes.find(st => st.id === hoveredHex.subTypeId)
      : null
  );
</script>

<div class="inspector-section">
  <h3>Hex Inspector</h3>
  {#if hoveredHex && biome}
    <div class="inspector-card">
      <div class="inspector-header">
        <span class="color-badge" style="background: {biome.hexColor};"></span>
        <SpriteIcon name={biome.icon} size={20} />
        <span class="biome-name">{biome.name}</span>
      </div>
      <p class="biome-desc">{biome.description}</p>

      {#if subType}
        <div class="subtype-block">
          <div class="subtype-header">
            {#if subType.icon}
              <SpriteIcon name={subType.icon} size={16} />
            {/if}
            <span class="subtype-name">{subType.name}</span>
          </div>
          <p class="subtype-desc">{subType.description}</p>
        </div>
      {/if}

      <div class="data-row">
        <span class="data-label">Coordinates:</span>
        <span class="data-value">[Col {hoveredHex.col}, Row {hoveredHex.row}]</span>
      </div>
      <div class="data-row">
        <span class="data-label">Point of Interest:</span>
        <span class="data-value">{hoveredHex.poi ? hoveredHex.poi.type : 'None'}</span>
      </div>
    </div>
  {:else}
    <div class="empty-state">
      <p>Hover over any hex on the grid to inspect tactical biome data.</p>
    </div>
  {/if}
</div>

<style>
  .inspector-section {
    padding: 16px;
    border-bottom: 1px solid var(--panel-border, #242f3d);
    flex: 1;
  }

  h3 {
    font-size: 0.8rem;
    color: var(--accent, #38bdf8);
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .inspector-card {
    background: #0d121c;
    border: 1px solid var(--panel-border, #242f3d);
    border-radius: 6px;
    padding: 12px;
  }

  .inspector-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: bold;
    font-size: 0.95rem;
    color: #fff;
    margin-bottom: 6px;
  }

  .color-badge {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    border: 1px solid rgba(0, 0, 0, 0.4);
    flex-shrink: 0;
  }

  .biome-desc {
    font-size: 0.8rem;
    color: var(--text-muted, #94a3b8);
    margin-bottom: 10px;
    line-height: 1.3;
  }

  .subtype-block {
    margin-bottom: 10px;
    padding: 8px;
    background: rgba(255, 255, 255, 0.03);
    border-left: 2px solid var(--accent, #38bdf8);
    border-radius: 0 4px 4px 0;
  }

  .subtype-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 2px;
  }

  .subtype-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #e2e8f0;
  }

  .subtype-desc {
    font-size: 0.75rem;
    color: #94a3b8;
    margin: 0;
    line-height: 1.25;
  }

  .data-row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    font-size: 0.8rem;
  }

  .data-row:last-child {
    border-bottom: none;
  }

  .data-label {
    color: var(--text-muted, #94a3b8);
  }

  .data-value {
    font-weight: 600;
    color: #fff;
  }

  .empty-state p {
    font-size: 0.8rem;
    color: var(--text-muted, #94a3b8);
    font-style: italic;
  }
</style>