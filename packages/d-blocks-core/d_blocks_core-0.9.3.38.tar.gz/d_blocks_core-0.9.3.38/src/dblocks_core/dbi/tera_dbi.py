from contextlib import contextmanager

import sqlalchemy as sa

try:
    import teradatasql
except ImportError:
    pass
import re

from sqlalchemy import exc as sa_exc

from dblocks_core import exc
from dblocks_core.config.config import logger, plugin_instances
from dblocks_core.dbi import contract
from dblocks_core.model import config_model, meta_model, plugin_model

# custom log level for DB interaction
# TRACE: 5
# DEBUG: 10
# INFO: 20
# SUCCESS: 25
# WARNING: 30
# ERROR: 40
# CRITICAL: 501
# we use 15 so that we do not send all to stdout (meta_model.DATABASE_LOG_LEVEL)
LOG_LEVEL_NAME = "TERADATA"
LOG_LEVEL = logger.level(
    LOG_LEVEL_NAME,
    no=meta_model.DATABASE_LOG_LEVEL,
    color="<blue>",
    icon="🛢️",
)

_LOG_SEPARATOR = "\n" + "-" * 80 + "\n"

# this is used to decide if object details are in dbc.tablesV
_CAN_HAVE_COMMENT = [meta_model.TABLE, meta_model.VIEW, meta_model.PROCEDURE]
_CAN_HAVE_COLUMNS = [meta_model.TABLE, meta_model.VIEW]

# error codes we know and handle
ERR_CODE_USER_PASSWORD_INVALID = "8017"
ERR_CODE_NO_STATS_DEFINED = "3624"
ERR_CODE_DOES_NOT_EXIST = "3807"
ERR_CODE_DB_DOES_NOT_EXIST = "3802"
ERR_CODE_SYNTAX_ERROR = "3706"
ERR_CODE_NO_ACCESS = "3523"
ERR_CODE_REF_INTEGRITY_VIOLATION = "5313"
ERR_CODE_COLUMN_NOT_FOUND = "5628"

STATEMENT_ERRORS = (
    ERR_CODE_COLUMN_NOT_FOUND,
    ERR_CODE_REF_INTEGRITY_VIOLATION,
    ERR_CODE_SYNTAX_ERROR,
)

# prefixes of error descriptions we know and handle
ERR_DSC_HOSTNAME_LOOKUP_FAILED = "Hostname lookup failed"
ERR_DSC_FAILED_TO_CONNECT = "Failed to connect to"

_DBKIND_TO_TYPE = {
    "D": meta_model.DATABASE,
    "U": meta_model.USER,
}

_TABLEKIND_TO_TYPE = {
    "O": meta_model.TABLE,
    "T": meta_model.TABLE,  # table
    "Q": meta_model.TABLE,  # queue
    "V": meta_model.VIEW,
    "P": meta_model.PROCEDURE,
    "E": meta_model.PROCEDURE,
    "I": meta_model.JOIN_INDEX,
    "N": meta_model.INDEX,  # todo hash index, really?
    "M": meta_model.MACRO,
    "G": meta_model.TRIGGER,
    "F": meta_model.FUNCTION,  # show function can cause err 5593 which we have to "survive"
    "R": meta_model.FUNCTION,  # TODO: there various function types - see function mapping
    "A": meta_model.FUNCTION,  # can cause 3523: The user does not have any access to ...
    "2": meta_model.FUNCTION_MAPPING,
    "U": meta_model.TYPE,  # can cause 6878: Show Type operation is not allowed on Internal type UDT
    "X": meta_model.AUTHORIZATION,
}


@contextmanager
def ignore_errors(err_list: str | list[str | int]):
    """
    A context manager to suppress specific SQL errors based on error codes.

    Args:
        err_list (str | list[str | int]): A single error code or a list of error
            codes to ignore. Error codes are converted to strings for comparison.

    Yields:
        None: Executes the block within the context, suppressing specified errors.

    Behavior:
    - Converts the provided error codes to strings for uniform comparison.
    - Catches `sa_exc.StatementError` exceptions caused by `teradatasql.Error`.
    - Extracts the error code from the exception and suppresses the error if its
      code is in the specified list.
    - Reraises the exception if the error code is not in the ignore list or the
      cause is not a `teradatasql.Error`.
    """

    if isinstance(err_list, str):
        err_list = [err_list]
    err_list = [str(err) for err in err_list]
    try:
        yield
    except sa_exc.StatementError as err:
        cause = err.orig
        if not isinstance(cause, teradatasql.Error):  # type: ignore
            raise
        # teradata does not provide additional details about the error
        # we have to get error number from first line of the error string
        err_code = get_error_code_from_exception(cause)
        if err_code in err_list:
            err_desc = get_description_from_exception(cause)
            logger.debug(f"ignoring error: {err_code}: {err_desc}")
            return
        raise


@contextmanager
def tera_catch():
    """
    A context manager to catch and log Teradata SQL exceptions.

    Yields:
        None: Executes the block within the context, logging exceptions if they occur.

    Behavior:
    - Catches `sa_exc.StatementError` and `sa_exc.OperationalError` exceptions.
    - Logs the error code, description, and statement that caused the exception.
    """
    try:
        yield
    except (sa_exc.StatementError, sa_exc.OperationalError) as err:
        cause = err.orig
        err_code = get_error_code_from_exception(cause)
        err_desc = get_description_from_exception(cause)
        statement = err.statement
        logger.error(
            f"ERROR: {err_code}: {err_desc}\nstatement = {statement[:100]} ..."
        )
        raise


@contextmanager
def translate_error():
    """
    A context manager to translate specific Teradata SQL errors into custom
    exceptions.

    Yields:
        None: Executes the block within the context, translating specified errors
        if they occur.

    Behavior:
    - Catches `sa_exc.StatementError` exceptions caused by `teradatasql.Error`.
    - Extracts the error code and description from the exception.
    - Translates specific errors into custom exceptions:
      - Error code "8017" or descriptions like "Hostname lookup failed" are
        translated into `exc.DBCannotConnect`.
    - Reraises the original exception if it cannot be translated or if the cause
      is not a `teradatasql.Error`.
    """

    try:
        yield
    except (sa_exc.StatementError, sa_exc.OperationalError) as err:
        cause = err.orig
        err_code = get_error_code_from_exception(cause)
        err_desc = get_description_from_exception(cause)
        statement = err.statement

        # not a TD error, can not translate
        if not isinstance(cause, teradatasql.Error):  # type: ignore
            raise

        if err_code == ERR_CODE_DOES_NOT_EXIST:
            logger.info("Code does not exist")
            logger.debug(cause)
            raise exc.DBObjectDoesNotExist(err_desc) from err

        # no access to ...
        if err_code == ERR_CODE_NO_ACCESS:
            raise exc.DBAccessRightsError(err_desc) from err

        # exc.DBCannotConnect - different causes we have seen ...
        if err_code == ERR_CODE_USER_PASSWORD_INVALID:
            logger.debug(cause)
            raise exc.DBCannotConnect(err_desc) from err

        if err_code == ERR_CODE_NO_STATS_DEFINED:
            logger.debug(cause)
            raise exc.DBNoStatsDefined(err_desc) from err

        if err_code == ERR_CODE_DB_DOES_NOT_EXIST:
            logger.debug(cause)
            raise exc.DBDoesNotExist(err_desc) from err

        # OperationalError with no error code -> exc.DBCannotConnect
        for dsc in (
            ERR_DSC_HOSTNAME_LOOKUP_FAILED,
            ERR_DSC_FAILED_TO_CONNECT,
        ):
            if err_desc.startswith(dsc):
                logger.debug(cause)
                raise exc.DBCannotConnect(err_desc) from err

        # can not translate, dump full stack of the error
        # TODO: should this always default to a DBStatementError?
        logger.debug(cause)
        raise exc.DBStatementError(message=err_desc, statement=statement) from err


def get_description_from_exception(
    err: teradatasql.Error | BaseException | None,  # type: ignore
) -> str:
    """
    Extracts the error description from a Teradata SQL exception.

    Args:
        err (teradatasql.Error): The Teradata SQL error to extract the description
            from.

    Returns:
        str: The error description, derived from the first line of the error
            message.

    Behavior:
    - Converts the exception to a string and splits it into lines.
    - Extracts the portion of the first line following the last closing square
      bracket (`]`) and strips any whitespace.
    """
    if not isinstance(err, teradatasql.Error):  # type: ignore
        return ""
    lines = str(err).splitlines()
    first_line = lines[0]
    caused_by = ""
    for line in lines:
        if line.startswith("Caused by"):
            caused_by = " (" + line.strip() + ")"
    description = first_line.split("]")[-1].strip() + caused_by
    return description


def get_error_code_from_exception(
    err: teradatasql.Error | BaseException | None,  # type: ignore
) -> str:  # type: ignore
    """
    Extracts the error code from a Teradata SQL exception.

    Args:
        err (teradatasql.Error): The Teradata SQL error to extract the code from.

    Returns:
        str: The error code as a string, or an empty string if no code is found.

    Behavior:
    - Converts the exception to a string and examines the first line.
    - Searches for an error code in the format `[Error <code>]` using a regular
      expression.
    - Returns the extracted code as a string if found, or an empty string
      otherwise.
    """
    if not isinstance(err, teradatasql.Error):  # type: ignore
        return ""

    # [Version 20.0.0.20] [Session 1679726] [Teradata Database]
    # [Error 3624] There are no statistics defined for the table.
    first_line = str(err).splitlines()[0]
    if m := re.search(r"\[Error (\d+)\]", first_line):
        return str(m.group(1))
    return ""


class TeraDBI(contract.AbstractDBI):
    def __init__(
        self,
        engine: sa.Engine,
        cfg: config_model.Config,
    ):
        self.engine = engine
        self.cfg = cfg

        # import plugins
        self.rewrite_plugins: list[plugin_model._PluginInstance] = plugin_instances(
            cfg,
            plugin_model.PluginDBIRewriteStatement,
        )

    @translate_error()
    def deploy_statements(self, statements: list[str]):
        """
        Deploys a list of SQL statements to the Teradata database.

        Args:
            statements (list[str]): A list of SQL statements to execute.

        Behavior:
        - Connects to the database engine.
        - Executes each SQL statement directly using `exec_driver_sql`.
        - Logs the SQL statement at the custom log level.
        """
        with self.engine.connect() as con:
            for sql in statements:
                # stmt = sa.text(sql)
                # logger.debug(stmt)
                # con.execute(stmt)

                # skip sqlalchemy compilation step, send the query directly
                # thus, sqlalchemy wont't try to compile named parameters
                # (therefore compilation of stored procedures should work)
                for plugin_instance in self.rewrite_plugins:
                    new_sql = plugin_instance.instance.rewrite_statement(sql)
                    if new_sql != sql:
                        logger.log(
                            LOG_LEVEL_NAME,
                            f"-- statement was changed by a plugin: {plugin_instance.class_name}",
                        )
                        sql = new_sql
                logger.log(LOG_LEVEL_NAME, _LOG_SEPARATOR + sql + _LOG_SEPARATOR)
                con.exec_driver_sql(sql)
                # FIXME: log size of the result set

    @translate_error()
    def get_described_object(
        self,
        object: meta_model.IdentifiedObject,
    ) -> meta_model.DescribedObject | None:
        """
        Retrieves a detailed description of a database object by gathering its DDL,
        comment, and additional details.

        Args:
            object (meta_model.IdentifiedObject): The database object to describe,
                including its name, type, and database.

        Returns:
            meta_model.DescribedObject: A comprehensive description of the database
                object, including its DDL, comment, and additional details.

        Behavior:
        - Fetches the DDL for the object using `get_object_ddl`.
        - Retrieves the object's comment using `get_object_comment`.
        - Collects additional details, such as statistics and column information,
        using `get_object_details`.
        - Combines the gathered information into a `meta_model.DescribedObject` and
        returns it.
        """

        # show table/view/proc ...
        try:
            ddl = self.get_object_ddl(
                database_name=object.database_name,
                object_name=object.object_name,
                object_type=object.object_type,
            )
            # comment of the object itself
            comment = self.get_object_comment(
                database_name=object.database_name,
                object_identification=object.object_name,
                object_type=object.object_type,
            )

            # show stats + dbc.columnsV (comments)
            details = self.get_object_details(
                database_name=object.database_name,
                object_identification=object.object_name,
                object_type=object.object_type,
            )

            # join it all together
            described_object = meta_model.DescribedObject(
                identified_object=object,
                object_comment_ddl=comment,
                basic_definition=ddl,
                additional_details=details,
            )
        except exc.DBAccessRightsError as err:
            logger.error(err.message)
            return None

        except exc.DBObjectDoesNotExist as err:
            logger.debug(err)
            return None
        return described_object

    @translate_error()
    def delete_database(self, database_name: str):
        """
        Deletes a database from the Teradata system.

        Args:
            database_name (str): The name of the database to delete.

        Behavior:
        - Constructs a SQL statement to delete the database.
        - Executes the SQL statement using the database engine.
        - Logs the SQL statement at the custom log level.
        """
        sql = f"""delete database "{database_name}";"""
        stmt = sa.text(sql)
        with self.engine.connect() as con:
            logger.log(LOG_LEVEL_NAME, stmt)
            con.execute(stmt)

    @translate_error()
    def rename_identified_object(
        self,
        obj: meta_model.IdentifiedObject,
        new_name: str,
        *,
        ignore_errors: bool = False,
    ):
        """
        Renames a database object.

        Args:
            obj (meta_model.IdentifiedObject): The object to rename.
            new_name (str): The new name for the object.
            ignore_errors (bool, optional): Whether to ignore errors during renaming.
                Defaults to False.

        Behavior:
        - Constructs a SQL statement to rename the object.
        - Executes the SQL statement using the database engine.
        - Logs the SQL statement at the custom log level.
        - If `ignore_errors` is True, logs a warning instead of raising an exception
          on error.
        """
        object_type = obj.object_type
        sql = (
            f"""RENAME {object_type} "{obj.database_name}"."{obj.object_name}" """
            f"""TO "{obj.database_name}"."{new_name}";"""
        )
        try:
            with translate_error():
                with self.engine.connect() as con:
                    logger.log(LOG_LEVEL_NAME, sql)
                    con.exec_driver_sql(sql)
        except exc.DBStatementError as err:
            if not ignore_errors:
                raise
            logger.warning(str(err))

    @translate_error()
    def drop_identified_object(
        self,
        obj: meta_model.IdentifiedObject,
        *,
        ignore_errors: bool = True,
    ):
        """
        Drops a database object.

        Args:
            obj (meta_model.IdentifiedObject): The object to drop.
            ignore_errors (bool, optional): Whether to ignore errors during dropping.
                Defaults to True.

        Behavior:
        - Constructs a SQL statement to drop the object.
        - Executes the SQL statement using the database engine.
        - Logs the SQL statement at the custom log level.
        - If `ignore_errors` is True, logs a warning instead of raising an exception
          on error.
        """
        object_type = obj.object_type
        sql = f"""DROP {object_type} "{obj.database_name}"."{obj.object_name}";"""
        stmt = sa.text(sql)
        try:
            with translate_error():
                with self.engine.connect() as con:
                    logger.log(LOG_LEVEL_NAME, stmt)
                    con.execute(stmt)
        except exc.DBStatementError as err:
            if not ignore_errors:
                raise
            logger.warning(str(err))

    @translate_error()
    def get_identified_object(
        self,
        database_name: str,
        object_name: str,
        object_type: str,
    ) -> meta_model.IdentifiedObject | None:
        """
        Retrieves an identified database object.

        Args:
            database_name (str): The name of the database containing the object.
            object_name (str): The name of the object to retrieve.
            object_type (str): Object type - it drives metadata location we gather information

        Returns:
            meta_model.IdentifiedObject | None: The identified object, or None if not
                found.

        Behavior:
        - Constructs a SQL query to retrieve the object details from `dbc.tablesV`.
        - Executes the query using the database engine.
        - Maps the query result to a `meta_model.IdentifiedObject`.
        - Returns the identified object, or None if not found.
        """

        # Exceptional objects that are not available in DBC.TablesV
        if object_type == meta_model.DATABASE:
            return self.get_identified_object_for_db(object_name)
        if object_type == meta_model.ROLE:
            return self.get_identified_object_for_role(object_name)
        if object_type == meta_model.PROFILE:
            return self.get_identified_object_for_profile(object_name)

        sql = """
        select
            databaseName as database_name,
            tableName as object_name,
            tableKind as object_type,
            createTimeStamp as create_datetime,
            lastAlterTimeStamp as last_alter_datetime,
            creatorName as creator_name,
            lastAlterName as last_alter_name

        from dbc.tablesV
        where databaseName = :database_name
            and tableName = :object_name
        order by 1,2
        """
        stmt = sa.text(sql).bindparams(
            database_name=database_name, object_name=object_name
        )
        with self.engine.connect() as con:
            rows = [
                meta_model.IdentifiedObject(
                    database_name=row.database_name.strip(),
                    object_name=row.object_name.strip(),
                    object_type=_TABLEKIND_TO_TYPE[row.object_type.strip()],
                    platform_object_type=row.object_type.strip(),
                    create_datetime=row.create_datetime,
                    last_alter_datetime=row.last_alter_datetime,
                    creator_name=row.creator_name.strip() if row.creator_name else None,
                    last_alter_name=(
                        row.last_alter_name.strip() if row.last_alter_name else None
                    ),
                )
                for row in con.execute(stmt).fetchall()
            ]
            if len(rows) == 0:
                return None
            return rows[0]

    @translate_error()
    def get_identified_object_for_role(
        self,
        role_name: str,
    ) -> meta_model.IdentifiedObject | None:
        """
        Retrieves an identified object representing role.

        Args:
            role_name (str): The name of the role.

        Returns:
            meta_model.IdentifiedObject | None: The identified object, or None if not
                found.

        Behavior:
        - Constructs a SQL query to retrieve the object details from `dbc.databases`.
        - Executes the query using the database engine.
        - Maps the query result to a `meta_model.IdentifiedObject`.
        - Returns the identified object, or None if not found.
        """
        sql = """
        select
            roleName as role_name,
            createTimeStamp as create_datetime,
            createUID as creator_name

        from dbc.roles
        where roleName = :role_name
        order by 1
        """
        stmt = sa.text(sql).bindparams(role_name=role_name)
        with self.engine.connect() as con:
            rows = [
                meta_model.IdentifiedObject(
                    database_name="",
                    object_name=role_name.strip(),
                    object_type=meta_model.ROLE,
                    platform_object_type="",
                    create_datetime=row.create_datetime,
                    last_alter_datetime=row.create_datetime,
                    creator_name=row.creator_name.strip() if row.creator_name else None,
                    last_alter_name=(
                        row.creator_name.strip() if row.creator_name else None
                    ),
                )
                for row in con.execute(stmt).fetchall()
            ]
            if len(rows) == 0:
                return None
            return rows[0]

    @translate_error()
    def get_identified_object_for_profile(
        self,
        profile_name: str,
    ) -> meta_model.IdentifiedObject | None:
        """
        Retrieves an identified object representing profile.

        Args:
            profile_name (str): The name of the profile.

        Returns:
            meta_model.IdentifiedObject | None: The identified object, or None if not
                found.

        Behavior:
        - Constructs a SQL query to retrieve the object details from `dbc.databases`.
        - Executes the query using the database engine.
        - Maps the query result to a `meta_model.IdentifiedObject`.
        - Returns the identified object, or None if not found.
        """
        sql = """
        select
            profileName as profile_name,
            createTimeStamp as create_datetime,
            lastAlterTimeStamp as last_alter_datetime,
            createUID as creator_name,
            lastAlterUID as last_alter_name
        from dbc.profiles
        where profileName = :profile_name
        order by 1
        """
        stmt = sa.text(sql).bindparams(profile_name=profile_name)
        with self.engine.connect() as con:
            rows = [
                meta_model.IdentifiedObject(
                    database_name="",
                    object_name=profile_name.strip(),
                    object_type=meta_model.PROFILE,
                    platform_object_type="",
                    create_datetime=row.create_datetime,
                    last_alter_datetime=row.last_alter_datetime,
                    creator_name=row.creator_name.strip() if row.creator_name else None,
                    last_alter_name=(
                        row.last_alter_name.strip() if row.last_alter_name else None
                    ),
                )
                for row in con.execute(stmt).fetchall()
            ]
            if len(rows) == 0:
                return None
            return rows[0]

    @translate_error()
    def get_identified_object_for_db(
        self,
        database_name: str,
    ) -> meta_model.IdentifiedObject | None:
        """
        Retrieves an identified object representing database.

        Args:
            database_name (str): The name of the database containing the object.

        Returns:
            meta_model.IdentifiedObject | None: The identified object, or None if not
                found.

        Behavior:
        - Constructs a SQL query to retrieve the object details from `dbc.databases`.
        - Executes the query using the database engine.
        - Maps the query result to a `meta_model.IdentifiedObject`.
        - Returns the identified object, or None if not found.
        """
        sql = """
        select
            databaseName as database_name,
            dbkind as db_type,
            createTimeStamp as create_datetime,
            lastAlterTimeStamp as last_alter_datetime,
            creatorName as creator_name,
            lastAlterName as last_alter_name

        from dbc.databasesV
        where databaseName = :database_name
        order by 1,2
        """
        stmt = sa.text(sql).bindparams(database_name=database_name)
        with self.engine.connect() as con:
            rows = [
                meta_model.IdentifiedObject(
                    database_name=row.database_name.strip(),
                    object_name=row.database_name.strip(),
                    object_type=_DBKIND_TO_TYPE[row.db_type.strip()],
                    platform_object_type=row.db_type.strip(),
                    create_datetime=row.create_datetime,
                    last_alter_datetime=row.last_alter_datetime,
                    creator_name=row.creator_name.strip() if row.creator_name else None,
                    last_alter_name=(
                        row.last_alter_name.strip() if row.last_alter_name else None
                    ),
                )
                for row in con.execute(stmt).fetchall()
            ]
            if len(rows) == 0:
                return None
            return rows[0]

    @translate_error()
    def get_object_list(
        self,
        database_name: str,
        *,
        limit_to_type: str | None = None,
    ) -> list[meta_model.IdentifiedObject]:
        """
        Retrieves a list of database objects.

        Args:
            database_name (str): The name of the database containing the objects.
            limit_to_type (str, optional): The type of objects to limit the query to.
                Defaults to None.

        Returns:
            list[meta_model.IdentifiedObject]: A list of identified objects.

        Behavior:
        - Constructs a SQL query to retrieve the object details from `dbc.tablesV`.
        - Limits the query to specific object types if `limit_to_type` is provided.
        - Executes the query using the database engine.
        - Maps the query result to a list of `meta_model.IdentifiedObject`.
        """
        # get the scope
        if limit_to_type is None:
            scope = ", ".join([f"'{kind}'" for kind in _TABLEKIND_TO_TYPE.keys()])
            logger.trace(scope)
        else:
            scope = ", ".join(
                [
                    f"'{kind}'"
                    for kind, tp in _TABLEKIND_TO_TYPE.items()
                    if tp == meta_model.TABLE
                ]
            )
            logger.trace(scope)
        sql = f"""
        select
            databaseName as database_name,
            tableName as object_name,
            tableKind as object_type,
            createTimeStamp as create_datetime,
            lastAlterTimeStamp as last_alter_datetime,
            creatorName as creator_name,
            lastAlterName as last_alter_name
        from dbc.tablesV
        where databaseName = :database_name
        and tableKind in ({scope})
        order by 1,2
        """
        stmt = sa.text(sql).bindparams(database_name=database_name)
        logger.debug(stmt)
        with self.engine.connect() as con:
            rows = [
                meta_model.IdentifiedObject(
                    database_name=row.database_name.strip(),
                    object_name=row.object_name.strip(),
                    object_type=_TABLEKIND_TO_TYPE[row.object_type.strip()],
                    platform_object_type=row.object_type.strip(),
                    create_datetime=row.create_datetime,
                    last_alter_datetime=row.last_alter_datetime,
                    creator_name=(
                        row.creator_name.strip()
                        if row.creator_name is not None
                        else None
                    ),
                    last_alter_name=(
                        row.last_alter_name.strip()
                        if row.last_alter_name is not None
                        else None
                    ),
                )
                for row in con.execute(stmt).fetchall()
            ]
        return rows

    @translate_error()
    def get_object_ddl(
        self,
        database_name: str,
        object_name: str,
        object_type: str,
    ) -> str:
        """
        Retrieves the DDL statement for a database object.

        Args:
            database_name (str): The name of the database containing the object.
            object_name (str): The name of the object to retrieve the DDL for.
            object_type (str): The type of the object (e.g., "table").

        Returns:
            str: The DDL statement for the object.

        Behavior:
        - Constructs a SQL query to retrieve the DDL statement using `SHOW`.
        - Executes the query using the database engine.
        - Returns the DDL statement.
        """
        with self.engine.connect() as con:
            return self._get_object_ddl(con, database_name, object_name, object_type)

    def _get_object_ddl(
        self,
        con: sa.Connection,
        database_name: str,
        object_name: str,
        object_type: str = "table",
    ) -> str:
        """
        Retrieves the DDL statement for a database object.

        Args:
            con (sa.Connection): The database connection.
            database_name (str): The name of the database containing the object.
            object_name (str): The name of the object to retrieve the DDL for.
            object_type (str, optional): The type of the object (e.g., "table").
                Defaults to "table".

        Returns:
            str: The DDL statement for the object.

        Behavior:
        - Constructs a SQL query to retrieve the DDL statement using `SHOW`.
        - Executes the query using the database connection.
        - Returns the DDL statement.
        """
        sql = f"""show {object_type} "{database_name}"."{object_name}";"""
        logger.debug(sql)
        stmt = sa.text(sql)
        rows = [r[0].replace("\r", "\n") for r in con.execute(stmt).fetchall()]
        stmt = "".join(rows)

        stmt = stmt.strip().removesuffix(";") + ";\n"
        return stmt

    @translate_error()
    def get_object_comment(
        self,
        database_name: str,
        object_identification: str,
        *,
        object_type: str,
    ) -> str | None:
        """
        Retrieves the comment for a database object.

        Args:
            database_name (str): The name of the database containing the object.
            object_identification (str): The name of the object to retrieve the
                comment for.
            object_type (str): The type of the object (e.g., "table").

        Returns:
            str | None: The comment for the object, or None if no comment is found.

        Behavior:
        - Constructs a SQL query to retrieve the comment from `dbc.tablesV`.
        - Executes the query using the database engine.
        - Returns the comment, or None if no comment is found.
        """
        # TODO: předělat tak, aby výjimka byla pro sloupec. rozdvojka tablesV a columnsV.
        if object_type in _CAN_HAVE_COMMENT:
            return self._get_coment_from_tables_v(
                database_name,
                table_name=object_identification,
                object_type=object_type,
            )
        logger.debug(f"no comment for {database_name}.{object_identification}")
        return None

    @translate_error()
    def get_object_details(
        self,
        database_name: str,
        object_identification: str,
        *,
        object_type: str,
    ) -> meta_model.ObjectDetails:
        """
        Retrieves additional details for a database object.

        Args:
            database_name (str): The name of the database containing the object.
            object_identification (str): The name of the object to retrieve details
                for.
            object_type (str): The type of the object (e.g., "table").

        Returns:
            meta_model.ObjectDetails: A list of additional details for the object.

        Behavior:
        - Retrieves column comments using `_column_comments`.
        - Retrieves statistics using `_show_stats`.
        - Combines the retrieved details into a `meta_model.ObjectDetails` list.
        """
        return [
            *(
                self._column_comments(
                    database_name,
                    object_identification,
                    object_type=object_type,
                )
            ),
            *(
                self._show_stats(
                    database_name,
                    object_identification,
                    object_type=object_type,
                )
            ),
        ]

    def _column_comments(
        self,
        database_name: str,
        object_identification: str,
        *,
        object_type: str,
    ) -> meta_model.ObjectDetails:
        """
        Retrieves column comments for a database object.

        Args:
            database_name (str): The name of the database containing the object.
            object_identification (str): The name of the object to retrieve column
                comments for.
            object_type (str): The type of the object (e.g., "table").

        Returns:
            meta_model.ObjectDetails: A list of column comments for the object.

        Behavior:
        - Constructs a SQL query to retrieve column comments from `dbc.columnsV`.
        - Executes the query using the database engine.
        - Maps the query result to a list of `meta_model.ColumnDescription`.
        """
        if object_type not in _CAN_HAVE_COLUMNS:
            return []
        sql = """
            select columnName, commentString
            from dbc.columnsV
            where
                 commentString is not null
                 and databaseName = :database_name
                 and tableName = :table_name
            order by columnId asc"""
        stmt = sa.text(sql).bindparams(
            database_name=database_name,
            table_name=object_identification,
        )
        logger.debug(sql)
        logger.debug(f"params: {database_name=}, table_name={object_identification}")

        def _quote(comment: str) -> str:
            return comment.replace("'", "''")

        with self.engine.connect() as con:
            comments = [  # pyright: ignore[reportGeneralTypeIssues]
                meta_model.ColumnDescription(
                    column_name=row[0].strip(),
                    column_comment=row[1],
                    ddl_statement=(
                        f"COMMENT ON COLUMN {database_name}."
                        f"{object_identification}.{row[0].strip()} "
                        f"IS '{_quote(row[1])}';"
                    ),
                )
                for row in con.execute(stmt).fetchall()
            ]
            logger.debug(f"{len(comments)=}")
            return comments

    def _show_stats(
        self,
        database_name: str,
        object_identification: str,
        *,
        object_type: str,
    ) -> meta_model.ObjectDetails:
        """
        Retrieves statistics for a database object.

        Args:
            database_name (str): The name of the database containing the object.
            object_identification (str): The name of the object to retrieve statistics
                for.
            object_type (str): The type of the object (e.g., "table").

        Returns:
            meta_model.ObjectDetails: A list of statistics for the object.

        Behavior:
        - Constructs a SQL query to retrieve statistics using `SHOW STATS`.
        - Executes the query using the database engine.
        - Maps the query result to a list of `meta_model.TableStatistic`.
        - Handles specific exceptions silently or logs them without crashing.
        """
        if object_type != meta_model.TABLE:
            return []

        sql = f"""show stats on "{database_name}"."{object_identification}";"""
        stmt = sa.text(sql)

        try:
            with translate_error():
                all_stats = ""
                logger.debug(stmt)
                with self.engine.connect() as con:
                    rows = [
                        r[0].replace("\r", "\n") for r in con.execute(stmt).fetchall()
                    ]
                    all_stats = "".join(rows)

        # pass no stats silently
        except exc.DBNoStatsDefined as err:
            return []

        # log no access rights but do not crash
        except exc.DBAccessRightsError as err:
            msg = f"{database_name}.{object_identification}: {err.message}"
            logger.error(msg)
            return []

        stats = [
            meta_model.TableStatistic(ddl_statement=f"{s}\n;")
            for s in all_stats.split(";")
            # last stats statement also ends with semicolon and ends with \n
            # filter out this - last, empty - statement
            if s.replace("\n", "").strip() != ""
        ]

        logger.debug(f"{len(stats)=}")
        return stats

    def _get_coment_from_tables_v(
        self,
        database_name: str,
        table_name: str,
        object_type: str,
    ) -> str | None:
        """
        Retrieves the comment for a database object from `dbc.tablesV`.

        Args:
            database_name (str): The name of the database containing the object.
            table_name (str): The name of the object to retrieve the comment for.
            object_type (str): The type of the object (e.g., "table").

        Returns:
            str | None: The comment for the object, or None if no comment is found.

        Behavior:
        - Constructs a SQL query to retrieve the comment from `dbc.tablesV`.
        - Executes the query using the database engine.
        - Returns the comment, or None if no comment is found.
        """
        sql = """
            select commentString as comment_string
            from dbc.tablesV
            where
                databaseName = :database_name
                and tableName = :table_name
                and commentString is not null
            """
        stmt = sa.text(sql).bindparams(
            database_name=database_name,
            table_name=table_name,
        )
        logger.debug(sql)
        logger.debug(f"{database_name=}, {table_name=}")
        with self.engine.connect() as con:
            for row in con.execute(stmt):
                comment = row.comment_string.replace("'", "''")
                comment = (
                    f"""comment on {object_type} "{database_name}"."{table_name}" """
                    f"""is '{comment}';"""
                )
                return comment
        return None

    @translate_error()
    def get_databases(self) -> list[meta_model.DescribedDatabase]:
        """
        Retrieves a list of databases from the Teradata system.

        Returns:
            list[meta_model.DescribedDatabase]: A list of described databases.

        Behavior:
        - Constructs a SQL query to retrieve database details from `DBC.databasesV`.
        - Executes the query using the database engine.
        - Maps the query result to a list of `meta_model.DescribedDatabase`.
        """
        sql = """
            SELECT
                databaseName AS database_name,
                ownerName AS owner_name,
                commentString AS comment_string,
                permSpace AS perm_space,
                spoolSpace AS spool_space,
                tempSpace AS temp_space,
                dbKind AS db_kind
            FROM DBC.databasesV
            ORDER BY databaseName
        """
        stmt = sa.text(sql)
        with self.engine.connect() as con:
            data = [
                meta_model.DescribedDatabase(
                    database_name=row.database_name,
                    comment_string=row.comment_string,
                    database_details=meta_model.DescribedTeradataDatabase(
                        owner_name=row.owner_name,
                        perm_space=row.perm_space,
                        spool_space=row.spool_space,
                        temp_space=row.temp_space,
                        db_kind=row.db_kind.strip(),
                    ),
                    parent_name=row.owner_name,
                    parent_tag="",
                )
                for row in con.execute(stmt)
            ]
        logger.debug(f"{len(data)=}")
        return data

    @translate_error()
    def test_connection(self):
        """
        Tests the connection to the Teradata database.

        Behavior:
        - Logs the start of the connection test.
        - Connects to the database engine.
        - Logs the success of the connection test.
        """
        logger.info("testing connection")
        with self.engine.connect():
            logger.info("success")

    @translate_error()
    def dispose(self):
        """
        Disposes of the SQL engine.

        Behavior:
        - Logs the disposal of the SQL engine.
        - Disposes of the database engine.
        """
        logger.info("dispose of the sql engine")
        self.engine.dispose()

    @translate_error()
    def change_database(self, database_name):
        """
        Changes the current database.

        Args:
            database_name (str): The name of the database to change to.

        Behavior:
        - Constructs a SQL statement to change the database.
        - Executes the SQL statement using the database engine.
        - Logs the SQL statement at the custom log level.
        - Logs a warning if the database name is invalid.
        """
        if not database_name:
            logger.warning(f"can not change database: {database_name=}")
            return
        with self.engine.connect() as con:
            stmt = f"database {database_name};"
            logger.log(LOG_LEVEL_NAME, _LOG_SEPARATOR + stmt + _LOG_SEPARATOR)
            con.exec_driver_sql(stmt)

    def get_full_definition(self, database: str, object: str) -> list[str] | None:
        """
        Retrieves the full definition of a database object.

        Args:
            database (str): The name of the database.
            table (str): The name of the table.

        Returns:
            str: The full definition of the object.
        """
        identified_object = self.get_identified_object(
            database_name=database,
            object_name=object,
            object_type=None,
        )
        if not identified_object:
            return None
        object = self.get_described_object(identified_object)
        if not object:
            return None

        statements = []
        statements = []
        if object.basic_definition:
            statements.append(object.basic_definition)

        if object.object_comment_ddl:
            statements.append(f"\n{object.object_comment_ddl}")

        separate_stats = True
        for i, detail in enumerate(object.additional_details):
            # na prvním řádku chceme mít dvouřádkový odskok
            if i == 0:
                statements.append("\n")

            if isinstance(detail, meta_model.TableStatistic):
                # na první statistice chceme mít prázdný řádek nahoře
                if separate_stats:
                    statements.append("\n")
                    separate_stats = False
                statements.append(detail.ddl_statement)
            elif isinstance(detail, meta_model.ColumnDescription):
                statements.append(detail.ddl_statement)
            else:
                msg = f"{detail=}\n{object=}"
                raise NotImplementedError(msg)

        return statements


# dbc.tablesV.tableKind: https://docs.teradata.com/r/Enterprise_IntelliFlex_VMware/Data-Dictionary/View-Column-Values/TableKind-Column
# ----- PRIO 1
# TABLES
#   O	Table with no primary index and no partitioning
#   T	Table with a primary index or primary AMP index, partitioning, or both. Or a partitioned table with NoPI
#   Q	Queue table
# V	View
# P	Stored procedure
# INDEXES
#   I	Join index
#   N	Hash index
# G	Trigger
# E	External stored procedure
# F	Standard function
# R	Table function
# M	Macro
# A	Aggregate function
# U	User-defined type
# X	Authorization - NOS - externí tabulky - asi docela podstatné

# ----- PRIO 2+
# B	Combined aggregate and ordered analytical function
# C	Table operator parser contract function : 7977] [SQLState HY000] 'Show' operation on 'xxxx' not allowed .
# D	JAR
# H	Instance or constructor method
# J	Journal
# K	Foreign server object.
# K is supported on the Teradata-to-Hadoop and Teradata-to-Teradata connectors.
# L	Table Operator
# S	Ordered analytical function
# Y	GLOP set
# Z	UIF
# 1	A DATASET schema object created by CREATE SCHEMA.
# 2	Function alias object.
# 3	Unbounded Array Framework (UAF) Time Series functions.
