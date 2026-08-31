export interface HotkeyDefinition {
  id: string;
  key: string;
  label: string;
  category: 'View' | 'Map Controls' | 'General';
  description: string;
}

export const HOTKEYS: HotkeyDefinition[] = [
  {
    id: 'toggle-coordinates',
    key: 'c',
    label: 'Toggle Coordinates',
    category: 'View',
    description: 'Show or hide coordinate labels (0,0; 0,1; etc.) on hex tiles'
  },
  {
    id: 'toggle-inspector',
    key: 'i',
    label: 'Toggle Inspector HUD',
    category: 'View',
    description: 'Minimize or expand the Hex Inspector overlay'
  }
];