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
  
  // 1. Preload the Sprite Sheet Image
  let spriteSheet = $state<HTMLImageElement | null>(null);

  onMount(() => {
    const img = new Image();
    img.src = spriteSheetUrl;
    img.onload = () => {
      spriteSheet = img;
      render();
    };

    window.addEventListener('resize', render);
    render();
    return () => window.removeEventListener('resize', render);
  });

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

    // Turn on pixelated rendering for clean 16x16 sprites
    ctx.imageSmoothingEnabled = false;

    // 1. Base Hex Tiles & Bitmap Overlay Pipeline
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

        // 2. Render Sprite or Fallback Emoji/Text
        if (iconKey) {
          const coord = SPRITE_MAP[iconKey];

          if (coord && spriteSheet) {
            // Standard 16x16 pixel sprite slice inside a 4x4 sheet
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
            // Fallback for Fantasy/Sci-Fi themes using native unicode emojis
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
      ctx.lineWidth = isHovered ? 3 : 1.2;
      ctx.stroke();

      // Coordinate Label
      ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
      ctx.font = `${Math.max(9, Math.round(geo.radius * 0.22))}px monospace`;
      ctx.textAlign = 'center';
      ctx.fillText(`${hex.col},${hex.row}`, center.x, center.y - geo.radius * 0.52);
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
      ctx.lineWidth = 2;
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
  }

  function handleMouseMove(e: MouseEvent) {
    if (!canvasEl || !containerEl) return;
    const rect = canvasEl.getBoundingClientRect();
    const mousePt = {
      x: (e.clientX - rect.left) * (canvasEl.width / rect.width),
      y: (e.clientY - rect.top) * (canvasEl.height / rect.height)
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

  function handleMouseLeave() {
    mapStore.hoveredHex = null;
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
      sheet: spriteSheet
    };
    render();
  });
</script>

<div class="viewport" bind:this={containerEl}>
  <canvas
    bind:this={canvasEl}
    onmousemove={handleMouseMove}
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

  canvas {
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
    background: #101622;
    border-radius: 10px;
    cursor: crosshair;
  }
</style>