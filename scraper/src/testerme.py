import os
from dotenv import load_dotenv
from scraper.src.scraper_utils import setup_logging
from scraper.backend.mongo_utils import get_database, insert_many_documents

logger = setup_logging()

# Load environment variables from the .env file
load_dotenv()

# Global Variables for MongoDB credentials
username = os.getenv("MONGO_DB_USERNAME_TEST")
password = os.getenv("MONGO_DB_PASSWORD_TEST")

ca_file = os.path.join(os.path.dirname(__file__), '../backend/isrgrootx1.pem')

def main():
    print("Starting MongoDB test...")

    # Connect to MongoDB
    logger.info("Connecting to MongoDB...")
    collection = get_database("shrama_vasana_fund_uat", "test_data", username, password, ca_file)

    # Sample data to insert
    test_data = [
        {"name": "Test Entry 1", "description": "This is a test entry."},
        {"name": "Test Entry 2", "description": "Another test entry."}
    ]

    # Insert the sample data into MongoDB
    logger.info("Inserting test data into MongoDB...")
    inserted_ids = insert_many_documents(collection, test_data)

    logger.info(f"Inserted {len(inserted_ids)} documents into MongoDB.")
    print("Done with MongoDB test.")

if __name__ == "__main__":
    main()
