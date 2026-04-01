# AlphaForge Performance Optimization - Quick Reference

## 🚀 Quick Start

```bash
# 1. Install Redis (optional)
./scripts/setup_redis.sh

# 2. Install dependencies
pip install redis

# 3. Start backend
python api_server.py

# 4. Start frontend
cd frontend && npm run dev

# 5. Test
open http://localhost:3000/stock/AAPL
```

## 📡 API Endpoints

### Historical Data (Call Once)
```bash
GET /api/historical/{symbol}?days=30
```
- Returns: Full cached dataset with all indicators
- Cache: 1 hour TTL
- Size: ~500KB
- Use: Page load only

### Live Price (Poll Every 30s)
```bash
GET /api/live/{symbol}
```
- Returns: Latest price + indicators only
- Cache: 30 seconds TTL
- Size: ~1KB
- Use: Live updates

### Cache Management
```bash
# Get stats
GET /api/cache/stats

# Clear all
POST /api/cache/clear

# Clear namespace
POST /api/cache/clear?namespace=historical
```

## 💻 Frontend Usage

### Load Historical Data
```typescript
const response = await api.getHistoricalData(symbol, 30)
setData(response.data)
```

### Update Live Data
```typescript
const liveData = await api.getLivePrice(symbol)
setData(prevData => {
  const newData = [...prevData]
  newData[newData.length - 1] = updatedPoint
  return newData
})
```

### Live Mode Pattern
```typescript
// Enable live mode
const [isLive, setIsLive] = useState(false)

useEffect(() => {
  if (!isLive) return
  
  const interval = setInterval(async () => {
    await updateLiveData()
  }, 30000)
  
  return () => clearInterval(interval)
}, [isLive])
```

## 🎨 UI Components

### Live Indicator
```tsx
<LiveIndicator
  isLive={isLiveMode}
  lastUpdated={lastUpdated}
  onToggle={toggleLiveMode}
  isLoading={isUpdating}
  error={error}
/>
```

### Price Chart with Highlight
```tsx
<PriceChart
  data={data}
  showIndicators={showIndicators}
  highlightLast={isLiveMode}
/>
```

## 🔧 Configuration

### Cache Service
```python
# services/cache_service.py
cache_service = CacheService(
    redis_host='localhost',
    redis_port=6379,
    default_ttl=300  # 5 minutes
)
```

### Polling Interval
```typescript
// frontend/app/stock/[symbol]/page.tsx
const POLL_INTERVAL = 30000  // 30 seconds
```

### Cache TTL
```python
# Historical data
cache_service.set_historical_data(symbol, data, ttl=3600)  # 1 hour

# Live price
cache_service.set_live_price(symbol, price, timestamp, ttl=30)  # 30 seconds

# Features
cache_service.set_features(symbol, features, ttl=600)  # 10 minutes
```

## 📊 Performance Metrics

| Metric | Target | Command |
|--------|--------|---------|
| Initial Load | <500ms | DevTools Network tab |
| Cache Hit | >95% | `curl /api/cache/stats` |
| Live Payload | <2KB | `curl -w '%{size_download}' /api/live/AAPL` |
| Update Interval | 30s | Browser Network tab |

## 🐛 Common Issues

### Redis Not Available
**Symptom**: Warning in logs
**Solution**: System uses in-memory cache automatically. No action needed.

### Cache Not Working
**Solution**:
```bash
curl -X POST http://localhost:8000/api/cache/clear
```

### Live Updates Stopped
**Solution**:
1. Check live mode enabled (green indicator)
2. Check browser console
3. Disable/enable live mode

### Slow Initial Load
**Solution**:
```bash
# Ensure data is ingested
python -m data_ingestion.ingestion
```

## 🧪 Testing

### Quick Test
```bash
# Test cache
curl http://localhost:8000/api/cache/stats

# Test historical (first call)
time curl http://localhost:8000/api/historical/AAPL

# Test historical (cached)
time curl http://localhost:8000/api/historical/AAPL

# Test live
time curl http://localhost:8000/api/live/AAPL
```

### Full Test Suite
```bash
./scripts/test_performance.sh
```

## 📈 Optimization Checklist

- [x] Redis installed and running
- [x] Cache service initialized
- [x] Historical endpoint returns cached data
- [x] Live endpoint returns minimal payload
- [x] Frontend loads instantly
- [x] Live mode updates smoothly
- [x] Chart doesn't flicker
- [x] User can toggle live mode
- [x] Error handling works
- [x] Cache hit rate >95%

## 🎯 Key Principles

1. **Load once** - Historical data fetched once on mount
2. **Update incrementally** - Only last datapoint updated
3. **Cache aggressively** - Use Redis with TTL
4. **Minimize payload** - Live endpoint returns 1KB vs 500KB
5. **User control** - Let users enable/disable live mode
6. **Graceful degradation** - Fall back to in-memory cache
7. **Visual feedback** - Show live/static status clearly

## 📚 Documentation

- **Full Guide**: `PERFORMANCE_OPTIMIZATION_COMPLETE.md`
- **Testing**: `PERFORMANCE_TESTING_GUIDE.md`
- **Setup**: `scripts/setup_redis.sh`
- **Architecture**: `PERFORMANCE_OPTIMIZATION_PLAN.md`

## 🔗 Useful Commands

```bash
# Backend
python api_server.py                    # Start server
curl /api/cache/stats                   # Check cache
curl -X POST /api/cache/clear           # Clear cache

# Frontend
cd frontend && npm run dev              # Start dev server
npm run build                           # Production build

# Redis
redis-cli ping                          # Check connection
redis-cli MONITOR                       # Watch commands
redis-cli FLUSHALL                      # Clear all data

# Testing
./scripts/test_performance.sh           # Run tests
./scripts/setup_redis.sh                # Setup Redis
```

## 💡 Pro Tips

1. **Use Redis in production** - Much better than in-memory
2. **Monitor cache hit rate** - Should be >95%
3. **Adjust TTL based on usage** - Balance freshness vs load
4. **Enable live mode only when needed** - Saves bandwidth
5. **Clear cache after data ingestion** - Get fresh data
6. **Use WebSocket for real-time** - Better than polling
7. **Add monitoring** - Track performance metrics

## 🎓 Learning Resources

- Redis Documentation: https://redis.io/docs
- React Performance: https://react.dev/learn/render-and-commit
- FastAPI Caching: https://fastapi.tiangolo.com/advanced/response-headers/
- Chart.js Performance: https://www.chartjs.org/docs/latest/general/performance.html

---

**Need Help?** Check the full documentation or run the test suite to diagnose issues.
