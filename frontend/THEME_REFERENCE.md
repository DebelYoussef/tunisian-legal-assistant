# Theme Color Reference

## Quick Color Palette

### Semantic Colors (Use these!)

```css
/* Backgrounds */
--background        /* Main page background */
--card             /* Card/message bubble background */
--popover          /* Popover/dropdown background */
--input            /* Input field background */

/* Text */
--foreground       /* Primary text color */
--muted-foreground /* Secondary/disabled text color */

/* Actions */
--primary          /* Primary buttons/links */
--accent           /* Accent color (teal) - #14B8A6 */
--destructive      /* Delete/error actions */

/* UI Elements */
--border           /* Border color */
--ring             /* Focus ring color */
--sidebar          /* Sidebar background */
--sidebar-foreground /* Sidebar text */
```

## Sidebar Colors (Dark Mode)

```
Sidebar Background: #0F172A (--sidebar)
    ├── Active Item: #1E293B (--sidebar-accent)
    │   └── Text: white (--sidebar-accent-foreground)
    ├── Inactive Item: transparent
    │   └── Text: #94A3B8 (--sidebar-foreground)
    └── Border: #1E293B (--sidebar-border)

Main Area: #1A1F2E (--background)
    ├── Bot Messages: #1E293B (--card)
    │   └── Text: white (--card-foreground)
    ├── Input Bar: #1E293B (--input)
    │   └── Border: #334155
    └── Accent Color: #14B8A6 (--accent)
```

## Tailwind Classes

### Light Mode (Default)
```tsx
// Direct colors
<div className="bg-white text-black" />

// Semantic tokens
<div className="bg-background text-foreground" />

// Sidebar
<div className="bg-sidebar text-sidebar-foreground" />
<div className="bg-sidebar-accent text-sidebar-accent-foreground" />
```

### Dark Mode
- Same classes auto-apply dark colors
- No need to add `dark:` prefix for semantic tokens
- Use `dark:` only for custom Tailwind colors

```tsx
// These work in both modes
<div className="bg-background text-foreground" />

// Both light and dark handled automatically!
```

## Examples

### Message Bubble (User - Teal)
```tsx
<div className="bg-accent text-white">
  Your message goes here
</div>
```

### Message Bubble (Assistant)
```tsx
<div className="border border-border bg-card text-card-foreground">
  Assistant response
</div>
```

### Sidebar Item
```tsx
<div className="bg-sidebar-accent text-sidebar-accent-foreground">
  Active conversation
</div>
```

### Button
```tsx
<button className="bg-accent text-white hover:opacity-90">
  Send
</button>
```

### Input
```tsx
<input className="border border-input bg-input text-foreground" />
```

## Color Values by Mode

### Light Mode
| Token | Value |
|-------|-------|
| background | #FFFFFF |
| foreground | #145A4C |
| sidebar | #1E293B |
| sidebar-foreground | #94A3B8 |
| card | #E2E8F0 |
| accent | #14B8A6 |
| input | #FFFFFF |
| border | #CBD5E1 |

### Dark Mode
| Token | Value |
|-------|-------|
| background | #1A1F2E |
| foreground | #FFFFFF |
| sidebar | #0F172A |
| sidebar-foreground | #94A3B8 |
| sidebar-accent | #1E293B |
| card | #1E293B |
| accent | #14B8A6 |
| input | #1E293B |
| border | #334155 |

## Component Theme Variants

### Navbar
- Light: Uses default background
- Dark: `#0F172A` (slate-950)

### Sidebar
- Light: `#1E293B` (slate-900)
- Dark: `#0F172A` (slate-950)

### Active Sidebar Item
- Light: `#334155` (slate-700)
- Dark: `#1E293B` (slate-900)

### Main Chat Area
- Light: `#F8F9FA` (off-white)
- Dark: `#1A1F2E` (custom dark)

### Bot Message Bubble
- Light: `#E2E8F0` (slate-100)
- Dark: `#1E293B` (slate-900)

### User Message Bubble
- Both modes: `#14B8A6` (teal-500)

### Input Bar
- Light: white with `#CBD5E1` border
- Dark: `#1E293B` with `#334155` border

## Do's and Don'ts

### ✅ DO

```tsx
// Use semantic color tokens
<div className="bg-background text-foreground" />

// Use accent for primary actions
<button className="bg-accent text-white" />

// Use card for message bubbles
<div className="bg-card text-card-foreground" />

// Use sidebar colors for sidebar
<div className="bg-sidebar text-sidebar-foreground" />
```

### ❌ DON'T

```tsx
// Don't hardcode colors
<div className="bg-white dark:bg-slate-900" />

// Don't use arbitrary colors
<div className="bg-[#1e293b]" />

// Don't mix light/dark tokens inconsistently
<div className="bg-white dark:bg-background" /> // Confusing!
```

## Applying Dark Mode to New Components

### Step 1: Import the theme hook
```tsx
'use client'
import { useTheme } from 'next-themes'
```

### Step 2: Use semantic colors
```tsx
export function MyComponent() {
  return (
    <div className="bg-background text-foreground">
      <h1 className="text-foreground">Title</h1>
      <p className="text-muted-foreground">Subtitle</p>
      <button className="bg-accent text-white">Action</button>
    </div>
  )
}
```

### Step 3: No extra dark mode CSS needed!
- The `.dark` class is automatically applied by next-themes
- All CSS variables update automatically
- Component automatically supports both themes

## Testing Your Theme

```bash
# Light mode
# 1. Toggle to Light in navbar
# 2. Check all elements render correctly

# Dark mode  
# 1. Toggle to Dark in navbar
# 2. Check all elements render correctly
# 3. Check contrast meets WCAG AA (4.5:1 minimum)

# System preference
# 1. Change OS dark/light setting
# 2. Refresh page
# 3. Should match system preference
```

## Debugging

### Check current theme
```tsx
'use client'
import { useTheme } from 'next-themes'

export function DebugTheme() {
  const { theme } = useTheme()
  return <div>Current theme: {theme}</div>
}
```

### Check CSS variables
```tsx
// In browser console
getComputedStyle(document.documentElement).getPropertyValue('--background')
```

### Check localStorage
```tsx
// In browser console
localStorage.getItem('theme-preference')
```

---

**All components in this project use these semantic colors automatically!**
