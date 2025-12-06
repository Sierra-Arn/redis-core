# **Application Structure**

*This README provides a high-level architectural overview of the project: what each component is for and why it exists. For implementation details refer to the docstrings and comments inside each file.*

## **I. `db/` — The Data Layer**

1. **`config.py`**  
    Provides Redis configuration singleton built with Pydantic, loaded from `.env` with strict validation.

2. **`client.py`**  
    Provides Redis client singletons — synchronous and asynchronous — pre-configured from validated settings.

3. **`decorators.py`**  
    Provides caching and invalidation decorators — designed to be applied directly to functions or methods that need Redis caching, eliminating the need for manual cache logic or dedicated service wrappers.

4. **`serializers.py`**  
    Handles data encoding/decoding between Python objects and Redis-compatible formats (e.g., JSON and pickle).

5. **`services/`**  
    Provides mock implementations that demonstrate use of decorators across both synchronous and asynchronous code.

## **II. `initialization/` — Bootstrapping Redis**

1. **`01-create-users.acl`**  
    Defines multiple Redis users and assigns minimal necessary permissions to each, following the principle of least privilege.

2. **`generate-redis-acl.sh`**  
    Shell script that generates the `01-create-users.acl` file by injecting Redis credentials from `.env` — bypassing the ACL format’s lack of environment variables support.

3. **`README.md`**  
    Documents the role-based access control (RBAC) model used in this project. It explains: 
    - which Redis users exist,
    - what permissions each one holds,
    - why those specific permissions are granted.