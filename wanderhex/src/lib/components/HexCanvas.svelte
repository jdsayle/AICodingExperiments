<script lang="ts">
  import { onMount } from 'svelte';
  import { mapStore } from '../state/mapState.svelte';
  import { calculateHexGeometry, getRectHexCenter, getHexCorners, isPointInPolygon } from '../math/hexMath';
  import { drawOrganicSpline } from '../math/splineMath';
  import { THEME_CATALOG } from '../themes/themeCatalog';
  import { SPRITE_MAP } from '../constants/spriteMap';
  import spriteSheetUrl from '../../assets/icons.jpg';

  let canvasEl = $state<HTMLCanvasElement | null>(null);
  let containerEl = $state<HTMLDivElement | null>(null);

  // Preload the Sprite Sheet Image
  let spriteSheet = $state<HTMLImageElement | null>(null);

  // --- Pan & Zoom Transform State ---
  let zoomScale = $state<number>(1);
  let panOffset = $state<{ x: number; y: number }>({ x: 0, y: 0 });
  let isDragging = $state<boolean>(false);
  let dragStart = { x: 0, y: 0 };

  const MIN_ZOOM = 1;
  const MAX_ZOOM = 4;
  const ZOOM_STEP = 0.25;

  // --- HUD State ---
  let isHudMinimized = $state<boolean>(false);

  // Title Case helper function for formatting text in HexInspector HUD
  function toTitleCase(str: string): string {
    if (!str) return '';

    return str
      // Split camelCase words (e.g., 'ruinedSprawl' -> 'ruined Sprawl')
      .replace(/([a-z])([A-Z])/g, '$1 $2')
      // Replace underscores and hyphens with spaces (e.g., 'shattered_city' -> 'shattered city')
      .replace(/[_]+/g, ' ')
      // Capitalize the first letter of each word while preserving symbols like '/' or '-'
      .replace(/\b[a-z]/g, (letter) => letter.toUpperCase());
  }

  // Derived active hex details for the HUD
  const activeHexInfo = $derived.by(() => {
    if (!mapStore.hoveredHex) return null;

    const hex = mapStore.hoveredHex;
    const biome = mapStore.getBiomeConfig(hex.biomeId);
    const catalogTheme = THEME_CATALOG[mapStore.themeId];
    const catalogBiome = catalogTheme?.biomes.find((b) => b.id === hex.biomeId);
    const subType = catalogBiome?.subTypes.find((st) => st.id === hex.subTypeId);

    const iconKey = subType?.icon || biome?.icon || '';

    // Extract poi to a local variable for strict null checks
    const poi = hex.poi;

    // If POI is present on the hex
    if (poi) {
      const rawPoi = poi as unknown as Record<string, unknown>;
      const poiType = typeof rawPoi.type === 'string' ? rawPoi.type : null;
      const poiName = typeof rawPoi.name === 'string' ? rawPoi.name : null;
      const poiDesc = typeof rawPoi.description === 'string' ? rawPoi.description : '';

      const catalogPoi = catalogTheme?.pois?.find(
        (p) => p.icon === poi.icon || (poiType && p.name === poiType)
      );

      const rawPoiDisplayName = catalogPoi?.name || poiName || poiType || poi.icon || 'Unknown POI';

      return {
        col: hex.col,
        row: hex.row,
        biomeName: biome?.name ?? 'Unknown Biome',
        hasPoi: true,
        poiName: toTitleCase(String(rawPoiDisplayName)),
        description: poiDesc || catalogPoi?.description || ''
      };
    }

    // Standard Hex Layout
    return {
      col: hex.col,
      row: hex.row,
      biomeName: biome?.name ?? 'Unknown Biome',
      hasPoi: false,
      mainFeature: toTitleCase(iconKey),
      description: subType?.description ?? ''
    };
  });

  function toggleHud() {
    isHudMinimized = !isHudMinimized;
  }

  function handleKeyDown(e: KeyboardEvent) {
    const target = e.target as HTMLElement | null;
    if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)) {
      return;
    }

    if (e.key === 'i' || e.key === 'I') {
      e.preventDefault();
      toggleHud();
    }
  }

  onMount(() => {
    const img = new Image();
    img.src = spriteSheetUrl;
    img.onload = () => {
      spriteSheet = img;
      render();
    };

    window.addEventListener('resize', render);
    window.addEventListener('keydown', handleKeyDown);

    render();
    return () => {
      window.removeEventListener('resize', render);
      window.removeEventListener('keydown', handleKeyDown);
    };
  });

  function clampPan(x: number, y: number, scale: number): { x: number; y: number } {
    if (!canvasEl) return { x: 0, y: 0 };
    
    const maxPanX = (canvasEl.width * (scale - 1)) / 2;
    const maxPanY = (canvasEl.height * (scale - 1)) / 2;

    return {
      x: Math.max(-maxPanX, Math.min(maxPanX, x)),
      y: Math.max(-maxPanY, Math.min(maxPanY, y))
    };
  }

  function handleZoom(deltaScale: number, mouseCanvasX?: number, mouseCanvasY?: number) {
    if (!canvasEl) return;

    const oldScale = zoomScale;
    const newScale = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, oldScale + deltaScale));

    if (newScale === oldScale) return;

    if (newScale === 1) {
      zoomScale = 1;
      panOffset = { x: 0, y: 0 };
      render();
      return;
    }

    const targetX = mouseCanvasX ?? canvasEl.width / 2;
    const targetY = mouseCanvasY ?? canvasEl.height / 2;

    const factor = newScale / oldScale;
    const newPanX = targetX - factor * (targetX - panOffset.x);
    const newPanY = targetY - factor * (targetY - panOffset.y);

    zoomScale = newScale;
    panOffset = clampPan(newPanX, newPanY, newScale);
    render();
  }

  function resetZoom() {
    zoomScale = 1;
    panOffset = { x: 0, y: 0 };
    render();
  }

  function handleWheel(e: WheelEvent) {
    e.preventDefault();
    if (!canvasEl) return;

    const rect = canvasEl.getBoundingClientRect();
    const mouseX = (e.clientX - rect.left) * (canvasEl.width / rect.width);
    const mouseY = (e.clientY - rect.top) * (canvasEl.height / rect.height);

    const delta = e.deltaY < 0 ? ZOOM_STEP : -ZOOM_STEP;
    handleZoom(delta, mouseX, mouseY);
  }

  function handleMouseDown(e: MouseEvent) {
    if (e.button !== 0 || zoomScale === 1) return;
    isDragging = true;
    dragStart = { x: e.clientX - panOffset.x, y: e.clientY - panOffset.y };
  }

  function handleMouseMove(e: MouseEvent) {
    if (!canvasEl || !containerEl) return;

    if (isDragging) {
      const rawX = e.clientX - dragStart.x;
      const rawY = e.clientY - dragStart.y;
      panOffset = clampPan(rawX, rawY, zoomScale);
      render();
    }

    const rect = canvasEl.getBoundingClientRect();
    const rawMouseX = (e.clientX - rect.left) * (canvasEl.width / rect.width);
    const rawMouseY = (e.clientY - rect.top) * (canvasEl.height / rect.height);

    const centerX = canvasEl.width / 2;
    const centerY = canvasEl.height / 2;

    const mousePt = {
      x: (rawMouseX - centerX - panOffset.x) / zoomScale + centerX,
      y: (rawMouseY - centerY - panOffset.y) / zoomScale + centerY
    };

    const { gridCols, gridRows, orientation, hexes } = mapStore;
    const sidePadding = 48;
    const maxW = (containerEl.clientWidth || 800) - sidePadding * 2;
    const maxH = (containerEl.clientHeight || 800) - sidePadding * 2;

    let hexRadius = orientation === 'pointy'
      ? Math.min(maxW / ((gridCols + 0.5) * Math.sqrt(3)), maxH / (gridRows * 1.5 + 0.5))
      : Math.min(maxW / (gridCols * 1.5 + 0.5), maxH / ((gridRows + 0.5) * Math.sqrt(3)));

    hexRadius = Math.max(24, Math.min(65, hexRadius));
    const geo = calculateHexGeometry(orientation, hexRadius);
    const originX = sidePadding + geo.width / 2;
    const originY = sidePadding + geo.height / 2;

    let found: typeof hexes[0] | null = null;
    for (const hex of hexes) {
      const center = getRectHexCenter(hex.col, hex.row, geo, orientation, originX, originY);
      const corners = getHexCorners(center, geo.radius, orientation);
      if (isPointInPolygon(mousePt, corners)) {
        found = hex;
        break;
      }
    }
    mapStore.hoveredHex = found;
  }

  function handleMouseUp() {
    isDragging = false;
  }

  function handleMouseLeave() {
    isDragging = false;
    mapStore.hoveredHex = null;
  }

  function render() {
    if (!canvasEl || !containerEl) return;
    const ctx = canvasEl.getContext('2d');
    if (!ctx) return;

    const { gridCols, gridRows, orientation, hexes, curves, hoveredHex, customOverrides } = mapStore;
    const sidePadding = 48;
    const maxW = (containerEl.clientWidth || 800) - sidePadding * 2;
    const maxH = (containerEl.clientHeight || 800) - sidePadding * 2;

    let hexRadius = orientation === 'pointy'
      ? Math.min(maxW / ((gridCols + 0.5) * Math.sqrt(3)), maxH / (gridRows * 1.5 + 0.5))
      : Math.min(maxW / (gridCols * 1.5 + 0.5), maxH / ((gridRows + 0.5) * Math.sqrt(3)));

    hexRadius = Math.max(24, Math.min(65, hexRadius));

    const geo = calculateHexGeometry(orientation, hexRadius);
    const totalW = orientation === 'pointy'
      ? (gridCols + 0.5) * geo.xSpacing
      : (gridCols - 1) * geo.xSpacing + geo.width;
    const totalH = orientation === 'pointy'
      ? (gridRows - 1) * geo.ySpacing + geo.height
      : (gridRows + 0.5) * geo.ySpacing;

    canvasEl.width = Math.max(300, totalW + sidePadding * 2);
    canvasEl.height = Math.max(300, totalH + sidePadding * 2);

    const originX = sidePadding + geo.width / 2;
    const originY = sidePadding + geo.height / 2;

    ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);

    ctx.save();
    const centerX = canvasEl.width / 2;
    const centerY = canvasEl.height / 2;

    ctx.translate(centerX + panOffset.x, centerY + panOffset.y);
    ctx.scale(zoomScale, zoomScale);
    ctx.translate(-centerX, -centerY);

    ctx.imageSmoothingEnabled = false;

    // 1. Base Hex Tiles & Bitmap Overlay
    hexes.forEach((hex) => {
      const biome = mapStore.getBiomeConfig(hex.biomeId);
      const center = getRectHexCenter(hex.col, hex.row, geo, orientation, originX, originY);
      const corners = getHexCorners(center, geo.radius - 1, orientation);

      ctx.save();
      ctx.beginPath();
      ctx.moveTo(corners[0].x, corners[0].y);
      for (let i = 1; i < 6; i++) {
        ctx.lineTo(corners[i].x, corners[i].y);
      }
      ctx.closePath();
      ctx.clip();

      const override = customOverrides[hex.subTypeId] || customOverrides[hex.biomeId];
      if (override) {
        ctx.fillStyle = override;
        ctx.fill();
      } else {
        const hexColor = biome?.hexColor ?? '#86efac';
        const iconColor = biome?.iconColor ?? '#166534';
        
        const catalogBiome = THEME_CATALOG[mapStore.themeId]?.biomes.find(b => b.id === hex.biomeId);
        const subType = catalogBiome?.subTypes.find(st => st.id === hex.subTypeId);
        
        const iconKey = subType?.icon || biome?.icon || '';

        ctx.fillStyle = hexColor;
        ctx.fill();

        if (iconKey) {
          const coord = SPRITE_MAP[iconKey];

          if (coord && spriteSheet) {
            const tileSize = spriteSheet.width / 4;
            const sourceX = coord.col * tileSize;
            const sourceY = coord.row * tileSize;

            const renderSize = Math.round(geo.radius * 0.9);
            const drawX = center.x - renderSize / 2;
            const drawY = center.y - renderSize / 2;

            ctx.drawImage(
              spriteSheet,
              sourceX, sourceY, tileSize, tileSize,
              drawX, drawY, renderSize, renderSize
            );
          } else {
            ctx.fillStyle = iconColor;
            ctx.font = `bold ${Math.round(geo.radius * 0.7)}px sans-serif`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(iconKey, center.x, center.y + 2);
          }
        }
      }

      ctx.restore();

      // Hex Borders & Hover State
      ctx.beginPath();
      ctx.moveTo(corners[0].x, corners[0].y);
      for (let i = 1; i < 6; i++) {
        ctx.lineTo(corners[i].x, corners[i].y);
      }
      ctx.closePath();

      const isHovered = hoveredHex && hoveredHex.col === hex.col && hoveredHex.row === hex.row;
      ctx.strokeStyle = isHovered ? '#38bdf8' : 'rgba(0, 0, 0, 0.35)';
      ctx.lineWidth = isHovered ? 3 / zoomScale : 1.2 / zoomScale;
      ctx.stroke();

      // Coordinate Label (Renders conditionally based on store toggle)
      if (mapStore.showCoordinates) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.65)';
        ctx.font = `${Math.max(9, Math.round(geo.radius * 0.22))}px monospace`;
        ctx.textAlign = 'center';
        ctx.fillText(`${hex.col},${hex.row}`, center.x, center.y - geo.radius * 0.52);
      }
    });

    // 2. Organic Spline Curves
    curves.forEach((curve) => {
      ctx.save();
      ctx.beginPath();
      drawOrganicSpline(ctx, curve.points, 0.6);

      if (curve.type === 'river') {
        ctx.strokeStyle = '#0284c7';
        ctx.lineWidth = curve.width || 4;
        ctx.stroke();
      } else if (curve.type === 'highway') {
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = curve.width || 3;
        ctx.stroke();
      }
      ctx.restore();
    });

    // 3. POI Tokens
    hexes.forEach((hex) => {
      if (!hex.poi) return;
      const center = getRectHexCenter(hex.col, hex.row, geo, orientation, originX, originY);
      const poiRadius = Math.max(12, geo.radius * 0.35);

      ctx.beginPath();
      ctx.arc(center.x, center.y + geo.radius * 0.25, poiRadius, 0, Math.PI * 2);
      ctx.fillStyle = hex.poi.color;
      ctx.fill();
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2 / zoomScale;
      ctx.stroke();

      const coord = SPRITE_MAP[hex.poi.icon];
      if (coord && spriteSheet) {
        const tileSize = spriteSheet.width / 4;
        const sourceX = coord.col * tileSize;
        const sourceY = coord.row * tileSize;
        const iconSize = poiRadius * 1.2;
        ctx.drawImage(
          spriteSheet,
          sourceX, sourceY, tileSize, tileSize,
          center.x - iconSize / 2, (center.y + geo.radius * 0.25) - iconSize / 2, iconSize, iconSize
        );
      } else {
        ctx.font = `bold ${Math.round(poiRadius * 0.9)}px sans-serif`;
        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(hex.poi.icon, center.x, center.y + geo.radius * 0.25 + 1);
      }
    });

    ctx.restore();
  }

  $effect(() => {
    const _ = {
      theme: mapStore.themeId,
      cols: mapStore.gridCols,
      rows: mapStore.gridRows,
      orient: mapStore.orientation,
      hexes: mapStore.hexes,
      curves: mapStore.curves,
      hover: mapStore.hoveredHex,
      overrides: mapStore.customOverrides,
      showCoordinates: mapStore.showCoordinates,
      sheet: spriteSheet,
      zoom: zoomScale,
      pan: panOffset
    };
    render();
  });
</script>

<div class="viewport" bind:this={containerEl}>
  <!-- Top-Right Zoom Controls -->
  <div class="zoom-controls">
    <button type="button" class="zoom-btn" onclick={() => handleZoom(ZOOM_STEP)} title="Zoom In">+</button>
    <span class="zoom-level">{Math.round(zoomScale * 100)}%</span>
    <button type="button" class="zoom-btn" onclick={() => handleZoom(-ZOOM_STEP)} title="Zoom Out">−</button>
    <button type="button" class="reset-btn" onclick={resetZoom} title="Reset View">Reset</button>
  </div>

  <!-- Bottom-Left Floating Map HUD Panel -->
  {#if isHudMinimized}
    <button
      type="button"
      class="hud-pill"
      onclick={toggleHud}
      title="Expand Inspector (Press 'I')"
    >
      <span class="hud-pill-icon">ℹ</span>
      <span class="hud-pill-label">Inspect</span>
    </button>
  {:else}
    <div class="hex-hud">
      <div class="hud-header">
        <span class="hud-title">Hex Inspector</span>
        <button
          type="button"
          class="hud-toggle-btn"
          onclick={toggleHud}
          title="Minimize Inspector (Press 'I')"
        >
          −
        </button>
      </div>

      <div class="hud-body">
        {#if activeHexInfo}
          <div class="hud-row">
            <span class="hud-label">Tile:</span>
            <span class="hud-coord">({activeHexInfo.col}, {activeHexInfo.row})</span>
          </div>
          
          <div class="hud-row">
            <span class="hud-label">Biome:</span>
            <span class="hud-value">{activeHexInfo.biomeName}</span>
          </div>

          {#if activeHexInfo.hasPoi}
            <!-- POI Specific Layout -->
            <div class="hud-row">
              <span class="hud-label">POI:</span>
              <span class="hud-poi-val">{activeHexInfo.poiName}</span>
            </div>
          {:else}
            <!-- Standard Hex Layout -->
            {#if activeHexInfo.mainFeature}
              <div class="hud-row">
                <span class="hud-label">Main Feature:</span>
                <span class="hud-icon-val">{activeHexInfo.mainFeature}</span>
              </div>
            {/if}
          {/if}

          <!-- Description (POI Description or Sub-type Description) -->
          {#if activeHexInfo.description}
            <div class="hud-description">
              {activeHexInfo.description}
            </div>
          {/if}
        {:else}
          <div class="hud-placeholder">
            Hover over a hex for more info
          </div>
        {/if}
      </div>
    </div>
  {/if}

  <canvas
    bind:this={canvasEl}
    class:grab={zoomScale > 1 && !isDragging}
    class:grabbing={isDragging}
    onwheel={handleWheel}
    onmousedown={handleMouseDown}
    onmousemove={handleMouseMove}
    onmouseup={handleMouseUp}
    onmouseleave={handleMouseLeave}
  ></canvas>
</div>

<style>
  .viewport {
    flex: 1;
    width: 100%;
    height: 100%;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #080c14;
    overflow: hidden;
  }

  /* Top-Right Floating Controls */
  .zoom-controls {
    position: absolute;
    top: 16px;
    right: 16px;
    z-index: 20;
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(16, 22, 34, 0.85);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 6px 10px;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
    user-select: none;
  }

  .zoom-btn, .reset-btn {
    background: #1e293b;
    color: #f8fafc;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.15s ease, transform 0.05s ease;
  }

  .zoom-btn {
    width: 28px;
    height: 28px;
    font-size: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .reset-btn {
    padding: 0 8px;
    height: 28px;
    font-size: 12px;
  }

  .zoom-btn:hover, .reset-btn:hover {
    background: #334155;
    border-color: #38bdf8;
  }

  .zoom-btn:active, .reset-btn:active {
    transform: scale(0.95);
  }

  .zoom-level {
    color: #94a3b8;
    font-size: 12px;
    font-family: monospace;
    min-width: 38px;
    text-align: center;
  }

  /* Bottom-Left Floating HUD Overlay */
  .hex-hud {
    position: absolute;
    bottom: 16px;
    left: 16px;
    z-index: 20;
    width: 240px;
    background: rgba(16, 22, 34, 0.85);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 10px 12px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
    color: #f8fafc;
    user-select: none;
    pointer-events: auto;
  }

  .hud-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    padding-bottom: 4px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .hud-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #38bdf8;
  }

  .hud-toggle-btn {
    background: transparent;
    border: none;
    color: #94a3b8;
    font-size: 14px;
    font-weight: bold;
    cursor: pointer;
    line-height: 1;
    padding: 0 4px;
    border-radius: 3px;
  }

  .hud-toggle-btn:hover {
    color: #f8fafc;
    background: rgba(255, 255, 255, 0.1);
  }

  .hud-body {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .hud-row {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
  }

  .hud-label {
    color: #94a3b8;
    font-weight: 500;
  }

  .hud-coord {
    font-family: monospace;
    color: #cbd5e1;
  }

  .hud-value {
    font-weight: 600;
    color: #f8fafc;
  }

  .hud-icon-val {
    font-family: monospace;
    font-size: 12px;
    color: #38bdf8;
  }

  .hud-poi-val {
    font-weight: 700;
    color: #f59e0b;
  }

  .hud-description {
    font-size: 12px;
    line-height: 1.35;
    color: #94a3b8;
    margin-top: 4px;
    white-space: normal;
  }

  .hud-placeholder {
    font-size: 12px;
    color: #64748b;
    font-style: italic;
    padding: 4px 0;
  }

  /* Minimized Pill View */
  .hud-pill {
    position: absolute;
    bottom: 16px;
    left: 16px;
    z-index: 20;
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(16, 22, 34, 0.85);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 20px;
    padding: 6px 12px;
    color: #f8fafc;
    cursor: pointer;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
    transition: background 0.15s ease, border-color 0.15s ease;
  }

  .hud-pill:hover {
    background: #1e293b;
    border-color: #38bdf8;
  }

  .hud-pill-icon {
    font-size: 12px;
    color: #38bdf8;
  }

  .hud-pill-label {
    font-size: 12px;
    font-weight: 600;
  }

  canvas {
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
    background: #101622;
    border-radius: 10px;
    cursor: crosshair;
  }

  canvas.grab {
    cursor: grab;
  }

  canvas.grabbing {
    cursor: grabbing;
  }
</style>