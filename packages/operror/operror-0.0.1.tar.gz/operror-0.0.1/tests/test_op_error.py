import traceback

from operror.op_error import OpError, new_internal_error
from operror.op_status import Code, Status


class Connection:
    def exec_sql(self, sql: str):
        raise RuntimeError("Network error")

class DBClient:
    def __init__(self, conn: Connection):
        self._conn = conn

    def insert(self, data: str):
        try:
            self._conn.exec_sql("insert into ...")
        except RuntimeError as e:
            raise new_internal_error().with_message("DB insert failed").build(OpError) from e

class Service:
    def __init__(self, db: DBClient):
        self._db = db
        
    def save(self, data: str):
        self._db.insert(data)

class API:
    def __init__(self, service: Service):
        self._service = service
        
    def create(self, data: str):
        self._service.save(data)

def test_op_error_print_stack():
    api = API(Service(DBClient(Connection())))
    try:
        api.create("test")
    except OpError:
        # print(f"error info: {e}")
        print(traceback.format_exc())

def test_check_op_error_cause():
    try:
        api = API(Service(DBClient(Connection())))
        api.create("test")
    except OpError as e:
        assert e.__cause__ is not None
        assert isinstance(e.__cause__, RuntimeError)
        assert e.__cause__.args[0] == "Network error"
        assert e.__context__ is not None
        assert isinstance(e.__context__, RuntimeError)
        assert e.__context__.args[0] == "Network error"

def test_build_op_error():
    e = new_internal_error().with_message("internal error").build()
    assert isinstance(e, OpError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "internal error"  
    
    class MyOpError(OpError):
        pass

    e = new_internal_error().with_message("internal error").build(MyOpError)
    assert isinstance(e, MyOpError)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "internal error"
    
    class MyOpError2(OpError):
        def __init__(self, status: Status, p_arg: str, kw_arg: str = ""):
            super().__init__(status=status)
            self.p_arg = p_arg
            self.kw_arg = kw_arg

    e = new_internal_error().with_message("internal error").build(MyOpError2, "p_arg", kw_arg="kw_arg")
    assert isinstance(e, MyOpError2)
    assert e.status.code == Code.INTERNAL_ERROR
    assert e.status.message == "internal error"
    assert e.p_arg == "p_arg"
    assert e.kw_arg == "kw_arg"
