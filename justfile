# =====================================================
# Justfile Settings
# =====================================================
# Load environment variables from .env file into justfile context
# This allows justfile recipes to reference variables using ${VAR_NAME} syntax
set dotenv-load := true

# Export all loaded environment variables to child processes
# This makes variables available to all commands executed within recipes
# (e.g., docker compose, shell scripts, and other external tools)
set export := true


# =====================================================
# Environment Setup
# =====================================================
# Create local environment configuration file from template
# Copy .env.example to .env for initial project setup
# After copying, edit .env file to set your specific configuration values
copy-env:
    cp .env.example .env


# =====================================================  
# Redis ACL & Permissions Management  
# =====================================================  
# Make Redis ACL generation script executable  
# Grants execute permissions to the script that dynamically creates Redis user ACL rules  
make-x:  
    chmod +x app/initialization/generate-redis-acl.sh  

# Generate Redis ACL configuration file  
# Executes the ACL script to produce 01-create-users.acl based on current .env settings  
# Output file will be mounted into the Redis container for authentication and access control  
gen-acl:  
    ./app/initialization/generate-redis-acl.sh  


# =====================================================  
# Redis Persistent Storage Management  
# =====================================================  
# Initialize Redis data directory structure  
# Creates the local directory specified by REDIS_DATA_PATH environment variable  
# This directory will store Redis RDB snapshots and AOF persistence files  
init-redis-storage:  
    sudo mkdir -p ${REDIS_DATA_PATH}  

# Remove Redis persistent storage directory and all contents  
delete-redis-storage:  
    sudo rm -rf ${REDIS_DATA_PATH}


# =====================================================  
# Docker Compose 1: Redis Server Initialization  
# =====================================================  
# Start Redis server with ACL-based authentication in detached mode   
#  
# -d flag (detached mode):  
#   Runs containers in the background and releases the terminal immediately.  
#   Without -d, docker compose would stream logs to stdout and block the shell  
#   until interrupted. Detached mode is preferred for long-running services like Redis.  
redis-up-1:  
    docker compose -f docker-composes/docker-compose.1-init.yml --env-file .env up -d  

# Stop and remove Redis containers, networks, and anonymous volumes  
redis-down-1:  
    docker compose -f docker-composes/docker-compose.1-init.yml --env-file .env down


# =====================================================  
# Docker Compose 2: Redis with Interactive Shell Access  
# =====================================================  
# Start Redis server and client containers in detached mode with shell access enabled  
# Uses the same .env configuration for consistency across environments  
# Client container runs an idle process to allow `exec`-based interactive access  
redis-up-2:  
    docker compose -f docker-composes/docker-compose.2-shell.yml --env-file .env up -d  

# !!! For development convenience only — using .env file password variables directly in CLI commands !!!  
# This approach exposes secrets in process lists and command history; never use in production  

# Launch Redis CLI as application user
redis-shell-2:  
    docker compose \
        -f docker-composes/docker-compose.2-shell.yml \
        --env-file .env \
        exec redis-client \
        redis-cli \
            --user "$REDIS_USERNAME" \
            --pass "$REDIS_PASSWORD" \
            -h redis-server \
            -p "$REDIS_INTERNAL_PORT"

# Launch Redis CLI as admin user with full privileges
redis-shell-admin-2:
    docker compose \
        -f docker-composes/docker-compose.2-shell.yml \
        --env-file .env \
        exec redis-client \
        redis-cli \
            --user "$REDIS_ADMIN_USERNAME" \
            --pass "$REDIS_ADMIN_PASSWORD" \
            -h redis-server \
            -p "$REDIS_INTERNAL_PORT"

# Stop and remove Redis containers and networks defined in compose file  
redis-down-2:  
    docker compose -f docker-composes/docker-compose.2-shell.yml --env-file .env down


# =====================================================  
# Docker Compose 3: Persistent Redis Production-like Setup  
# =====================================================  
# Start Redis server with full persistence (RDB + AOF), ACL users, and long-term data retention  
# Designed to simulate a production-ready configuration while remaining manageable in development    
redis-up-3:  
    docker compose -f docker-composes/docker-compose.3-persistent.yml --env-file .env up -d  

# !!! For development convenience only — using .env file password variables directly in CLI commands !!!  
# This approach exposes secrets in process lists and shell history; never use in production environments  

# Launch Redis CLI as application user
redis-shell-3:
    docker compose \
        -f docker-composes/docker-compose.3-persistent.yml \
        --env-file .env \
        exec redis-client \
        redis-cli \
            --user "$REDIS_USERNAME" \
            --pass "$REDIS_PASSWORD" \
            -h redis-server \
            -p "$REDIS_INTERNAL_PORT"

# Launch Redis CLI as admin user with full privileges
redis-shell-admin-3:
    docker compose \
        -f docker-composes/docker-compose.3-persistent.yml \
        --env-file .env \
        exec redis-client \
        redis-cli \
            --user "$REDIS_ADMIN_USERNAME" \
            --pass "$REDIS_ADMIN_PASSWORD" \
            -h redis-server \
            -p "$REDIS_INTERNAL_PORT"

# Stop and remove containers and networks from the persistent Redis setup  
# Persistent data in REDIS_DATA_PATH is preserved for future restarts or backups  
redis-down-3:  
    docker compose -f docker-composes/docker-compose.3-persistent.yml --env-file .env down