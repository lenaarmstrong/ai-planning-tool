#!/bin/bash

# Run container 1
cd retrieve_papers
pipenv lock --clear
docker build --no-cache -t retrieve_papers .
docker run --rm -ti -v "$(pwd)":/app retrieve_papers python retrieve_papers.py
# docker wait container1  # Wait for container1 to finish

# Run container 2
cd ../embed_papers
pipenv lock --clear
docker build --no-cache -t embed_papers .
docker run --rm -ti -v "$(pwd)":/app embed_papers python embed_papers.py
# docker wait container2  # Wait for container2 to finish

# Run container 3
cd ../perform_rag
pipenv lock --clear
docker build --no-cache -t perform_rag .
docker run --rm -ti -v "$(pwd)":/app perform_rag python perform_rag.py
# docker wait container3  # Wait for container3 to finish

echo "All containers have finished running."
