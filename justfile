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
# Redis Docker Compose Management
# =====================================================

# Start Redis server based on specified composition number
# Usage: just redis-up <number>
#   number=1: Basic server with ACL-based authentication (docker-compose.1-init.yml)
#   number=2: Server with interactive shell access (docker-compose.2-shell.yml)
#   number=3: Persistent production-like setup (docker-compose.3-persistent.yml)

redis-up number:
    #!/usr/bin/env bash
    if [ "{{ number }}" = "1" ]; then
        # Docker Compose 1: Redis Server Initialization
        # Start Redis server with ACL-based authentication in detached mode
        #
        # -d flag (detached mode):
        #   Runs containers in the background and releases the terminal immediately.
        #   Without -d, docker compose would stream logs to stdout and block the shell
        #   until interrupted. Detached mode is preferred for long-running services like Redis.
        docker compose -f docker-composes/docker-compose.1-init.yml --env-file .env up -d
    elif [ "{{ number }}" = "2" ]; then
        # Docker Compose 2: Redis with Interactive Shell Access
        # Start Redis server and client containers in detached mode with shell access enabled
        # Uses the same .env configuration for consistency across environments
        # Client container runs an idle process to allow `exec`-based interactive access
        docker compose -f docker-composes/docker-compose.2-shell.yml --env-file .env up -d
    elif [ "{{ number }}" = "3" ]; then
        # Docker Compose 3: Persistent Redis Production-like Setup
        # Start Redis server with full persistence (RDB + AOF), ACL users, and long-term data retention
        # Designed to simulate a production-ready configuration while remaining manageable in development
        docker compose -f docker-composes/docker-compose.3-persistent.yml --env-file .env up -d
    else
        echo "Error: Invalid composition number. Use 1, 2, or 3."
        exit 1
    fi

# Stop and remove Redis containers based on specified composition number
# Usage: just redis-down <number>
#   number=1: Stop basic server instance
#   number=2: Stop server with shell access
#   number=3: Stop persistent instance (data in REDIS_DATA_PATH is preserved)

redis-down number:
    #!/usr/bin/env bash
    if [ "{{ number }}" = "1" ]; then
        # Stop and remove Redis containers, networks, and anonymous volumes
        docker compose -f docker-composes/docker-compose.1-init.yml --env-file .env down
    elif [ "{{ number }}" = "2" ]; then
        # Stop and remove Redis containers and networks defined in compose file
        docker compose -f docker-composes/docker-compose.2-shell.yml --env-file .env down
    elif [ "{{ number }}" = "3" ]; then
        # Stop and remove containers and networks from the persistent Redis setup
        # Persistent data in REDIS_DATA_PATH is preserved for future restarts or backups
        docker compose -f docker-composes/docker-compose.3-persistent.yml --env-file .env down
    else
        echo "Error: Invalid composition number. Use 1, 2, or 3."
        exit 1
    fi


# =====================================================
# Redis Interactive Shell Access
# =====================================================
# !!! For development convenience only — using .env file password variables directly in CLI commands !!!
# This approach exposes secrets in process lists and command history; never use in production

# Launch Redis CLI based on composition number and user type
# Usage: just redis-shell <number> [admin]
#   number=2: Shell access via docker-compose.2-shell.yml
#   number=3: Shell access via docker-compose.3-persistent.yml
#   admin: Optional flag to connect as superuser instead of application user

redis-shell number user="app":
    #!/usr/bin/env bash
    if [ "{{ number }}" = "2" ]; then
        if [ "{{ user }}" = "admin" ]; then
            # Launch Redis CLI as admin user with full privileges
            docker compose \
                -f docker-composes/docker-compose.2-shell.yml \
                --env-file .env \
                exec redis-client \
                redis-cli \
                    --user "$REDIS_ADMIN_USERNAME" \
                    --pass "$REDIS_ADMIN_PASSWORD" \
                    -h redis-server \
                    -p "$REDIS_INTERNAL_PORT"
        else
            # Launch Redis CLI as application user
            docker compose \
                -f docker-composes/docker-compose.2-shell.yml \
                --env-file .env \
                exec redis-client \
                redis-cli \
                    --user "$REDIS_USERNAME" \
                    --pass "$REDIS_PASSWORD" \
                    -h redis-server \
                    -p "$REDIS_INTERNAL_PORT"
        fi
    elif [ "{{ number }}" = "3" ]; then
        if [ "{{ user }}" = "admin" ]; then
            # Launch Redis CLI as admin user with full privileges
            docker compose \
                -f docker-composes/docker-compose.3-persistent.yml \
                --env-file .env \
                exec redis-client \
                redis-cli \
                    --user "$REDIS_ADMIN_USERNAME" \
                    --pass "$REDIS_ADMIN_PASSWORD" \
                    -h redis-server \
                    -p "$REDIS_INTERNAL_PORT"
        else
            # Launch Redis CLI as application user
            docker compose \
                -f docker-composes/docker-compose.3-persistent.yml \
                --env-file .env \
                exec redis-client \
                redis-cli \
                    --user "$REDIS_USERNAME" \
                    --pass "$REDIS_PASSWORD" \
                    -h redis-server \
                    -p "$REDIS_INTERNAL_PORT"
        fi
    else
        echo "Error: Invalid composition number. Use 2 or 3."
        exit 1
    fi