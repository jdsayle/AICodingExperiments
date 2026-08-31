import { HOTKEYS } from '../types/hotkeys';
import { mapStore } from '../lib/state/mapState.svelte';

function isInputElement(target: EventTarget | null): boolean {
  if (!target || !(target instanceof HTMLElement)) return false;
  
  const tagName = target.tagName.toUpperCase();
  const isInput = tagName === 'INPUT' || tagName === 'TEXTAREA' || tagName === 'SELECT';
  const isEditable = target.isContentEditable;

  return isInput || isEditable;
}

export function initHotkeyListener(): () => void {
  function handleKeyDown(event: KeyboardEvent) {
    // Suppress hotkeys when focused inside text inputs, textareas, or contenteditable fields
    if (isInputElement(event.target)) return;

    // Ignore modifier combinations (Ctrl/Cmd/Alt) to avoid intercepting browser shortcuts
    if (event.ctrlKey || event.metaKey || event.altKey) return;

    const key = event.key.toLowerCase();

    const matchedHotkey = HOTKEYS.find((h) => h.key.toLowerCase() === key);
    if (!matchedHotkey) return;

    switch (matchedHotkey.id) {
      case 'toggle-coordinates':
        event.preventDefault();
        mapStore.toggleCoordinates();
        break;
      case 'toggle-inspector':
        event.preventDefault();
        mapStore.toggleHud();
        break;
    }
  }

  window.addEventListener('keydown', handleKeyDown);

  // Return cleanup function for teardown/unmounting if needed
  return () => {
    window.removeEventListener('keydown', handleKeyDown);
  };
}