# AlphaForge Performance Testing Guide

## 🧪 Testing the Optimization

This guide helps you verify that the performance optimizations are working correctly.

## Prerequisites

1. Backend running: `python api_server.py`
2. Frontend running: `cd frontend && npm run dev`
3. Redis installed (optional): `./scripts/setup_redis.sh`

## Test Suite

### Test 1: Cache Service Initialization

**Objective**: Verify cache service starts correctly

```bash
# Check cache stats
curl http://localhost:8000/api/cache/stats
```

**Expected Output**:
```json
{
  "status": "success",
  "stats": {
    "redis_available": true,  // or false if using in-memory
    "memory_cache_size": 0,
    "redis_keys": 0
  }
}
```

**Pass Criteria**: 
- ✅ Returns 200 status
- ✅ Shows redis_available status
- ✅ No errors in backend logs

---

### Test 2: Historical Data Endpoint (First Call)

**Objective**: Verify historical data fetching and caching

```bash
# First call - should fetch from feature store
time curl http://localhost:8000/api/historical/AAPL
```

**Expected Output**:
```json
{
  "symbol": "AAPL",
  "data": [...],  // 30 datapoints
  "cached_at": "2026-04-01T19:30:00",
  "data_points": 30,
  "cache_hit": false  // First call
}
```

**Pass Criteria**:
- ✅ Returns 200 status
- ✅ Contains 30 datapoints
- ✅ cache_hit is false (first call)
- ✅ Response time < 2 seconds
- ✅ Backend logs show "Cache miss"

---

### Test 3: Historical Data Endpoint (Cached Call)

**Objective**: Verify cache is working

```bash
# Second call - should return from cache
time curl http://localhost:8000/api/historical/AAPL
```

**Expected Output**:
```json
{
  "symbol": "AAPL",
  "data": [...],
  "cached_at": "2026-04-01T19:30:00",
  "data_points": 30,
  "cache_hit": true  // Cached!
}
```

**Pass Criteria**:
- ✅ Returns 200 status
- ✅ cache_hit is true
- ✅ Response time < 100ms (10-20x faster!)
- ✅ Backend logs show "Cache HIT"

---

### Test 4: Live Price Endpoint

**Objective**: Verify live data endpoint returns minimal payload

```bash
# Get live price
time curl http://localhost:8000/api/live/AAPL
```

**Expected Output**:
```json
{
  "symbol": "AAPL",
  "price": 182.45,
  "timestamp": "2026-04-01T19:30:00",
  "change": 2.34,
  "change_pct": 0.0130,
  "indicators": {
    "rsi": 65.2,
    "macd": 1.23,
    // ... other indicators
  },
  "cached_at": "2026-04-01T19:30:00"
}
```

**Pass Criteria**:
- ✅ Returns 200 status
- ✅ Response size < 2KB (check with `curl -w '%{size_download}\n'`)
- ✅ Response time < 50ms (from cache)
- ✅ Contains all required indicators

---

### Test 5: Payload Size Comparison

**Objective**: Verify 99% payload reduction

```bash
# Historical endpoint (full dataset)
curl -w 'Size: %{size_download} bytes\n' -o /dev/null -s http://localhost:8000/api/historical/AAPL

# Live endpoint (single point)
curl -w 'Size: %{size_download} bytes\n' -o /dev/null -s http://localhost:8000/api/live/AAPL
```

**Expected Output**:
```
Historical: ~500,000 bytes (500KB)
Live: ~1,000 bytes (1KB)
Reduction: 99.8%
```

**Pass Criteria**:
- ✅ Historical endpoint: 400-600KB
- ✅ Live endpoint: 1-2KB
- ✅ Reduction > 99%

---

### Test 6: Cache Expiration

**Objective**: Verify TTL is working

```bash
# Call historical endpoint
curl http://localhost:8000/api/historical/AAPL

# Wait 5 seconds
sleep 5

# Call again - should still be cached (1-hour TTL)
curl http://localhost:8000/api/historical/AAPL

# Clear cache
curl -X POST http://localhost:8000/api/cache/clear

# Call again - should fetch fresh
curl http://localhost:8000/api/historical/AAPL
```

**Pass Criteria**:
- ✅ Second call shows cache_hit: true
- ✅ After clear, shows cache_hit: false
- ✅ Backend logs show cache operations

---

### Test 7: Frontend Initial Load

**Objective**: Verify instant page load

1. Open browser DevTools (Network tab)
2. Navigate to `http://localhost:3000/stock/AAPL`
3. Observe network requests

**Expected Behavior**:
- ✅ Single request to `/api/historical/AAPL`
- ✅ Page renders in < 500ms
- ✅ No repeated requests
- ✅ Chart displays immediately

**Pass Criteria**:
- ✅ DOMContentLoaded < 500ms
- ✅ Load complete < 1s
- ✅ Only 1 API call on mount

---

### Test 8: Frontend Live Mode

**Objective**: Verify live updates work correctly

1. Navigate to `http://localhost:3000/stock/AAPL`
2. Click "Enable Live Mode"
3. Observe network requests for 2 minutes

**Expected Behavior**:
- ✅ Live indicator shows green "LIVE"
- ✅ Pulse animation visible
- ✅ Request to `/api/live/AAPL` every 30 seconds
- ✅ Chart updates smoothly (no flicker)
- ✅ Last datapoint highlighted with pulsing dot

**Pass Criteria**:
- ✅ Exactly 4 requests in 2 minutes (30s interval)
- ✅ Each request < 2KB
- ✅ No full page re-renders
- ✅ Chart remains smooth

---

### Test 9: Frontend Static Mode

**Objective**: Verify static mode stops updates

1. Navigate to `http://localhost:3000/stock/AAPL`
2. Enable live mode
3. Wait for 1 update
4. Click "Pause Updates"
5. Wait 1 minute

**Expected Behavior**:
- ✅ Live indicator shows yellow "STATIC"
- ✅ No pulse animation
- ✅ No network requests to `/api/live/AAPL`
- ✅ Chart remains frozen
- ✅ "Last updated" timestamp stops updating

**Pass Criteria**:
- ✅ Zero requests after pause
- ✅ UI clearly shows static mode
- ✅ Can re-enable live mode

---

### Test 10: Error Handling

**Objective**: Verify graceful error handling

```bash
# Stop backend
# Try to load page

# Restart backend
# Reload page
```

**Expected Behavior**:
- ✅ Shows error message (not crash)
- ✅ Falls back to mock data
- ✅ Recovers when backend restarts
- ✅ User can retry

**Pass Criteria**:
- ✅ No white screen of death
- ✅ Error message displayed
- ✅ Automatic recovery

---

### Test 11: Multiple Symbols

**Objective**: Verify caching works per symbol

```bash
# Cache different symbols
curl http://localhost:8000/api/historical/AAPL
curl http://localhost:8000/api/historical/TSLA
curl http://localhost:8000/api/historical/GOOGL

# Check cache stats
curl http://localhost:8000/api/cache/stats
```

**Expected Output**:
```json
{
  "stats": {
    "redis_keys": 3,  // One per symbol
    "memory_cache_size": 3
  }
}
```

**Pass Criteria**:
- ✅ Each symbol cached separately
- ✅ No cache collision
- ✅ All symbols load fast

---

### Test 12: Cache Clear

**Objective**: Verify cache management works

```bash
# Populate cache
curl http://localhost:8000/api/historical/AAPL
curl http://localhost:8000/api/live/AAPL

# Check stats
curl http://localhost:8000/api/cache/stats

# Clear historical namespace
curl -X POST "http://localhost:8000/api/cache/clear?namespace=historical"

# Check stats again
curl http://localhost:8000/api/cache/stats

# Clear all
curl -X POST http://localhost:8000/api/cache/clear

# Check stats
curl http://localhost:8000/api/cache/stats
```

**Pass Criteria**:
- ✅ Namespace clear removes only that namespace
- ✅ Clear all removes everything
- ✅ Stats reflect changes

---

## Performance Benchmarks

### Expected Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Initial Load | 3-5s | <500ms | 90% faster |
| Update Payload | 500KB | 1KB | 99% reduction |
| API Calls/Hour | 360 | 120 | 67% reduction |
| Cache Hit Rate | 0% | >95% | N/A |
| Chart Re-renders | Every update | Only last point | 97% reduction |

### Measuring Performance

**Backend Response Time**:
```bash
# Historical (first call)
time curl -o /dev/null -s http://localhost:8000/api/historical/AAPL
# Expected: 1-2 seconds

# Historical (cached)
time curl -o /dev/null -s http://localhost:8000/api/historical/AAPL
# Expected: <100ms

# Live (cached)
time curl -o /dev/null -s http://localhost:8000/api/live/AAPL
# Expected: <50ms
```

**Frontend Load Time**:
```javascript
// In browser console
performance.timing.loadEventEnd - performance.timing.navigationStart
// Expected: <1000ms
```

---

## Troubleshooting

### Issue: Cache not working

**Symptoms**: Every call shows cache_hit: false

**Solutions**:
1. Check Redis is running: `redis-cli ping`
2. Check backend logs for connection errors
3. Verify cache service initialized: `curl http://localhost:8000/api/cache/stats`
4. Clear cache and retry: `curl -X POST http://localhost:8000/api/cache/clear`

### Issue: Live updates not working

**Symptoms**: No network requests in live mode

**Solutions**:
1. Check browser console for errors
2. Verify backend is running
3. Check live mode is enabled (green indicator)
4. Disable and re-enable live mode

### Issue: Slow initial load

**Symptoms**: First load takes >2 seconds

**Solutions**:
1. Check if data is in feature store
2. Run data ingestion: `python -m data_ingestion.ingestion`
3. Check backend logs for errors
4. Verify database connection

---

## Automated Testing Script

```bash
#!/bin/bash

echo "🧪 AlphaForge Performance Test Suite"
echo "====================================="
echo ""

# Test 1: Cache Stats
echo "Test 1: Cache Stats"
curl -s http://localhost:8000/api/cache/stats | jq '.status'
echo ""

# Test 2: Historical (First Call)
echo "Test 2: Historical Data (First Call)"
curl -X POST -s http://localhost:8000/api/cache/clear > /dev/null
time curl -s http://localhost:8000/api/historical/AAPL | jq '.cache_hit'
echo ""

# Test 3: Historical (Cached)
echo "Test 3: Historical Data (Cached)"
time curl -s http://localhost:8000/api/historical/AAPL | jq '.cache_hit'
echo ""

# Test 4: Live Price
echo "Test 4: Live Price"
time curl -s http://localhost:8000/api/live/AAPL | jq '.price'
echo ""

# Test 5: Payload Size
echo "Test 5: Payload Size Comparison"
echo -n "Historical: "
curl -w '%{size_download} bytes\n' -o /dev/null -s http://localhost:8000/api/historical/AAPL
echo -n "Live: "
curl -w '%{size_download} bytes\n' -o /dev/null -s http://localhost:8000/api/live/AAPL
echo ""

echo "✅ All tests complete!"
```

Save as `scripts/test_performance.sh` and run:
```bash
chmod +x scripts/test_performance.sh
./scripts/test_performance.sh
```

---

## Success Criteria

The optimization is successful if:

✅ Historical endpoint cached response < 100ms
✅ Live endpoint response < 50ms
✅ Payload reduction > 99%
✅ Frontend initial load < 500ms
✅ Live updates smooth (no flicker)
✅ Cache hit rate > 95%
✅ User can control live mode
✅ Error handling works gracefully

---

## Next Steps

After verifying all tests pass:

1. ✅ Deploy to staging environment
2. ✅ Run load tests with multiple users
3. ✅ Monitor cache hit rates
4. ✅ Optimize cache TTL based on usage
5. ✅ Consider WebSocket for real-time updates
6. ✅ Add monitoring and alerting
7. ✅ Document for team

---

## Support

If you encounter issues:

1. Check backend logs: `tail -f logs/app.log`
2. Check Redis logs: `redis-cli MONITOR`
3. Check browser console for frontend errors
4. Review this testing guide
5. Clear cache and retry: `curl -X POST http://localhost:8000/api/cache/clear`
