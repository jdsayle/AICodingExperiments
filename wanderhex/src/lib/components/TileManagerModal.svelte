<script lang="ts">
  import { mapStore } from '../state/mapState.svelte';

  interface Props {
    isOpen: boolean;
    onClose: () => void;
  }

  let { isOpen, onClose }: Props = $props();
  let dialogRef = $state<HTMLDialogElement | null>(null);

  $effect(() => {
    if (!dialogRef) return;
    if (isOpen && !dialogRef.open) {
      dialogRef.showModal();
    } else if (!isOpen && dialogRef.open) {
      dialogRef.close();
    }
  });

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === dialogRef) {
      onClose();
    }
  }

  function handleImageUpload(biomeId: string, event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;

    const file = input.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target?.result as string;
      if (dataUrl) {
        mapStore.customOverrides[biomeId] = dataUrl;
      }
    };
    reader.readAsDataURL(file);
  }

  function clearOverride(biomeId: string) {
    if (mapStore.customOverrides[biomeId]) {
      delete mapStore.customOverrides[biomeId];
    }
  }
</script>

<dialog
  bind:this={dialogRef}
  class="modal-dialog"
  onclick={handleBackdropClick}
  onclose={onClose}
>
  <div class="modal-card">
    <div class="modal-header">
      <h3>Manage Custom Tile Textures</h3>
      <button class="close-btn" onclick={onClose} aria-label="Close modal">&times;</button>
    </div>

    <div class="modal-body">
      <p class="modal-desc">
        Upload custom textures for active biomes in the <strong>{mapStore.activeTheme.name}</strong> theme.
      </p>

      <div class="tile-list">
        {#each mapStore.activeTheme.biomes as biome}
          <div class="tile-item">
            <div class="tile-info">
              <span class="color-badge" style="background-color: {biome.hexColor};"></span>
              <span class="tile-name">{biome.name}</span>
            </div>
            <div class="tile-actions">
              {#if mapStore.customOverrides[biome.id]}
                <span class="status-active">Custom Active</span>
                <button type="button" class="btn-clear" onclick={() => clearOverride(biome.id)}>Reset</button>
              {:else}
                <label class="btn-upload">
                  Upload
                  <input
                    type="file"
                    accept="image/*"
                    onchange={(e) => handleImageUpload(biome.id, e)}
                  />
                </label>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </div>

    <div class="modal-footer">
      <button type="button" class="primary" onclick={onClose}>Done</button>
    </div>
  </div>
</dialog>

<style>
  .modal-dialog {
    border: none;
    padding: 0;
    background: transparent;
    max-width: 90vw;
  }

  .modal-dialog::backdrop {
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(2px);
  }

  .modal-card {
    background: #111620;
    border: 1px solid var(--panel-border, #242f3d);
    border-radius: 8px;
    width: 440px;
    max-width: 90vw;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid var(--panel-border, #242f3d);
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1rem;
    color: #fff;
  }

  .close-btn {
    background: none;
    border: none;
    color: var(--text-muted, #94a3b8);
    font-size: 1.4rem;
    cursor: pointer;
    line-height: 1;
    padding: 0;
  }

  .close-btn:hover {
    color: #fff;
  }

  .modal-body {
    padding: 16px;
    overflow-y: auto;
    max-height: 60vh;
  }

  .modal-desc {
    font-size: 0.85rem;
    color: var(--text-muted, #94a3b8);
    margin-bottom: 16px;
  }

  .tile-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .tile-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: #182230;
    border-radius: 6px;
  }

  .tile-info {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .color-badge {
    width: 14px;
    height: 14px;
    border-radius: 3px;
  }

  .tile-name {
    font-size: 0.85rem;
    color: #fff;
  }

  .tile-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .status-active {
    font-size: 0.75rem;
    color: var(--accent, #38bdf8);
  }

  .btn-upload {
    background: #242f3d;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.8rem;
    cursor: pointer;
    color: #fff;
  }

  .btn-upload input {
    display: none;
  }

  .btn-clear {
    background: #382424;
    border: 1px solid #5a3030;
    color: #f87171;
    padding: 4px 8px;
    font-size: 0.75rem;
    cursor: pointer;
    border-radius: 4px;
  }

  .modal-footer {
    padding: 12px 16px;
    border-top: 1px solid var(--panel-border, #242f3d);
    display: flex;
    justify-content: flex-end;
  }

  .modal-footer button.primary {
    background: var(--accent, #38bdf8);
    color: #0b1118;
    border: none;
    padding: 6px 16px;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
  }
</style>