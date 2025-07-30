"""
Lua scripts for atomic Redis operations in feature store.

These scripts eliminate multiple round trips by combining operations
into single atomic calls, targeting P95 ≤ 300µs performance.

Performance Polish: Consolidated scripts to reduce redundancy and improve maintainability.
"""

# Unified atomic operation script - consolidates HINCRBY_WITH_TTL and HSET_WITH_TTL
UNIFIED_HASH_OPERATION = """
-- KEYS[1] = hash_key
-- ARGV[1] = operation ("hincrby" or "hset")
-- ARGV[2] = field
-- ARGV[3] = value/amount
-- ARGV[4] = ttl_seconds
local hash_key = KEYS[1]
local operation = ARGV[1]
local field = ARGV[2]
local value = tonumber(ARGV[3]) or ARGV[3]
local ttl_seconds = tonumber(ARGV[4])

local result
if operation == "hincrby" then
    result = redis.call('HINCRBY', hash_key, field, value)
elseif operation == "hset" then
    result = redis.call('HSET', hash_key, field, value)
else
    return redis.error_reply("Invalid operation: " .. operation)
end

-- Set TTL only if not already set (TTL returns -1 if no TTL)
if redis.call('TTL', hash_key) < 0 then
    redis.call('EXPIRE', hash_key, ttl_seconds)
end

return result
"""

# Legacy scripts for backward compatibility - will be deprecated
HINCRBY_WITH_TTL = """
-- KEYS[1] = hash_key, ARGV[1] = field, ARGV[2] = amount, ARGV[3] = ttl_seconds
local current = redis.call('HINCRBY', KEYS[1], ARGV[1], ARGV[2])

-- Set TTL only if not already set (TTL returns -1 if no TTL)
if redis.call('TTL', KEYS[1]) < 0 then
    redis.call('EXPIRE', KEYS[1], ARGV[3])
end

return current
"""

HSET_WITH_TTL = """
-- KEYS[1] = hash_key, ARGV[1] = field, ARGV[2] = value, ARGV[3] = ttl_seconds
local result = redis.call('HSET', KEYS[1], ARGV[1], ARGV[2])

-- Set TTL only if not already set
if redis.call('TTL', KEYS[1]) < 0 then
    redis.call('EXPIRE', KEYS[1], ARGV[3])
end

return result
"""

# Get specific bucket fields (HMGET optimization)
GET_WINDOW_BUCKETS = """
-- KEYS[1] = hash_key, ARGV[1..N] = bucket_fields to retrieve
-- Returns values for requested bucket fields only
return redis.call('HMGET', KEYS[1], unpack(ARGV))
"""

# Enhanced batch operations with parameter-driven TTL
ENHANCED_BATCH_HINCRBY = """
-- KEYS[1] = hash_key
-- ARGV = [field1, amount1, field2, amount2, ..., fieldN, amountN, ttl_seconds]
-- Last argument is always TTL
local hash_key = KEYS[1]
local ttl_seconds = tonumber(ARGV[#ARGV])
local results = {}

-- Process field/amount pairs (all args except last one which is TTL)
for i = 1, #ARGV - 1, 2 do
    local field = ARGV[i]
    local amount = tonumber(ARGV[i + 1])
    if field and amount then
        local current = redis.call('HINCRBY', hash_key, field, amount)
        table.insert(results, current)
    end
end

-- Set TTL only if not already set
if redis.call('TTL', hash_key) < 0 then
    redis.call('EXPIRE', hash_key, ttl_seconds)
end

return results
"""

# Optimized rolling window with configurable decay factor and TTL
ENHANCED_ROLLING_WINDOW = """
-- KEYS[1] = hash_key
-- ARGV[1] = current_time
-- ARGV[2] = decay_factor (optional, defaults to 0.9)
-- ARGV[3] = window_size_seconds (optional, defaults to 60)
-- ARGV[4] = ttl_seconds
local hash_key = KEYS[1]
local current_time = tonumber(ARGV[1])
local decay_factor = tonumber(ARGV[2]) or 0.9
local window_size = tonumber(ARGV[3]) or 60.0
local ttl_seconds = tonumber(ARGV[4])

-- Get current rolling value and last update time
local rolling_data = redis.call('HMGET', hash_key, 'value', 'last_update')
local current_value = tonumber(rolling_data[1]) or 0
local last_update = tonumber(rolling_data[2]) or current_time

-- Calculate time difference and apply decay
local time_diff = current_time - last_update
local decayed_value = current_value * math.exp(-time_diff / window_size)

-- Add new event and update
local new_value = decayed_value + 1

-- Store updated values using HSET for better performance
redis.call('HSET', hash_key, 'value', new_value, 'last_update', current_time)

-- Set TTL if needed
if redis.call('TTL', hash_key) < 0 then
    redis.call('EXPIRE', hash_key, ttl_seconds)
end

return new_value
"""

# High-performance bulk operation for sliding windows
BULK_WINDOW_OPERATION = """
-- KEYS[1] = hash_key
-- ARGV[1] = operation_type ("increment" or "unique")
-- ARGV[2] = current_time
-- ARGV[3] = window_size_seconds
-- ARGV[4] = ttl_seconds
-- ARGV[5..N] = operation-specific data
local hash_key = KEYS[1]
local op_type = ARGV[1]
local current_time = tonumber(ARGV[2])
local window_size = tonumber(ARGV[3])
local ttl_seconds = tonumber(ARGV[4])

-- Calculate cutoff time for window cleanup
local cutoff_time = current_time - window_size
local bucket_size = 60  -- 60-second buckets
local current_bucket = math.floor(current_time / bucket_size)
local cutoff_bucket = math.floor(cutoff_time / bucket_size)

local results = {}

if op_type == "increment" then
    -- ARGV[5] = amount to increment
    local amount = tonumber(ARGV[5]) or 1
    local bucket_field = tostring(current_bucket)
    
    -- Increment current bucket
    local new_value = redis.call('HINCRBY', hash_key, bucket_field, amount)
    table.insert(results, new_value)
    
    -- Clean up old buckets (limit to prevent performance impact)
    local all_fields = redis.call('HKEYS', hash_key)
    local cleaned = 0
    for _, field in ipairs(all_fields) do
        local bucket_num = tonumber(field)
        if bucket_num and bucket_num < cutoff_bucket and cleaned < 10 then
            redis.call('HDEL', hash_key, field)
            cleaned = cleaned + 1
        end
    end
    
elseif op_type == "unique" then
    -- ARGV[5] = unique_value
    local unique_value = ARGV[5]
    local bucket_field = tostring(current_bucket) .. ":" .. unique_value
    
    -- Set unique value
    local new_field = redis.call('HSET', hash_key, bucket_field, "1")
    table.insert(results, new_field)
    
    -- Clean up old unique values
    local all_fields = redis.call('HKEYS', hash_key)
    local cleaned = 0
    for _, field in ipairs(all_fields) do
        local bucket_part = string.match(field, "^(%d+):")
        if bucket_part then
            local bucket_num = tonumber(bucket_part)
            if bucket_num and bucket_num < cutoff_bucket and cleaned < 10 then
                redis.call('HDEL', hash_key, field)
                cleaned = cleaned + 1
            end
        end
    end
end

-- Set TTL if needed
if redis.call('TTL', hash_key) < 0 then
    redis.call('EXPIRE', hash_key, ttl_seconds)
end

return results
"""

# Legacy scripts for backward compatibility
BATCH_HINCRBY = ENHANCED_BATCH_HINCRBY  # Alias for compatibility
ROLLING_WINDOW_UPDATE = ENHANCED_ROLLING_WINDOW  # Alias for compatibility
