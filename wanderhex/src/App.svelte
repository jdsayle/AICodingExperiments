<script lang="ts">
  import { onMount } from 'svelte';
  import { initHotkeyListener } from './services/hotkeyService';
  import Sidebar from './lib/components/Sidebar.svelte';
  import HexCanvas from './lib/components/HexCanvas.svelte';
  import { mapStore } from './lib/state/mapState.svelte';

  // Automatically generate the initial map when the app mounts
  onMount(() => {
    mapStore.generateFresh();
    const cleanup = initHotkeyListener();
    return cleanup;
  });
</script>

<main class="app-layout">
  <Sidebar />
  <div class="canvas-viewport">
    <HexCanvas />
  </div>
</main>

<style>
  :global(body, html) {
    margin: 0;
    padding: 0;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    font-family: sans-serif;
    background: #0b0f19;
    color: #f3f4f6;
  }

  .app-layout {
    display: flex;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
  }

  .canvas-viewport {
    flex: 1;
    min-width: 0;
    min-height: 0;
    height: 100%;
    position: relative;
    background: #0f172a;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }
</style>