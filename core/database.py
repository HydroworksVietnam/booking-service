from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create MongoDB client
from models.service import Service
from models.appointment import Appointment
# Handle both local (no auth) and production (with auth) connections
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

if db_user and db_password:
    client = AsyncIOMotorClient(
        f"mongodb://{db_user}:{db_password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    )
else:
    client = AsyncIOMotorClient(f"mongodb://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/")

# Get database
db = client[os.getenv('DB_NAME', 'automation_crm')]

# Initialize beanie
async def init_db():
    try:
        # Ensure models are imported
        from models.service import Service
        from models.appointment import Appointment

        # Initialize Beanie with document models
        await init_beanie(
            database=db,
            document_models=[
                Service,
                Appointment
            ]
        )
        logger.info(f"Successfully connected to database: {db.name}")
        logger.info(f"Registered models: {[model.__name__ for model in [Service, Appointment]]}")
        logger.info(f"Appointment model collection name: {Appointment.get_settings().name}")

        # Explicitly check and create collections if they don't exist
        collections = await db.list_collection_names()
        # Get collection names from models to ensure consistency
        required_collections = [Service.get_settings().name, Appointment.get_settings().name]
        created_collections = []

        for coll in required_collections:
            if coll not in collections:
                # Create collection
                await db.create_collection(coll)
                created_collections.append(coll)

        if created_collections:
            logger.info(f"Created missing collections: {created_collections}")
        else:
            logger.info("All required collections already exist")

    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)

# Dependency to get database
def get_db():
    return db