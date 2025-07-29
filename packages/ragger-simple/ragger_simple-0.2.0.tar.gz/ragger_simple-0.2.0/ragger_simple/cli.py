import argparse
import json
import os
from .db import VectorDB
from qdrant_client.http.models import Distance, VectorParams, Filter
from pathlib import Path
import logging

def get_config_path():
    """Get the path to the config file."""
    config_dir = Path.home() / ".ragger-simple"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"

def save_config(config):
    """Save configuration to file."""
    with open(get_config_path(), "w") as f:
        json.dump(config, f)
    print(f"Configuration saved to {get_config_path()}")

def load_config():
    """Load configuration from file."""
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
            print(f"Loaded configuration from {config_path}")
            return config
    print(f"No configuration found at {config_path}")
    return {}

def main():
    parser = argparse.ArgumentParser(description="Vector Database Operations with Qdrant")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Initialize command
    init_parser = subparsers.add_parser("init", help="Initialize vector database")
    init_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress debug messages")
    init_parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Embedding model name")
    init_parser.add_argument("--collection", default="documents", help="Collection name")
    init_parser.add_argument("--qdrant-url", help="Qdrant server URL (for cloud)")
    init_parser.add_argument("--qdrant-key", help="Qdrant API key (for cloud)")
    init_parser.add_argument("--qdrant-path", help="Path for local Qdrant database")
    
    # Process documents command
    process_parser = subparsers.add_parser("process", help="Process documents into vector database")
    process_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress debug messages")
    process_parser.add_argument("--input", required=True, help="JSON file with documents {name: text}")
    process_parser.add_argument("--collection", default="documents", help="Collection name")
    process_parser.add_argument("--chunk-size", type=int, default=200, help="Chunk size in words")
    process_parser.add_argument("--overlap", type=int, default=50, help="Overlap between chunks")
    process_parser.add_argument("--qdrant-url", help="Qdrant server URL (for cloud)")
    process_parser.add_argument("--qdrant-key", help="Qdrant API key (for cloud)")
    process_parser.add_argument("--qdrant-path", help="Path for local Qdrant database")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search relevant chunks for query")
    search_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress debug messages")
    search_parser.add_argument("--query", required=True, help="Query text")
    search_parser.add_argument("--collection", default="documents", help="Collection name")
    search_parser.add_argument("--k", type=int, default=5, help="Number of results to return")
    search_parser.add_argument("--output", help="Output file for results (default: print to console)")
    search_parser.add_argument("--qdrant-url", help="Qdrant server URL (for cloud)")
    search_parser.add_argument("--qdrant-key", help="Qdrant API key (for cloud)")
    search_parser.add_argument("--qdrant-path", help="Path for local Qdrant database")
    
    # List collections command
    list_parser = subparsers.add_parser("list-collections", help="List all collections in database")
    list_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress debug messages")
    list_parser.add_argument("--qdrant-url", help="Qdrant server URL (for cloud)")
    list_parser.add_argument("--qdrant-key", help="Qdrant API key (for cloud)")
    list_parser.add_argument("--qdrant-path", help="Path for local Qdrant database")
    
    # Purge collection command
    purge_parser = subparsers.add_parser("delete-collection", help="Completely delete a collection from the database")
    purge_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress debug messages")
    purge_parser.add_argument("--collection", required=True, help="Collection name to delete")
    purge_parser.add_argument("--confirm", action="store_true", help="Confirm deletion without prompting")
    purge_parser.add_argument("--qdrant-url", help="Qdrant server URL (for cloud)")
    purge_parser.add_argument("--qdrant-key", help="Qdrant API key (for cloud)")
    purge_parser.add_argument("--qdrant-path", help="Path for local Qdrant database")
    
    # Collection stats command
    stats_parser = subparsers.add_parser("collection-stats", help="Show statistics about a collection")
    stats_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress debug messages")
    stats_parser.add_argument("--collection", required=True, help="Collection name to get stats for")
    stats_parser.add_argument("--qdrant-url", help="Qdrant server URL (for cloud)")
    stats_parser.add_argument("--qdrant-key", help="Qdrant API key (for cloud)")
    stats_parser.add_argument("--qdrant-path", help="Path for local Qdrant database")
    
    args = parser.parse_args()
    
    # Set logging level based on quiet flag
    if hasattr(args, 'quiet') and args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
        # Also silence specific loggers
        logging.getLogger("httpcore").setLevel(logging.ERROR)
        logging.getLogger("httpx").setLevel(logging.ERROR)
        logging.getLogger("qdrant_client").setLevel(logging.WARNING)
    
    # Load saved config
    config = load_config()
    
    # Build params with proper fallback logic
    db_params = {}
    
    # Collection name parameter
    if hasattr(args, 'collection'):
        db_params["collection_name"] = args.collection
    elif "collection_name" in config:
        db_params["collection_name"] = config["collection_name"]
    else:
        db_params["collection_name"] = "documents"
    
    # Qdrant URL parameter
    if hasattr(args, 'qdrant_url') and args.qdrant_url:
        db_params["qdrant_url"] = args.qdrant_url
    elif "qdrant_url" in config:
        db_params["qdrant_url"] = config["qdrant_url"]
    
    # Qdrant API key parameter
    if hasattr(args, 'qdrant_key') and args.qdrant_key:
        db_params["qdrant_api_key"] = args.qdrant_key
    elif "qdrant_api_key" in config:
        db_params["qdrant_api_key"] = config["qdrant_api_key"]
    
    # Qdrant path parameter
    if hasattr(args, 'qdrant_path') and args.qdrant_path:
        db_params["qdrant_path"] = args.qdrant_path
    elif "qdrant_path" in config:
        db_params["qdrant_path"] = config["qdrant_path"]
    
    # Print connection details (for debugging)
    print(f"Using connection settings:")
    print(f"  Collection: {db_params.get('collection_name')}")
    print(f"  Qdrant URL: {db_params.get('qdrant_url') or 'None (using local)'}")
    
    if args.command == "init":
        # Save configuration for future use
        config_to_save = {
            "collection_name": db_params.get("collection_name", "documents"),
            "qdrant_url": db_params.get("qdrant_url"),
            "qdrant_api_key": db_params.get("qdrant_api_key"),
            "qdrant_path": db_params.get("qdrant_path")  # Using .get() avoids KeyError
        }
        save_config(config_to_save)
        print("Configuration saved for future commands")
        
        # Continue with initialization...
        db_params["model_name"] = args.model
        db = VectorDB(**db_params)
        print(f"Vector database initialized with model {args.model}")
    
    elif args.command == "process":
        db = VectorDB(**db_params)
        with open(args.input, 'r') as f:
            documents = json.load(f)
        db.add_documents(documents, args.chunk_size, args.overlap)
    
    elif args.command == "search":
        db = VectorDB(**db_params)
        results = db.search(args.query, args.k)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
        else:
            print(json.dumps(results, indent=2))
            
    # List collections implementation
    elif args.command == "list-collections":
        db = VectorDB(**db_params)
        collections = db.list_collections()
        print("Available collections:")
        for collection in collections:
            print(f"- {collection}")
            
    # Purge collection implementation
    elif args.command == "delete-collection":
        if not args.confirm:
            confirmation = input(f"Are you sure you want to COMPLETELY DELETE collection '{args.collection}'? (yes/no): ")
            if confirmation.lower() != "yes":
                print("Operation cancelled.")
                return
        
        db = VectorDB(**db_params)
        # Use delete_collection instead of purge_collection
        success = db.delete_collection(args.collection)
        if success:
            print(f"Collection '{args.collection}' has been completely deleted.")
        else:
            print(f"Failed to delete collection '{args.collection}'.")
    
    # Collection stats implementation
    elif args.command == "collection-stats":
        db = VectorDB(**db_params)
        stats = db.get_collection_stats(args.collection)
        
        if "error" in stats:
            print(f"Error: {stats['error']}")
        else:
            print(f"\nCollection: {stats['name']}")
            print(f"Status: {stats['status']}")
            print(f"Vectors count: {stats['vectors_count']}")
            print(f"Vector size: {stats['vector_size']}")
            print(f"Distance: {stats['distance']}")
    
    else:
        parser.print_help()