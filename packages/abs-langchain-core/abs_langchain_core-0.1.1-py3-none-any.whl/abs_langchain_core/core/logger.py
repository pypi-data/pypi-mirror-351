from typing import Optional, Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path
import logging

from ..models.usage import UsageLog

logger = logging.getLogger(__name__)

#TODO: NEED to add with the nosql repository core
class UsageLogger:
    """Logger for tracking token usage in LangChain operations."""

    def __init__(
        self,
        log_dir: Optional[str] = None,
        log_to_file: bool = False,
        log_to_mongo: bool = True,
        mongo_uri: Optional[str] = None,
        mongo_db: str = "langchain_usage",
        mongo_collection: str = "usage_logs",
    ):
        """Initialize the usage logger.

        Args:
            log_dir: Directory to store log files
            log_to_file: Whether to log to file
            log_to_mongo: Whether to log to MongoDB
            mongo_uri: MongoDB connection URI
            mongo_db: MongoDB database name
            mongo_collection: MongoDB collection name
        """
        self.log_to_file = log_to_file
        self.log_to_mongo = log_to_mongo

        # Setup file logging
        if log_to_file:
            self.log_dir = Path(log_dir or "logs")
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self.log_file = self.log_dir / f"usage_{datetime.now().strftime('%Y%m%d')}.jsonl"

        # Setup MongoDB logging
        if log_to_mongo:
            try:
                if not mongo_uri:
                    mongo_uri = os.getenv("MONGODB_URI")
                    if not mongo_uri:
                        logger.warning("MongoDB URI not provided and MONGODB_URI env var not set. MongoDB logging will be disabled.")
                        self.log_to_mongo = False
                        return
                #todo : motor need to use
                from pymongo import MongoClient
                self.mongo_client = MongoClient(mongo_uri)
                # Test the connection
                self.mongo_client.admin.command('ping')
                self.mongo_db = self.mongo_client[mongo_db]
                self.mongo_collection = self.mongo_db[mongo_collection]
                logger.info("Successfully connected to MongoDB for usage logging")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                self.log_to_mongo = False

    def log_usage(self, usage_log: UsageLog) -> None:
        """Log token usage.

        Args:
            usage_log: Usage log to store
        """
        try:
            # Convert to dict for storage
            log_dict = usage_log.model_dump()

            # Log to file if enabled
            if self.log_to_file:
                with open(self.log_file, "a") as f:
                    f.write(json.dumps(log_dict) + "\n")

            # Log to MongoDB if enabled
            if self.log_to_mongo:
                try:
                    self.mongo_collection.insert_one(log_dict)
                except Exception as e:
                    logger.error(f"Failed to log usage to MongoDB: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to log usage: {str(e)}")

    def get_usage_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get usage statistics.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            user_id: User ID for filtering
            model_name: Model name for filtering

        Returns:
            Dict[str, Any]: Usage statistics
        """
        if self.log_to_mongo:
            try:
                # Build query
                query = {}
                if start_date:
                    query["created_at"] = {"$gte": start_date}
                if end_date:
                    query["created_at"] = {"$lte": end_date}
                if user_id:
                    query["user_id"] = user_id
                if model_name:
                    query["usage.model_name"] = model_name

                # Get stats from MongoDB
                pipeline = [
                    {"$match": query},
                    {
                        "$group": {
                            "_id": None,
                            "total_prompt_tokens": {"$sum": "$usage.prompt_tokens"},
                            "total_completion_tokens": {"$sum": "$usage.completion_tokens"},
                            "total_tokens": {"$sum": "$usage.total_tokens"},
                            "total_cost": {"$sum": "$usage.cost_usd"},
                            "request_count": {"$sum": 1},
                        }
                    }
                ]
                result = list(self.mongo_collection.aggregate(pipeline))
                return result[0] if result else {
                    "total_prompt_tokens": 0,
                    "total_completion_tokens": 0,
                    "total_tokens": 0,
                    "total_cost": 0,
                    "request_count": 0,
                }
            except Exception as e:
                logger.error(f"Failed to get usage stats from MongoDB: {str(e)}")
                return {
                    "total_prompt_tokens": 0,
                    "total_completion_tokens": 0,
                    "total_tokens": 0,
                    "total_cost": 0,
                    "request_count": 0,
                }
        else:
            # TODO: Implement file-based stats calculation
            raise NotImplementedError("File-based stats calculation not implemented yet")