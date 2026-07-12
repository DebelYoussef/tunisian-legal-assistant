# Dark Mode Implementation Guide

## Overview
This project includes a production-ready dark mode implementation using **next-themes** with system preference detection and localStorage persistence. The theme automatically defaults to the user's system preference and can be toggled via the sun/moon icon in the navbar.

## Features

✅ **Theme Toggle** - Sun/moon icon in the top navbar
✅ **System Preference Detection** - Respects `prefers-color-scheme` media query
✅ **Persistent Storage** - Saves user preference to localStorage as `theme-preference`
✅ **Smooth Transitions** - CSS transitions for all color changes
✅ **Production-Ready Design** - Professional dark color palette
✅ **RTL Support** - Automatic detection for Arabic/RTL content
✅ **Mobile Responsive** - Hamburger menu on mobile, full sidebar on desktop
✅ **Accessibility** - Semantic HTML, ARIA labels, focus indicators

## Color Palette

### Light Mode
- Sidebar: `#1E293B` (slate-900)
- Sidebar Text: `#94A3B8` (slate-400)
- Sidebar Active Item: `#334155` (slate-700)
- Main Area: `#F8F9FA` (white/near-white)
- Bot Messages: `#E2E8F0` (slate-100)
- Input Bar: white with `#CBD5E1` border
- Accent/Button/User Messages: `#14B8A6` (teal-500)

### Dark Mode
- Sidebar Background: `#0F172A` (slate-950)
- Sidebar Text: `#94A3B8` (slate-400)
- Sidebar Active Item: `#1E293B` (slate-900)
- Main Area: `#1A1F2E` (custom dark)
- Bot Messages: `#1E293B` (slate-900)
- Input Bar: `#1E293B` with `#334155` border
- Navbar: `#0F172A` (slate-950)
- Accent: `#14B8A6` (teal - consistent in both modes)
- Text: white / `#94A3B8` for secondary

## Implementation Details

### 1. Dependencies
```json
{
  "next-themes": "0.4.6"
}
```

### 2. Layout Setup (`app/layout.tsx`)
- Imports `ThemeProvider` from `next-themes`
- Wraps children with ThemeProvider component
- Configuration:
  - `attribute="class"` - Uses CSS class for theming
  - `defaultTheme="system"` - Defaults to system preference
  - `enableSystem={true}` - Enables system preference detection
  - `storageKey="theme-preference"` - Custom localStorage key
- Added `suppressHydrationWarning` to html tag

### 3. CSS Variables (`app/globals.css`)
All colors are defined as CSS variables in:
- `:root` - Light mode defaults
- `.dark` - Dark mode overrides
- `@media (prefers-color-scheme: dark)` - System preference fallback

### 4. Theme Toggle Component (`components/theme-toggle.tsx`)
- Client-side component using `useTheme()` hook
- Displays moon icon in light mode, sun icon in dark mode
- Mounted state check to prevent hydration mismatch
- Teal accent color for the icon

### 5. Chat UI Integration (`app/page.tsx`)
- Dynamic theme-aware styling for all components
- Sidebar styling adapts to theme
- Message bubbles use correct colors for each theme
- Input area styling matches theme
- Proper contrast maintained in both modes

## How It Works

1. **On First Load**: 
   - Checks system preference via `prefers-color-scheme`
   - Or loads saved preference from localStorage (`theme-preference`)
   - Applies appropriate CSS class to `<html>` element

2. **On Theme Toggle**:
   - User clicks sun/moon icon
   - Theme updates to opposite of current
   - CSS class on `<html>` changes dynamically
   - All components re-render with new colors
   - Preference saved to localStorage

3. **Persistence**:
   - Theme preference stored in localStorage under key `theme-preference`
   - Survives page reload
   - Survives browser restart

## Usage in Components

### Getting Current Theme
```tsx
'use client'

import { useTheme } from 'next-themes'

export function MyComponent() {
  const { theme, setTheme } = useTheme()
  
  // theme: 'light' | 'dark' | 'system'
  // setTheme: (theme: string) => void
}
```

### Adding Theme-Aware Styles
```tsx
// Using className (Tailwind)
<div className="bg-background text-foreground dark:bg-slate-900">
  Content
</div>

// Using CSS variables
<div style={{ backgroundColor: 'var(--background)' }}>
  Content
</div>
```

## CSS Classes Reference

The following classes are automatically applied based on theme:

| Class | Light Mode | Dark Mode |
|-------|-----------|-----------|
| `.dark` | Not applied | Applied to `<html>` |
| `.light` | Applied to `<html>` | Not applied |

## Browser Support

- All modern browsers supporting:
  - CSS custom properties
  - `prefers-color-scheme` media query
  - localStorage API

## Testing Dark Mode

1. **Manual Toggle**: Click sun/moon icon in navbar
2. **System Preference**: 
   - Windows: Settings > Personalization > Colors
   - macOS: System Preferences > General > Appearance
   - Linux: GNOME Settings > Appearance
3. **Browser DevTools**: Use "Emulate CSS media feature `prefers-color-scheme`"

## Troubleshooting

### Dark mode not persisting
- Check if localStorage is enabled
- Verify key is `theme-preference` in localStorage
- Check browser privacy settings

### FOUC (Flash of Unstyled Content)
- This is handled by next-themes' script injection
- Only visible if JavaScript is slow to load
- Added `suppressHydrationWarning` prevents hydration mismatches

### Colors not updating
- Ensure component is marked with `'use client'`
- Check CSS variable names match those in globals.css
- Verify Tailwind is processing the classes

## Customization

### Changing Colors
Edit `app/globals.css` in the `.dark` and `:root` sections:

```css
.dark {
  --background: #1A1F2E;
  --foreground: #FFFFFF;
  --sidebar: #0F172A;
  /* ... other variables ... */
}
```

### Changing Default Theme
In `app/layout.tsx`:
```tsx
<ThemeProvider
  defaultTheme="dark"  // Change to 'light' or 'dark'
  enableSystem
>
```

### Changing Storage Key
In `app/layout.tsx`:
```tsx
<ThemeProvider
  storageKey="my-custom-key"  // Change storage key
  enableSystem
>
```

## Performance Considerations

- **next-themes script**: Injected in HTML head to prevent FOUC
- **CSS Variables**: Minimal performance impact, GPU-accelerated
- **LocalStorage**: Simple key-value, very fast
- **No extra bundles**: next-themes is ~5KB gzipped

## Accessibility

- Theme toggle has proper `aria-label`
- Focus indicators visible in both modes
- Sufficient color contrast in both modes (WCAG AA+)
- Respects user's system preference by default
- Reduced motion compatible

## Production Checklist

- ✅ next-themes installed
- ✅ ThemeProvider configured in layout.tsx
- ✅ CSS variables defined in globals.css
- ✅ Theme toggle component created
- ✅ All components styled with theme awareness
- ✅ localStorage persistence working
- ✅ System preference detection working
- ✅ Mobile responsive design
- ✅ Accessibility checked
- ✅ FOUC prevented with suppressHydrationWarning

## Files Modified/Created

1. **`app/layout.tsx`** - Added ThemeProvider wrapper
2. **`app/globals.css`** - Updated with dark mode CSS variables
3. **`components/theme-toggle.tsx`** - Created theme toggle button
4. **`app/page.tsx`** - Complete chat UI with dark mode support

## Next Steps

1. Connect to your actual API endpoints
2. Implement authentication flow (login/register pages)
3. Add more pages (settings, about, etc.) with theme support
4. Test on various devices and browsers
5. Gather user feedback and iterate on colors

---

**Version**: 1.0  
**Last Updated**: 2026-07-07  
**Status**: Production Ready
