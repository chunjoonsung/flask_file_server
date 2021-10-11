from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker, joinedload

#engine = create_engine('sqlite:///:memory:', echo=True)
engine = create_engine('sqlite:///user.db', echo=True)
Base   = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(80))
    password = Column(String(80))
    admin    = Column(Integer)
    def __init__(self, username, password, admin):
        self.username = username
        self.password = password
        self.admin    = admin
    def __repr__(self):
        return "<User('%s', '%s', '%d')>" % (self.username, self.password, self.admin)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)     
    #Session = sessionmaker()
    Session.configure(bind=engine)   
    session = Session()
    session.add( User('user', 'user1234', 0) )
    session.add( User('admin', 'nimda4321', 0) )
    session.commit()
    
    print( session.query(User).filter(User.username=='admin').first() )
    print( session.query(User).filter_by(username='user').first() )
    '''
    session.add_all([
         User('user', 'user1234', 0),
         User('admin', 'nimda4321', 0)] )
    session.commit()
    '''
    '''
    our_user = session.query(User).filter_by(name='haruair').first()
    '''