# Try mysqlclient first; fall back to PyMySQL if not installed.
try:
    import MySQLdb  # mysqlclient — preferred
except ImportError:
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass  # Neither installed — Django will raise a clear error on db access
