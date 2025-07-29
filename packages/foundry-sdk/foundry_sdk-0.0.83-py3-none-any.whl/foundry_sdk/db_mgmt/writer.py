from foundry_sdk.db_mgmt import SQLDatabase, InsertionMode
import pandas as pd

class Writer():
    
    """
    Class to write data to a database table - all tables will inherit from this class

    """

    def __init__(self, db: SQLDatabase, insertion_mode: InsertionMode):
        self.db = db
        self.insertion_mode = insertion_mode

    def write_to_db_single_row(self, *args, save_ids=True):
        query = self.build_query()
        ids = self.db.execute_query(query, args, fetchone=True, commit=True)[0]
        self.db.close()
        self.ids = ids if save_ids else None

    def write_to_db_multi_row(self, df: pd.DataFrame, save_ids=True, show_progress_bar=False):

        # check that columns are the same as the ones in the table
        if not set(df.columns) == set(self.COLUMNS):
            raise ValueError(f"Columns in DataFrame {df.columns} do not match the columns in the table: {self.COLUMNS}")
        
        # ensure the order of columns is the same as the one in the table
        df = df[self.COLUMNS]

        # create a list of tuples from the DataFrame and convert all values to TYPES

        args = [
            tuple(None if pd.isna(val) else t(val) for t, val in zip(self.TYPES, row))
            for row in df.values
        ]
        
        query = self.build_query(single_placeholder=False)

        # note: multi-query executes the query one-by-one so fetchone is the correct setting
        ids = self.db.execute_multi_query(query, args, fetchone=save_ids, commit=True, show_progress_bar=show_progress_bar)
        self.db.close()
        self.ids = ids if save_ids else None
        

    def build_query(self, single_placeholder=False):
        # If a UNIQUE attribute is defined, use it; otherwise default to the first column

        confict_resulution = {
            InsertionMode.IGNORE: "DO NOTHING",
            InsertionMode.RAISE: "",
            InsertionMode.UPDATE: "DO UPDATE",
            InsertionMode.INSERT_MISSING: "DO NOTHING"
        }
        if self.insertion_mode == InsertionMode.UPDATE:
            update_clause = "SET" + ", ".join(f'"{col}" = EXCLUDED."{col}"' for col in self.COLUMNS if col != "ID")
        else:
            update_clause = ""
        
        conflict_columns = getattr(self, "UNIQUE")
        if conflict_columns is None:
            conflict_clause = ""
            update_clause = ""
        else:
            conflict_clause = "ON CONFLICT (" + ", ".join(f'"{col}"' for col in conflict_columns) + f") {confict_resulution[self.insertion_mode]}"

        if single_placeholder:
            placeholders = "%s" 
        else:
            placeholders = ", ".join(["%s" for _ in range(len(self.COLUMNS))])
        column_names = ", ".join(f'"{col}"' for col in self.COLUMNS)
        returning_clause = 'RETURNING "ID"' if getattr(self, "AUTO_ID", False) else ""

        query = f"""
            INSERT INTO {self.TABLE} ({column_names})
            VALUES ({placeholders})
            {conflict_clause}
            {update_clause}
            {returning_clause}
            """

        return query.strip()
