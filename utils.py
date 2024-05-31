
import os
import sys
from dotenv import load_dotenv

# Ensure the src directory is in the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.')))

load_dotenv()

from src.models.user_model import User
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker



def main():
    print(User.__name__)
    engine = create_engine("postgresql+psycopg2://vanya:1234@localhost:5433/test_fast_db")
    Session = sessionmaker(bind=engine)
    with Session() as ses:  
            stmt = (
                select(User)
                .where(User.name=="gunicorn1")
            )
            ans = ses.scalar(stmt)
            print(ans.__dict__)
            ses.commit()
            
    

if __name__ == "__main__":
    main()


