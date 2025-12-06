# **Redis ACL Configuration**

This section defines a role-based access control (RBAC) model for Redis, using dedicated users with minimal, purpose-driven permissions.

## **I. Administrative User**

```bash
user ${REDIS_ADMIN_USERNAME} on >${REDIS_ADMIN_PASSWORD} ~* &* +@all
```

### **Assigned permissions**

- **`~*`**  
    Full access to all keyspaces, enabling management of any data stored in Redis.
- **`&*`**  
    Access to all Pub/Sub channels, necessary for monitoring and broadcasting system-wide events.
- **`+@all`**  
    Grants execution rights to every Redis command category, including administrative and dangerous operations.

### **Role purpose**

Provides full administrative control over the Redis instance.

## **II. Caching User**

```bash
user ${REDIS_USERNAME} on >${REDIS_PASSWORD} ~* +get +set +del +exists +expire +pexpire +ttl +pttl +mget +mset +setex
```

### **Assigned permissions**

- **`~*`**  
    Grants access to all keys in the Redis instance across all database indexes. [^1]  

[^1]: Redis ACLs do not support restricting access to specific database numbers (e.g. `SELECT 2`). The key space is global from the ACL perspective. If key-level isolation is required, it is strongly recommended to use **key name prefixes** (e.g. `~cache:*`) and design your application to operate within that namespace. In this educational project, such isolation is intentionally omitted for simplicity, but the prefix-based approach remains the standard best practice for production environments.

- **`+get`**  
    Allows reading the value of a key. Essential for retrieving cached data.

- **`+set`**  
    Enables setting a key to a given value with optional expiration. Used to store new or updated cached entries.

- **`+del`**  
    Permits deletion of one or more keys. Useful for invalidating stale or obsolete cache entries.

- **`+exists`**  
    Checks whether a key exists. Often used to avoid unnecessary `GET` operations or to implement cache-existence logic.

- **`+expire`**  
    Sets a time-to-live (TTL) in seconds on an existing key. Critical for automatic cache expiration.

- **`+pexpire`**  
    Sets a TTL in milliseconds on an existing key. Provides finer-grained control over expiration timing.

- **`+ttl`**  
    Retrieves the remaining TTL of a key in seconds. Helpful for cache introspection or adaptive caching logic.

- **`+pttl`**  
    Retrieves the remaining TTL of a key in milliseconds. Offers higher precision for TTL inspection.

- **`+mget`**  
    Fetches values for multiple keys in a single request. Improves efficiency when loading several cached items at once.

- **`+mset`**  
    Sets multiple key-value pairs atomically in one operation. Optimizes bulk cache population.

- **`+setex`**  
    Sets a key with a value and a TTL in seconds in a single atomic command. Combines `set` and `expire` for convenience and performance.

### **Role purpose**

This user is designed exclusively for caching operations, with no access to administrative, dangerous, or non-caching-related commands. It follows the **principle of least privilege**, ensuring security while supporting all standard read/write/expire patterns.

## **III. Security: Disable the default user**

```bash
user default off nopass
```

### **Historical Context and Evolution**

**Redis < 6.0 (Legacy Era)**  
- No user or access control system existed.
- A single implicit "default" user handled all connections.
- Authentication (if used) was limited to a global `requirepass` setting — effectively one shared password for all clients.
- All authenticated clients had unrestricted access to the entire server.

**Redis >= 6.0 (ACL Era)**  
- Introduced a full-featured Access Control List (ACL) system.
- Supports multiple named users, each with independent passwords and fine-grained permissions.
- Provides precise control over which commands, keys, and Pub/Sub channels a user can access.
- The `default` user was retained **solely for backward compatibility** with legacy deployments.

**Current Security Risk**  
- By default, the `default` user retains full privileges (`~* &* +@all`) **and has no password** (`nopass`).
- This means **any unauthenticated connection automatically receives full administrative access** — a critical security vulnerability.
- In modern deployments, this contradicts basic security principles and can lead to unauthorized data access or system compromise.

**Official Redis Guidance**  
- Explicitly disable the `default` user in all production environments.
- Create dedicated named users with least-privilege permissions tailored to each application’s needs.

# **Critical ACL File Limitations**

1. **No Environment Variables**  
Redis ACL files cannot interpolate environment variables like `${REDIS_ADMIN_USERNAME}` — they are read literally.
2. **No Line Continuation**  
The `\` character for line continuation is not supported — each user definition must be on a single, complete line.

Due to these limitations, this project does **not** include a static `.acl` file with embedded environment variables. Instead, a dedicated initialization script (`generate-acl.sh`) dynamically generates the final ACL file at startup by substituting values from the `.env` file into a template. This ensures that Redis receives a syntactically valid ACL file containing concrete usernames and passwords, while still allowing configuration via environment variables in development and deployment environments.