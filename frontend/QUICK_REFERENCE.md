# Quick Reference Card

## 🚀 Getting Started

```bash
# App is running at:
http://localhost:3000

# Login with demo account:
Email: demo@example.com
Password: demo123
```

## 📁 File Locations

```
Login page          → /vercel/share/v0-project/app/login/page.tsx
Register page       → /vercel/share/v0-project/app/register/page.tsx
Chat pages          → /vercel/share/v0-project/app/chat/page.tsx
Chat session        → /vercel/share/v0-project/app/chat/[sessionId]/page.tsx

Sidebar component   → /vercel/share/v0-project/components/sidebar.tsx
Chat message        → /vercel/share/v0-project/components/chat-message.tsx
Chat input          → /vercel/share/v0-project/components/chat-input.tsx
Sources panel       → /vercel/share/v0-project/components/sources-panel.tsx
Theme toggle        → /vercel/share/v0-project/components/theme-toggle.tsx

Auth utilities      → /vercel/share/v0-project/lib/auth.ts
API client          → /vercel/share/v0-project/lib/api.ts

Theme colors        → /vercel/share/v0-project/app/globals.css
```

## 🎨 Dark Mode Colors

```css
--background: #1A1F2E;           /* Main area */
--sidebar: #0F172A;              /* Sidebar background */
--sidebar-accent: #1E293B;       /* Sidebar active */
--card: #1E293B;                 /* Message bubbles */
--border: #334155;               /* Borders */
--foreground: #FFFFFF;           /* Text primary */
--muted-foreground: #94A3B8;     /* Text secondary */
--accent: #14B8A6;               /* Teal (user messages, buttons) */
```

## 🔌 API Integration

1. **Set API URL**:
   ```bash
   # .env.local
   NEXT_PUBLIC_API_URL=http://localhost:3001/api
   ```

2. **Implement endpoints** in `lib/api.ts`:
   - `registerUser()`
   - `loginUser()`
   - `getChatSessions()`
   - `sendMessage()`
   - etc.

3. **Test login**:
   - Go to http://localhost:3000/login
   - Try demo account or your own

## 📝 Common Tasks

### Add a new page
```typescript
// app/new-page/page.tsx
'use client'

import { useRouter } from 'next/navigation'
import { isAuthenticated } from '@/lib/auth'
import { useEffect } from 'react'

export default function NewPage() {
  const router = useRouter()
  
  useEffect(() => {
    if (!isAuthenticated()) router.push('/login')
  }, [router])

  return <div>Content</div>
}
```

### Make API call
```typescript
import { sendMessage } from '@/lib/api'

const response = await sendMessage(sessionId, 'Hello')
```

### Use theme
```typescript
import { useTheme } from 'next-themes'

const { theme, setTheme } = useTheme()
// theme is 'light', 'dark', or 'system'
```

### Use semantic colors
```tsx
<div className="bg-background text-foreground">
  <button className="bg-accent text-white">Action</button>
  <p className="text-muted-foreground">Secondary text</p>
</div>
```

## 🔐 Authentication Flow

```
User visits http://localhost:3000
  ↓
isAuthenticated() check
  ↓
Not authenticated → Redirect to /login
  ↓
User logs in → Token saved to localStorage
  ↓
Authenticated → Redirect to /chat
  ↓
User can access chat pages
  ↓
Click logout → Clear tokens
  ↓
Redirect to /login
```

## 🛠️ Debugging

### Check authentication
```javascript
// In browser console
localStorage.getItem('auth_token')
localStorage.getItem('auth_user')
```

### Check current theme
```javascript
// In browser console
localStorage.getItem('theme-preference')
document.documentElement.classList.contains('dark')
```

### Clear everything
```javascript
// In browser console
localStorage.clear()
location.reload()
```

## 📱 Responsive Breakpoints

- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

Tailwind prefixes:
- `md:` for tablet+
- `lg:` for desktop+
- No prefix for mobile

## ✅ Checklist for Integration

- [ ] Set `NEXT_PUBLIC_API_URL` in `.env.local`
- [ ] Implement `/auth/register` endpoint
- [ ] Implement `/auth/login` endpoint
- [ ] Test login page
- [ ] Implement `/chat/sessions` endpoints
- [ ] Implement `/chat/messages` endpoints
- [ ] Test chat pages
- [ ] Implement `/rag/query` for responses
- [ ] Deploy!

## 🎯 Key Files to Customize

| File | What to change |
|------|---|
| `lib/api.ts` | API base URL and endpoints |
| `app/globals.css` | Colors and theme |
| `components/sidebar.tsx` | Navigation layout |
| `components/chat-message.tsx` | Message styling |
| `app/login/page.tsx` | Auth UI |

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| "Cannot find module" | `rm -rf node_modules && pnpm install` |
| API fails to connect | Check `NEXT_PUBLIC_API_URL` |
| Theme doesn't switch | Check localStorage |
| Pages won't load | Verify authentication |
| Dark mode colors wrong | Edit `app/globals.css` |

## 📚 Documentation

- Full guide: `FULL_PROJECT_GUIDE.md`
- API specs: `API_INTEGRATION.md`
- Code examples: `CODE_EXAMPLES.md`
- Theme guide: `DARK_MODE_README.md`

## 💡 Tips

1. **Use TypeScript**: All types defined in `lib/api.ts`
2. **Handle errors**: All API calls can throw `ApiError`
3. **Mobile first**: Test on phone while developing
4. **Use console.log**: Add `[v0]` prefix for debugging
5. **CSS classes**: Use semantic colors (not hardcoded hex)

## 🎨 Theme Customization

### Change accent color
Edit in `app/globals.css`:
```css
.dark {
  --accent: #00FF00;  /* Your new color */
}
```

### Change sidebar
```css
.dark {
  --sidebar: #1a1a2e;  /* Sidebar background */
  --sidebar-accent: #16213e;  /* Active item */
}
```

## 🔗 Useful Links

- Next.js docs: https://nextjs.org
- Tailwind docs: https://tailwindcss.com
- React docs: https://react.dev
- TypeScript docs: https://typescriptlang.org

## 📞 Support

Need help? Check the full documentation:
```
FULL_PROJECT_GUIDE.md (500+ lines)
API_INTEGRATION.md (400+ lines)
CODE_EXAMPLES.md (300+ lines)
DARK_MODE_README.md (200+ lines)
```

---

**Remember**: This is a frontend-only application. You need to implement the backend API endpoints for full functionality.

Good luck! 🚀
