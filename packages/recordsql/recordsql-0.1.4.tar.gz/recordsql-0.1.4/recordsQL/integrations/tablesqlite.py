from tablesqlite import SQLColumnInfo, SQLTableInfo
from ..query import (InsertQuery, INSERT, OnConflictQuery,
                     UpdateQuery, UPDATE,
                     DeleteQuery, DELETE,
                     SelectQuery, SELECT, WithQuery, JoinQuery,
                     CountQuery, COUNT,
                     ExistsQuery, EXISTS)
from ..types import SQLCol, SQLInput
from typing import Union, Dict, Tuple, List, Any, Optional
from ..dependencies import SQLCondition, no_condition, SQLExpression

def insert_query_for(table: SQLTableInfo, *items: Union[Dict, Tuple[str, Any]],
                    or_action: str = None,
                    on_conflict: OnConflictQuery = None,
                    returning: List[SQLCol] = None,
                    if_column_exists: bool = True, resolve_by: str = "raise", **kwargs) -> InsertQuery:
    set_columns = kwargs
    set_columns_in_self = {key: value for key, value in set_columns.items() if key in table.column_dict}
    for item in items:
        if isinstance(item, dict):
            set_columns_in_self.update({key: value for key, value in item.items() if key in table.column_dict})
            set_columns.update(item)
        elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str):
            set_columns[item[0]] = item[1]
            if item[0] in table.column_dict:
                set_columns_in_self[item[0]] = item[1]
        else:
            raise ValueError(f"Invalid item format: {item}. Expected dict or (str, any) tuple.")
    if if_column_exists and set_columns != set_columns_in_self:
        if resolve_by.lower() == "raise":
            raise ValueError("If 'if_column_exists' is True, all provided columns must exist in the table.")
        elif resolve_by.lower() == "ignore":
            set_columns = set_columns_in_self
    if not set_columns:
        raise ValueError("No valid columns provided for insertion.")
    returning = returning or []
    iq: InsertQuery = INSERT().INTO(table.name).SET(set_columns).RETURNING(*returning)
    if on_conflict is not None:
        iq = iq.ON_CONFLICT(do=on_conflict.do_what,
                            conflict_cols=on_conflict.conflict_cols,
                            set=on_conflict.set_clauses,
                            where=on_conflict.condition)
    iq.or_action = or_action
    return iq

def insert_query(self:SQLTableInfo, *items:Union[Dict,Tuple[str,Any]],
                or_action: str = None,
                on_conflict:OnConflictQuery=None,
                returning: List[SQLCol] = None,
                if_column_exists = True, resolve_by:str = "raise", **kwargs) -> InsertQuery:
        """
        Create an INSERT query for the table with the provided data.
        """
        return insert_query_for(
            self,
            *items,
            or_action=or_action,
            on_conflict=on_conflict,
            returning=returning,
            if_column_exists=if_column_exists,
            resolve_by=resolve_by,
            **kwargs
        )

def update_query_for(table: SQLTableInfo, set_clauses: dict[str, SQLInput] = None,
                condition: SQLCondition = no_condition, returning:List[SQLCol] = None, 
                if_column_exists: bool = True, resolve_by: str = "raise",                 
                **kwargs) -> UpdateQuery:
    initial_set_clauses = kwargs
    set_clauses_in_self = {key: value for key, value in initial_set_clauses.items() if key in table.column_dict}

    if set_clauses is not None:
        if not isinstance(set_clauses, dict):
            raise TypeError("set_clauses must be a dictionary.")
        set_clauses_in_self.update({key: value for key, value in set_clauses.items() if key in table.column_dict})
        initial_set_clauses.update(set_clauses)
    if if_column_exists and initial_set_clauses != set_clauses_in_self:
        if resolve_by.lower() == "raise":
            raise ValueError("If 'if_column_exists' is True, all provided columns must exist in the table.")
        elif resolve_by.lower() == "ignore":
            initial_set_clauses = set_clauses_in_self
        else:
            raise ValueError(f"Invalid resolve_by value: {resolve_by}")
    if not initial_set_clauses:
        raise ValueError("No valid columns provided for update.")
    returning = returning or []
    return UPDATE(table.name).SET(initial_set_clauses).WHERE(condition).RETURNING(*returning)

def update_query(self:SQLTableInfo, set_clauses: dict[str, SQLInput] = None,
                condition: SQLCondition = no_condition, returning:List[SQLCol] = None, 
                if_column_exists: bool = True, resolve_by: str = "raise", **kwargs) -> UpdateQuery:
        """
        Create an UPDATE query for the table with the provided data.
        """
        return update_query_for(
            self,
            set_clauses=set_clauses,
            condition=condition,
            returning=returning,
            if_column_exists=if_column_exists,
            resolve_by=resolve_by,
            **kwargs
        )

def delete_query_for(table: SQLTableInfo, condition: SQLCondition = no_condition,
                    returning: List[SQLCol] = None) -> DeleteQuery:
    returning = returning or []
    return DELETE(table.name).WHERE(condition).RETURNING(*returning)

def delete_query(self: SQLTableInfo, condition: SQLCondition = no_condition,
                 returning: List[SQLCol] = None) -> DeleteQuery:
    """
    Create a DELETE query for the table with the provided condition.
    """
    return delete_query_for(
        self,
        condition=condition,
        returning=returning
    )



def select_query_for(table: SQLTableInfo, columns: Union[str, list[SQLCol]] = "*",
                    condition: Any = None, order_by: Optional[List[Any]] = None,
                    criteria: List[str] = None, limit: Optional[Union[int, str]] = None,
                    offset: Optional[Union[int, str]] = None, group_by: Union[Any, list, None] = None,
                    having: Optional[Any] = None, *,
                    joins: List[JoinQuery] = None, withs: Optional[List[WithQuery]] = None,
                    ) -> SelectQuery:
    
    #Cant apply if_column_exists here, because columns can be any expression
    sq = SELECT(*columns).FROM(table.name).WHERE(condition).LIMIT(limit).OFFSET(offset).HAVING(having)
    sq.order_by = order_by
    sq.criteria = criteria
    sq.group_by = group_by
    sq.joins = joins or []
    sq.withs = withs or []
    return sq




def select_query(self: SQLTableInfo, columns: Union[str, list[SQLCol]] = "*",
                 condition: Any = None, order_by: Optional[List[Any]] = None,
                 criteria: List[str] = None, limit: Optional[Union[int, str]] = None,
                 offset: Optional[Union[int, str]] = None, group_by: Union[Any, list, None] = None,
                 having: Optional[Any] = None, *,
                 joins: List[Any] = None, withs: Optional[List[WithQuery]] = None) -> SelectQuery:
    """
    Create a SELECT query for the table with the provided parameters.
    """
    return select_query_for(
        self,
        columns=columns,
        condition=condition,
        order_by=order_by,
        criteria=criteria,
        limit=limit,
        offset=offset,
        group_by=group_by,
        having=having,
        joins=joins,
        withs=withs,
    )

    
def count_query_for(table:SQLTableInfo,
                    condition: Optional[SQLCondition] = no_condition,
                    group_by: Union[SQLCol, List[SQLCol], None] = None,
                    having: Optional[SQLCondition] = None) -> 'CountQuery':
    """
    Create a reference for a COUNT query.
    """
    return COUNT(table_name=table.name).WHERE(condition).GROUP_BY(group_by).HAVING(having)



def count_query(self: SQLTableInfo,
                condition: Optional[SQLCondition] = no_condition,
                group_by: Union[SQLCol, List[SQLCol], None] = None,
                having: Optional[SQLCondition] = None,
                ignore_forbidden_characters: bool = False) -> 'CountQuery':
    """
    Create a COUNT query reference for the table with the provided parameters.
    """
    return count_query_for(
        self,
        condition=condition,
        group_by=group_by,
        having=having,
        ignore_forbidden_characters=ignore_forbidden_characters
    )

def exists_query_for(table: SQLTableInfo,
                     condition: Optional[SQLCondition] = no_condition,
                     group_by: Union[SQLCol, List[SQLCol], None] = None,
                     having: Optional[SQLCondition] = None) -> 'ExistsQuery':
    """
    Create a reference for an EXISTS query.
    """
    return EXISTS(table_name=table.name).WHERE(condition).GROUP_BY(group_by).HAVING(having)

def exists_query(self: SQLTableInfo,
                 condition: Optional[SQLCondition] = no_condition,
                 group_by: Union[SQLCol, List[SQLCol], None] = None,
                 having: Optional[SQLCondition] = None) -> 'ExistsQuery':
    """
    Create an EXISTS query reference for the table with the provided parameters.
    """
    return exists_query_for(
        self,
        condition=condition,
        group_by=group_by,
        having=having
    )

def add_query_methods(cls: type[SQLTableInfo] = SQLTableInfo) -> type[SQLTableInfo]:
    """
    Adds record-level query builder methods to a SQLTableInfo-derived class.
    
    This includes: insert_query, update_query, delete_query, select_query, count_query, exists_query.
    """
    cls.insert_query = insert_query
    cls.update_query = update_query 
    cls.delete_query = delete_query
    cls.select_query = select_query
    cls.count_query = count_query
    cls.exists_query = exists_query
    return cls