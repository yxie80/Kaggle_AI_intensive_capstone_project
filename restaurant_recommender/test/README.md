# Test Folder Quick Reference

## Location

```plain
restaurant_recommender/test/
```

## Files

- `test_debug.py` - Conversation flow verification
- `test_debug2.py` - State tracking verification  
- `test_input.txt` - CLI automated input

## Quick Commands

### Run All Tests

```bash
cd restaurant_recommender
echo "=== Test 1: Flow ===" && pipenv run python3 test/test_debug.py && \
echo "" && echo "=== Test 2: State ===" && pipenv run python3 test/test_debug2.py && \
echo "" && echo "=== Test 3: CLI ===" && timeout 30 bash -c 'cat test/test_input.txt | pipenv run python3 main.py'
```

### Run Individual Tests

```bash
# Flow test
pipenv run python3 test/test_debug.py

# State test
pipenv run python3 test/test_debug2.py

# CLI test
cat test/test_input.txt | pipenv run python3 main.py
```

## Test Results: ✅ ALL PASSING

| Test | Duration | Status |
|------|----------|--------|
| test_debug.py | ~1s | ✅ |
| test_debug2.py | ~1s | ✅ |
| CLI Test | ~2s | ✅ |
| **Total** | **~4s** | **✅** |

## What's Being Tested

### test_debug.py

✅ Location geocoding → Melbourne CBD (coordinates)
✅ Energy assessment → 1000m search radius
✅ Budget extraction → "Mid-range" level 2
✅ Group size → 2 people (couple)
✅ Cuisine detection → Thai
✅ Restaurant discovery → 4 restaurants found
✅ Recommendations → Top 3 with ratings and distances

### test_debug2.py

✅ State creation and persistence
✅ Each state field updated correctly
✅ Location: -37.8136, 144.9631 (Melbourne CBD)
✅ Energy: level 2 (tired)
✅ Budget: level 2 (mid-range)
✅ Group: 2 people
✅ Cuisine: Thai
✅ Candidates: 4 found
✅ Recommendations: 3 generated

### test_input.txt + CLI Test

✅ Full end-to-end conversation
✅ 8 automated inputs processed
✅ Real Google Places API data
✅ Distance formatting: km with 1 decimal
✅ Restaurant selection: Zawaddi Thai (0.4 km away)
✅ Final state captured and displayed
✅ Graceful exit without errors

## Test Coverage

- ✅ Location Collection
- ✅ Energy Assessment  
- ✅ Budget Collection
- ✅ Group Size Parsing
- ✅ Cuisine Detection
- ✅ Restaurant Discovery (Real API)
- ✅ Recommendation Generation
- ✅ State Management
- ✅ Restaurant Selection
- ✅ Distance Formatting
- ✅ Error Handling

## Next Steps

- Use `test/test_debug.py` to verify conversation flow after changes
- Use `test/test_debug2.py` to verify state management
- Use CLI test with `test_input.txt` for full integration testing
- Add new test files to `test/` folder for new features

---

**Status: Production Ready** ✅
