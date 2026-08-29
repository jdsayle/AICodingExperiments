<script lang="ts">
  import { SPRITE_MAP } from '../constants/spriteMap';
  import spriteSheetUrl from '../../assets/icons.jpg';

  let { name, size = 24 }: { name: string; size?: number } = $props();

  const coord = $derived(SPRITE_MAP[name] ?? SPRITE_MAP['default_icon']);

  // Calculate background offsets for a 4x4 grid (0%, 33.333%, 66.666%, 100%)
  const posX = $derived((coord.col / 3) * 100);
  const posY = $derived((coord.row / 3) * 100);
</script>

<span
  class="sprite-icon"
  style="
    width: {size}px;
    height: {size}px;
    background-image: url('{spriteSheetUrl}');
    background-position: {posX}% {posY}%;
    background-size: 400% 400%;
  "
></span>

<style>
  .sprite-icon {
    display: inline-block;
    vertical-align: middle;
    image-rendering: pixelated;
    background-repeat: no-repeat;
    flex-shrink: 0;
  }
</style>