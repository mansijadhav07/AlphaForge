# Performance & Configuration Guide

## Auto-Refresh Settings

The dashboard auto-refreshes to show real-time data. You can customize this behavior in `frontend/lib/config.ts`:

### Current Settings

```typescript
refresh: {
  dashboard: 30000,      // 30 seconds
  stockDetail: 60000,    // 60 seconds
  insights: 45000,       // 45 seconds
  backtesting: 0,        // Disabled
  pgmGraph: 0,           // Disabled
  featureImpact: 0,      // Disabled
  modelEvaluation: 0,    // Disabled
  modelFailures: 0,      // Disabled
}
```

### How to Change

**Option 1: Increase Refresh Interval**
```typescript
// Change from 30 seconds to 60 seconds
dashboard: 60000,
```

**Option 2: Disable Auto-Refresh**
```typescript
// Set to 0 to disable
dashboard: 0,

// Or disable globally
features: {
  autoRefresh: false,
}
```

**Option 3: Decrease for More Real-Time Feel**
```typescript
// Change to 15 seconds (not recommended - more API calls)
dashboard: 15000,
```

## Page Load Performance

### Issue: Slow Page Transitions

**Causes:**
1. Animations taking time
2. Data fetching on page load
3. Large component trees

**Solutions:**

### 1. Reduce Animation Duration

Edit `frontend/lib/config.ts`:
```typescript
animations: {
  splashScreenDuration: 1000,  // Reduce from 1500ms
  pageTransitionDuration: 200, // Reduce from 300ms
  staggerDelay: 30,            // Reduce from 50ms
}
```

### 2. Disable Animations Completely

```typescript
features: {
  animations: false,  // Disable all animations
}
```

### 3. Skip Splash Screen

Edit `frontend/app/page.tsx`:
```typescript
// Change timeout to 0 for instant redirect
const timer = setTimeout(() => {
  router.push('/dashboard')
}, 0)
```

Or better yet, use server-side redirect:
```typescript
// Replace entire page.tsx with:
import { redirect } from 'next/navigation'

export default function Home() {
  redirect('/dashboard')
}
```

## Optimization Tips

### 1. Reduce Network Calls

**Current Behavior:**
- Dashboard fetches data every 30 seconds
- Each page fetches data on load

**Optimization:**
```typescript
// Increase intervals
refresh: {
  dashboard: 60000,  // 1 minute
  stockDetail: 120000, // 2 minutes
}
```

### 2. Enable Production Build

Development mode is slower. Use production build:

```bash
# Build for production
npm run build

# Run production server
npm start
```

**Performance Gains:**
- 3-5x faster page loads
- Smaller bundle sizes
- Optimized images
- Code minification

### 3. Lazy Load Heavy Components

Charts are heavy. They're already lazy-loaded, but you can verify:

```typescript
// In component files
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(() => import('./heavy-chart'), {
  loading: () => <SkeletonChart />,
  ssr: false
})
```

### 4. Reduce Animation Complexity

Edit `frontend/app/globals.css`:

```css
/* Disable complex animations */
* {
  transition-duration: 100ms !important; /* Faster */
}

/* Or disable completely */
* {
  transition: none !important;
  animation: none !important;
}
```

## Measuring Performance

### 1. Chrome DevTools

1. Open DevTools (F12)
2. Go to "Performance" tab
3. Click "Record"
4. Navigate pages
5. Stop recording
6. Analyze timeline

### 2. Lighthouse

1. Open DevTools (F12)
2. Go to "Lighthouse" tab
3. Click "Analyze page load"
4. Review scores

**Target Scores:**
- Performance: 90+
- Accessibility: 95+
- Best Practices: 90+

### 3. Network Tab

1. Open DevTools (F12)
2. Go to "Network" tab
3. Reload page
4. Check:
   - Total requests
   - Total size
   - Load time

**Optimization Goals:**
- < 20 requests per page
- < 1MB total size
- < 2s load time

## Common Issues & Fixes

### Issue: Page Flashes on Refresh

**Cause:** Loading state shows skeleton every refresh

**Fix:** Only show loading on initial load (already implemented)

```typescript
const fetchData = async () => {
  // Only show loading on initial load
  if (!marketData) {
    setLoading(true)
  }
  const data = await api.getMarketOverview()
  setMarketData(data)
  setLoading(false)
}
```

### Issue: Animations Feel Sluggish

**Cause:** Too many animations at once

**Fix:** Reduce stagger delay

```typescript
animations: {
  staggerDelay: 30,  // Reduce from 50ms
}
```

### Issue: High CPU Usage

**Cause:** Too many re-renders or animations

**Fix:**
1. Disable auto-refresh
2. Reduce animation complexity
3. Use production build

### Issue: Slow API Responses

**Cause:** Backend processing time

**Fix:**
1. Check backend logs
2. Optimize backend queries
3. Add caching
4. Use mock data for development

## Recommended Settings

### For Development
```typescript
refresh: {
  dashboard: 60000,  // 1 minute
}
animations: {
  splashScreenDuration: 500,  // 0.5 seconds
}
features: {
  autoRefresh: true,
  animations: true,
}
```

### For Production
```typescript
refresh: {
  dashboard: 30000,  // 30 seconds
}
animations: {
  splashScreenDuration: 1500,  // 1.5 seconds
}
features: {
  autoRefresh: true,
  animations: true,
}
```

### For Slow Connections
```typescript
refresh: {
  dashboard: 120000,  // 2 minutes
}
animations: {
  enabled: false,  // Disable animations
}
features: {
  autoRefresh: false,  // Manual refresh only
}
```

## Quick Fixes Summary

**To stop auto-refresh:**
```typescript
// frontend/lib/config.ts
features: {
  autoRefresh: false,
}
```

**To speed up page loads:**
```bash
npm run build
npm start
```

**To skip splash screen:**
```typescript
// frontend/app/page.tsx
import { redirect } from 'next/navigation'
export default function Home() {
  redirect('/dashboard')
}
```

**To reduce animations:**
```typescript
// frontend/lib/config.ts
animations: {
  splashScreenDuration: 500,
  pageTransitionDuration: 150,
  staggerDelay: 20,
}
```

---

**Need Help?** Check the browser console for errors or performance warnings.
