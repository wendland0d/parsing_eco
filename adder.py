from sme_parsers.models import Parser, engine
from sqlalchemy.orm import Session

with Session(bind=engine) as db:
    buf = Parser(
        name = 'buff',
        is_market = True
    )
    db.add(buf)
    db.commit()