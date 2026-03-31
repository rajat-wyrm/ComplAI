import logging
import sys
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'logs/compliance_copilot_{datetime.now().strftime("%Y%m%d")}.log')
        ]
    )
    
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('motor').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

logger = setup_logging()
