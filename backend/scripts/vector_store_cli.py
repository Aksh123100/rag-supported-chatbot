"""
Utility script to interact with the vector store.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vectorstore import VectorStoreService
from app.config import settings


def main():
    """Interactive CLI for vector store operations."""
    vector_store = VectorStoreService()

    while True:
        print("\n" + "=" * 50)
        print("Vector Store CLI")
        print("=" * 50)
        print("1. View statistics")
        print("2. Search documents")
        print("3. Clear all documents")
        print("4. Exit")
        print("-" * 50)

        choice = input("Enter choice (1-4): ").strip()

        if choice == "1":
            stats = vector_store.get_stats()
            print(f"\nCollection: {stats['collection_name']}")
            print(f"Document Count: {stats['document_count']}")
            print(f"Persist Directory: {stats['persist_directory']}")

        elif choice == "2":
            query = input("\nEnter search query: ").strip()
            if query:
                results = vector_store.query(query_text=query, n_results=5)

                print(f"\nTop {len(results['ids'][0])} results:")
                for i, doc in enumerate(results['documents'][0]):
                    print(f"\n--- Result {i+1} ---")
                    print(doc[:200] + "..." if len(doc) > 200 else doc)
                    print(f"Score: {1 - results['distances'][0][i]:.3f}")

        elif choice == "3":
            confirm = input("\nAre you sure? This will delete all documents. (yes/no): ").strip()
            if confirm.lower() == "yes":
                vector_store.clear_collection()
                print("All documents cleared.")
            else:
                print("Operation cancelled.")

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")