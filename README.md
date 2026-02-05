# **Redis Core**

*An educational project showcasing how to use Redis with Python, covering both synchronous and asynchronous approaches.* [^1]

[^1]: Redis offers a rich set of features (e.g. data structures, pub/sub, streams, Lua scripting). However, this project focuses on its original and most common use case: a fast, simple, and reliable cache. While Redis can do much more, here I intentionally limit the implementation to classic key-value caching to keep the example clear, educational, and aligned with Redis’s core purpose.

## **Project Structure**

```bash
redis-core/
├── app/                   # Main application code
├── docker-composes/       # Docker Compose configurations for Redis servers
├── .env.example           # Example environment variables file
├── justfile               # Project-specific commands using Just
├── pixi.lock              # Locked dependency versions for reproducible environments
├── pixi.toml              # Pixi project configuration: environments, dependencies, and platforms
└── playground-testing/    # Jupyter notebooks for playground testing
```

Each directory includes its own `README.md` with detailed information about its contents and usage, and every file contains comprehensive inline comments to explain the code.

## **Dependencies Overview**

- [pydantic-settings](https://github.com/pydantic/pydantic-settings) — 
a Pydantic-powered library for managing application configuration and environment variables with strong typing, validation, and seamless `.env` support.

- [redis-py](https://github.com/redis/redis-py) — 
the official Python client for Redis, used here for synchronous and asynchronous caching operations. [^2]

[^2]: I use `redis-py` directly instead of higher-level libraries like `redis-om` because this project focuses solely on simple key-value caching and advanced features are unnecessary for this use case.

- [just](https://github.com/casey/just) — 
a lightweight, cross-platform command runner that replaces complex shell scripts with clean, readable, and reusable project-specific recipes. [^3]

[^3]: Despite using `pixi`, there are issues with `pixi tasks` regarding environment variable handling from `.env` files and caching mechanism that is unclear and causes numerous errors. In contrast, `just` provides predictable, transparent execution without the complications encountered with `pixi tasks` system. I truly hope `pixi tasks` have been improved by the time you’re reading this! <33

### **Testing & Development Dependencies**
- [ipykernel](https://github.com/ipython/ipykernel) — 
the IPython kernel for Jupyter, enabling interactive notebook development and seamless integration with the project’s virtual environments.

## **Quick Start**

### **I. Prerequisites**

- [Docker and Docker Compose](https://docs.docker.com/engine/install/) container tools.
- [Pixi](https://pixi.sh/latest/) package manager.

> **Platform note**: All development and testing were performed on `linux-64`.  
> If you're using a different platform, you’ll need to:
> 1. Update the `platforms` list in the `pixi.toml` accordingly.
> 2. Ensure that platform-specific scripts (e.g., `.sh` files) are compatible with your operating system or replace them with equivalents.

### **II. Environment Setup**

1. **Clone the repository**

    ```bash
    git clone git@github.com:Sierra-Arn/redis-core.git
    cd redis-core
    ```

2. **Install dependencies**
    
    ```bash
    pixi install --all
    ```

3. **Activate pixi environment**
    
    ```bash
    pixi shell
    ```

4. **Setup environment configuration**
    
    ```bash
    just copy-env
    just make-x
    just gen-acl
    ```

### **III. Testing**

Once an environment is ready, you can run and test the Redis cache implementation.

1. **Activate pixi environment**
    
    ```bash
    pixi shell
    ```

2. **Start Redis database**

    ```bash
    just redis-up 2
    ```

3. **Test the implementation**

    Explore the interactive Jupyter notebooks in `playground-testing/`. Additionally, you can open a Redis shell to manually verify that everything is working correctly:
    
    ```bash
    just redis-shell 2
    ```

4. **Cleanup**

    ```bash
    just redis-down 2
    ```

## **License**

This project is licensed under the [BSD-3-Clause License](LICENSE).