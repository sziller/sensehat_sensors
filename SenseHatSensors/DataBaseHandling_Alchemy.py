import inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Column, Float, Integer, String, JSON
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import close_all_sessions
import config as conf
from EngineProcesses import (HelperFunctions as HeFu,
                             HashFunctions as HaFu)

Base = declarative_base()


def createSession(db_path: str, style: str = "SQLite", base=Base):
    """=== Function name: createSession ================================================================================
    ============================================================================================== by Sziller ==="""
    if style == "SQLite":
        engine = create_engine('sqlite:///%s' % db_path, echo=False, poolclass=NullPool)
    elif style == "PostGreSQL":
        engine = create_engine(db_path, echo=False, poolclass=NullPool)
    else:
        raise Exception("no valid dialect defined")

    base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()

# CLASS definitions ENDED                                                                   -   START   -


class User(Base):
    """=== Classname: User(Base) =======================================================================================
    Class represents general user who's data is to be stored and processed by the DB
    ============================================================================================== by Sziller ==="""
    __tablename__ = "users"
    uuid = Column("uuid", String, primary_key=True)
    email_list = Column("email_list", String)
    usr_fn = Column("usr_fn", String)
    usr_ln = Column("usr_ln", String)
    authorization = Column("authorization", Integer)
    pubkey = Column("pubkey", String)
    stripe_id = Column("stripe_id", String)
    timestamp = Column("timestamp", Float)

    def __init__(self,
                 uuid: str,
                 email_list: str,
                 usr_fn: str,
                 usr_ln: str = "",
                 authorization: int = 0,
                 pubkey: str or None = None,
                 stripe_id: str = "",
                 timestamp: float or None = None,
                 ):
        self.uuid           = uuid
        self.email_list     = email_list
        self.usr_fn         = usr_fn
        self.usr_ln         = usr_ln
        self.authorization  = authorization
        self.pubkey         = pubkey
        self.stripe_id      = stripe_id
        self.timestamp      = HeFu.timestamp(formatted=False)

    def return_as_dict(self):
        """=== Method name: return_as_dict =============================================================================
        Returns instance as a dictionary
        @return : dict - parameter: argument pairs in a dict
        ========================================================================================== by Sziller ==="""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @ classmethod
    def construct(cls, d_in):
        """=== Classmethod: construct ==================================================================================
        Input necessary class parameters to instantiate object of the class!
        @param d_in: dict - format data to instantiate new object
        @return: an instance of the class
        ========================================================================================== by Sziller ==="""
        return cls(
            d_in["uuid"], d_in["email_list"], d_in["usr_fn"],
            d_in["usr_ln"], d_in["authorization"], d_in["pubkey"], d_in["stripe_id"])

    def __repr__(self):
        return "{:<33}:{:>4} {:<15} {:<15} - email: {:<35} - added: {}".format(self.uuid,
                                                                               self.authorization,
                                                                               self.usr_fn,
                                                                               self.usr_ln,
                                                                               self.email_list,
                                                                               self.timestamp)


class Measurement(Base):
    """=== Classname: Record(Base) =====================================================================================
    Class represents general record who's data is to be stored and processed by the DB
    ============================================================================================== by Sziller ==="""
    __tablename__   = "measurement"
    measurement_hash: str       = Column("measurement_hash", String, primary_key=True)
    measurement_type: str       = Column("measurement_type", String)
    measurement_locat: str      = Column("measurement_locat", String)
    measurement_value: float    = Column("measurement_value", Float)
    measurement_dim: str        = Column("measurement_dim", Float)
    timestamp: float            = Column("timestamp", Float)

    def __init__(self,
                 measurement_hash: str,
                 measurement_type: str,
                 measurement_locat: str,
                 measurement_value: float,
                 measurement_dim: str,
                 timestamp: float
                 ):

        self.measurement_hash: str       = measurement_hash
        self.measurement_type: str       = measurement_type
        self.measurement_locat: str      = measurement_locat
        self.measurement_value: float    = measurement_value
        self.measurement_dim: str        = measurement_dim
        self.timestamp: float            = timestamp

    def return_as_dict(self):
        """=== Method name: return_as_dict =============================================================================
        Returns instance as a dictionary
        @return : dict - parameter: argument pairs in a dict
        ========================================================================================== by Sziller ==="""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @ classmethod
    def construct(cls, d_in):
        """=== Classmethod: construct ==================================================================================
        Input necessary class parameters to instantiate object of the class!
        @param d_in: dict - format data to instantiate new object
        @return: an instance of the class
        ========================================================================================== by Sziller ==="""
        return cls(**d_in)

    def __repr__(self):
        return "{:<33}:{:>35} - added: {}".format(self.hash_hxstr,
                                                  self.email,
                                                  self.timestamp)


# CLASS definitions ENDED                                                                   -   ENDED   -
# CLASS assignment to tables START                                                          -   START   -
OBJ_KEY = {"measurement": Measurement}
# CLASS assignment to tables ENDED                                                          -   ENDED   -


def ADD_rows_to_table(primary_key: str,
                      data_list: list,
                      db_table: str,
                      db_path: str = "",
                      style: str = "",
                      session_in: object or None = None):
    """
    @param primary_key: 
    @param data_list: 
    @param db_path: 
    @param db_table: 
    @param style: 
    @param session_in: 
    @return: 
    """
    if session_in:
        session = session_in
    else:
        session = createSession(db_path=db_path, style=style)
    added_primary_keys = []
    global OBJ_KEY
    RowObj = OBJ_KEY[db_table]
    for data in data_list:
        # there are cases:
        # - a. when primary key exists before instance being added to DB
        # - b. primary key is generated from other incoming data on instantiation
        if primary_key in data:  # a.: works only if primary key is set and included in row to be created!
            if not session.query(RowObj).filter(getattr(RowObj, primary_key) == data[primary_key]).count():
                newrow = RowObj.construct(d_in=data)
                session.add(newrow)
                added_primary_keys.append(data[primary_key])
        else:
            # this is the general case. <data> doesn't need to include primary key:
            # we check if primary key having been generated on instantiation exists.
            newrow = RowObj.construct(d_in=data)
            if not session.query(RowObj).filter(getattr(RowObj, primary_key) == getattr(newrow, primary_key)).count():
                session.add(newrow)
    session.commit()
    if not session_in:
        session.close()
    return added_primary_keys


def db_delete_table(db_path, dellist: list, style: str):
    """

    @return:
    """
    cmn = inspect.currentframe().f_code.co_name  # current method name
    if style == "SQLite":
        engine = create_engine('sqlite:///%s' % db_path, echo=True)
    elif style == "PostGreSQL":
        engine = create_engine(db_path, echo=True)
    else:
        raise Exception("<style> not recognized. - sais {}".format(cmn))
    
    # try: drop_table("documents", engine)
    # except: print("table probably NOT DELETED - documents")
    # try: drop_table("users", engine)
    # except: print("table probably NOT DELETED - users")
    # try: drop_table("records", engine)
    # except: print("table probably NOT DELETED - records")
    # try: drop_table("merkletrees", engine)
    # except: print("table probably NOT DELETED - merkletrees")

    Base.metadata.create_all(bind=engine)
    if "users" in dellist:
        User.__table__.drop(engine)
    if "documents" in dellist:
        Document.__table__.drop(engine)
    if "merkletrees" in dellist:
        MerkleTree.__table__.drop(engine)
    if "records" in dellist:
        Record.__table__.drop(engine)
    if "scheduledtasks" in dellist:
        ScheduledTask.__table__.drop(engine)


def drop_table(table_name, engine):
    """
    @param table_name: 
    @param engine: 
    @return: 
    """
    Base = declarative_base()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    table = metadata.tables[table_name]
    if table is not None:
        Base.metadata.drop_all(engine, [table], checkfirst=True)


def db_delete_multiple_usrs_by_key(key: str, filtervalue_list: list, db_path: str, style: str):
    """=== Function name: db_delete_multiple_usrs_by_key ==============================================================
    @param key: str - name of row's attribute
    @param filtervalue_list: list - list of values's of rows to be deleted
    @return:
    ============================================================================================== by Sziller ==="""
    session = createSession(db_path=db_path, style=style)
    for filtervalue in filtervalue_list:
        session.query(User).filter(getattr(User, key) == filtervalue).delete(synchronize_session=False)
    session.commit()
    # if not session_in:
    session.close()


def db_delete_multiple_docs_by_key(key: str, filtervalue_list: list, db_path: str, style: str):
    """=== Function name: db_delete_multiple_docs_by_key ==============================================================
    @param key: str - name of row's attribute
    @param filtervalue_list: list - list of values of rows to be deleted
    @param db_path: str - the actual DataBase name the engine uses. Different for SQLite and PostGreSQL
    @param style: str - to distinguish path handling, enter DB style : PostGreSQL or SQLite
    @return:
    ============================================================================================== by Sziller ==="""
    session = createSession(db_path=db_path, style=style)
    for filtervalue in filtervalue_list:
        session.query(Document).filter(getattr(Document, key) == filtervalue).delete(synchronize_session=False)
    session.commit()
    session.close()
    # if not session_in:
    session.close()


def MODIFY_multiple_rows_by_column_to_value(
        filterkey: str,
        filtervalue_list: list,
        target_key: str,
        target_value,
        db_table: str,
        db_path: str    = "",
        style: str      = "",
        session_in: object or None = None):
    """=== Function name: db_REC_modify_multiple_rows_by_column_to_value ===============================================
    USE THIS IF THE NEW VALUES THE CELLS MUST TAKE ARE IDENTICAL!!!
    This function deals with the USERs DB Table!!!
    @param filterkey: str - name of column, in which filtervalues will be looked for
    @param filtervalue_list: list - list of values of rows to be deleted
    @param target_key: str - name of the column, whose value will be modified
    @param target_value: any data to be put into multiple cell
    @param db_path: str - the actual DataBase name the engine uses. Different for SQLite and PostGreSQL
    @param db_table: str - name of the table you want to write
    @param style: str - to distinguish path handling, enter DB style : PostGreSQL or SQLite
    @param session_in: obj - a precreated session. If used, it will not be closed. If not entered, a new session is
                                                    created, which is closed at the end.
    @return:
    ============================================================================================== by Sziller ==="""
    if session_in:
        session = session_in
    else:
        session = createSession(db_path=db_path, style=style)
    global OBJ_KEY
    RowObj = OBJ_KEY[db_table]
    for filtervalue in filtervalue_list:
        session.query(RowObj).filter(getattr(RowObj, filterkey) == filtervalue).update({target_key: target_value})
    session.commit()
    if not session_in:
        session.close()


def MODIFY_multiple_rows_by_column_by_dict(filterkey: str,
                                           mod_dict: dict,
                                           db_table,
                                           db_path: str = "",
                                           style: str = "",
                                           session_in: object or None = None):
    """
    
    @param filterkey: 
    @param mod_dict: 
    @param db_path: 
    @param db_table: 
    @param style: 
    @param session_in:
    @return: 
    """
    if session_in:
        session = session_in
    else:
        session = createSession(db_path=db_path, style=style)
    global OBJ_KEY
    RowObj = OBJ_KEY[db_table]
    for filtervalue, sub_dict in mod_dict.items():
        session.query(RowObj).filter(getattr(RowObj, filterkey) == filtervalue).update(sub_dict)
    session.commit()
    if not session_in:
        session.close()


def QUERY_entire_table(ordered_by: str,
                       db_table: str,
                       db_path: str = "",
                       style: str = "",
                       session_in: object or None = None) -> list:
    """=== Function name: QUERY_entire_table =========================================================================
    Function returns an entire DB table, defined by args.
    This function deals with the entered DB Table!!!
    @param ordered_by:
    @param db_path:
    @param db_table:
    @param style:
    @param session_in:
    @return: list of rows in table requested.
    ========================================================================================== by Sziller ==="""
    if session_in:
        session = session_in
    else:
        session = createSession(db_path=db_path, style=style)
    global OBJ_KEY
    RowObj = OBJ_KEY[db_table]
    results = session.query(RowObj).order_by(ordered_by).all()
    result_list = [_.return_as_dict() for _ in results]
    session.commit()
    if not session_in:
        session.close()
    return result_list


def QUERY_rows_by_column_filtervalue_list_ordered(filterkey: str,
                                                  filtervalue_list: list,
                                                  ordered_by: str,
                                                  db_table: str,
                                                  db_path: str = "",
                                                  style: str = "",
                                                  session_in: object or None = None) -> list:

    """=== Function name: QUERY_rows_by_column_filtervalue_list_ordered =============================================
    This function deals with the entered DB Table!!!
    @param filterkey:
    @param filtervalue_list:
    @param ordered_by:
    @param db_path:
    @param db_table:
    @param style:
    @param session_in:
    @return:
    ============================================================================================== by Sziller ==="""
    if session_in:
        session = session_in
    else:
        session = createSession(db_path=db_path, style=style)
    global OBJ_KEY
    RowObj = OBJ_KEY[db_table]
    '''
    rec_results = []
    for filtervalue in filtervalue_list:
        rec_subresults = session.query(RowObj).filter(getattr(RowObj, filterkey) == filtervalue).order_by(ordered_by).all()
        rec_results += rec_subresults
        '''
    # rec_results = session.query(RowObj).filter(getattr(RowObj, filterkey) in filtervalue_list).order_by(ordered_by).all()
    # rec_results = session.query(RowObj).filter(RowObj.hash_hxstr.in_(tuple(filtervalue_list)))

    results = session.query(RowObj).filter(getattr(RowObj, filterkey).in_(tuple(filtervalue_list))).order_by(ordered_by)
    result_list = [_.return_as_dict() for _ in results]
    session.commit()
    if not session_in:
        session.close()
    return result_list


if __name__ == "__main__":
    pass
