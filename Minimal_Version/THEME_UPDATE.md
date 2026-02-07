# Shadcn-Inspired Theme Update

## ✨ What's New

Your Minimal_Version frontend has been completely redesigned with a **high-quality, fully responsive shadcn-inspired theme**.

### 🎨 Design System

#### Color Palette (Dark Theme)
- **Background**: Deep slate (hsl(224, 71%, 4%))
- **Foreground**: Light gray (hsl(213, 31%, 91%))
- **Primary**: Near white with hover states
- **Accent**: Subtle blue-gray tones
- **Border**: Consistent throughout for cards and inputs

#### Component Library
All pages now use consistent, reusable component classes:

**Buttons**:
- `.btn` - Base button styles
- `.btn-primary` - Primary action buttons
- `.btn-secondary` - Secondary buttons  
- `.btn-outline` - Outlined buttons
- `.btn-ghost` - Ghost buttons

**Form Elements**:
- `.input` - Text inputs and selects
- `.textarea` - Multi-line text areas
- `.label` - Form labels

**Cards & Badges**:
- `.card` - Container cards
- `.badge` - Inline badges (default, secondary, outline)

### 📱 Responsive Design

**Mobile-First Approach** with breakpoints:
- `sm:` - 640px and up
- `md:` - 768px and up  
- `lg:` - 1024px and up
- `2xl:` - 1400px (container max-width)

**Key Responsive Features**:
- Sticky navigation header with backdrop blur
- Responsive grid layouts (1-col mobile → 2-col tablet → 3-col desktop)
- Collapsible navigation on small screens
- Flexible form layouts
- Touch-friendly button sizes

### 🚀 Pages Updated

#### 1. Brand Configuration ([index.html](templates/index.html))
- Clean card-based brand listing
- 2-column responsive form layout
- Improved visual hierarchy

#### 2. Create Post ([create-post.html](templates/create-post.html))
- Brand selector with inline details
- Responsive 2-column form
- Professional loading modal with agent status

#### 3. Agent Debate ([debate.html](templates/debate.html))
- Post context summary cards
- Color-coded vote badges (approve/conditional/reject)
- Agent-specific icons and styling
- Prominent CMO decision display

#### 4. Generated Posts ([results.html](templates/results.html))
- 3-column responsive grid
- Gradient post headers
- Full-detail modal with syntax highlighting
- Copy-to-clipboard functionality

### 🛠️ Technical Implementation

**Tailwind CSS v3** configured with:
- Custom CSS variables for theming
- Extended color palette
- Custom animation keyframes
- Container queries
- Dark mode support

**Custom Utilities** in [input.css](static/css/input.css):
```css
@layer components {
  .btn { /* Base button styles */ }
  .card { /* Card container */ }
  .input { /* Form input */ }
  .badge { /* Badge component */ }
}
```

### 📦 Build Commands

```bash
# Build CSS once
npm run build:css

# Watch mode (auto-rebuild on changes)
npm run watch:css
```

### ✅ What's Working

- ✅ Fully responsive layouts (mobile → desktop)
- ✅ Consistent design system across all pages
- ✅ Accessible form controls with proper labels
- ✅ Smooth transitions and hover states
- ✅ Professional loading states
- ✅ Color-coded status indicators
- ✅ Touch-friendly mobile interface
- ✅ High contrast for readability

### 🎯 Next Steps

1. **Test Responsiveness**: Open in different screen sizes
2. **Run the Application**: `python app.py`
3. **Customize Colors**: Edit CSS variables in `input.css`
4. **Add More Components**: Extend the component library as needed

---

**Design Philosophy**: Clean, minimal, professional - inspired by shadcn/ui's component-first approach with Tailwind CSS utilities.
