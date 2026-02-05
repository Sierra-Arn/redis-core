# **Testing and Exploration**

Two Jupyter notebooks are provided for interactive experimentation with Redis: one for synchronous workflows, another for asynchronous patterns.

Additionally, you can always connect directly to the Redis container and manually inspect the database state using standard redis-cli commands like:

1. **View all databases:**
   ```sql
   INFO keyspace
   ```

2. **View keys in current keyspace:**
   ```sql
   SELECT <database_number> 
   SCAN 0 COUNT 100
   ```
   Or to see all keys at once:
   ```sql
   SELECT <database_number> 
   KEYS *
   ```

3. **View all users/roles:**
   ```sql
   ACL LIST
   ```

4. **Exit redis-cli:**
   ```sql
   exit
   ```