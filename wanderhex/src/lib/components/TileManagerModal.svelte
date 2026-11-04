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