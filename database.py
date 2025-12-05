"""
Database Manager with Dynamic Schema Support
Handles dynamic table creation based on JSON keys
"""
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Text, inspect, text
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Any
import config
import pandas as pd


class DynamicDatabaseManager:
    def __init__(self, db_url: str = config.DATABASE_URL):
        """Initialize database connection"""
        self.engine = create_engine(db_url, echo=False)
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
    
    def get_column_type(self, value: Any):
        """Determine SQLAlchemy column type based on value"""
        if isinstance(value, int):
            return Integer
        elif isinstance(value, float):
            return Float
        elif isinstance(value, str) and len(value) > 255:
            return Text
        else:
            return String(255)
    
    def create_or_update_table(self, table_name: str, sample_data: Dict[str, Any]):
        """
        Create table if it doesn't exist, or add new columns if needed
        
        Args:
            table_name: Name of the table
            sample_data: Sample record to infer schema from
        """
        inspector = inspect(self.engine)
        
        # Ensure table name is valid
        table_name = table_name.lower().replace(' ', '_').replace('-', '_')
        
        if not inspector.has_table(table_name):
            # Create new table
            columns = [Column('id', Integer, primary_key=True, autoincrement=True)]
            
            for key, value in sample_data.items():
                col_name = self._normalize_column_name(str(key))
                col_type = self.get_column_type(value)
                columns.append(Column(col_name, col_type, nullable=True))
            
            table = Table(table_name, self.metadata, *columns)
            table.create(self.engine)
            print(f"Created table: {table_name}")
        
        else:
            # Check for new columns and add them
            existing_columns = {col['name'] for col in inspector.get_columns(table_name)}
            
            for key, value in sample_data.items():
                col_name = self._normalize_column_name(str(key))
                
                if col_name not in existing_columns:
                    col_type_name = self._get_sql_type_name(value)
                    
                    # Add new column using raw SQL
                    from sqlalchemy import text
                    with self.engine.connect() as conn:
                        conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type_name}'))
                        conn.commit()
                    
                    print(f"Added column '{col_name}' to table '{table_name}'")
    
    def _normalize_column_name(self, name: str) -> str:
        """
        Normalize column name to be SQL-safe
        - Convert to lowercase
        - Replace spaces and hyphens with underscores
        - Add 'col_' prefix if starts with number
        - Replace 'id' with 'record_id' to avoid primary key conflict
        """
        col_name = name.lower().replace(' ', '_').replace('-', '_')
        col_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in col_name)
        
        # Add prefix if starts with number
        if col_name and col_name[0].isdigit():
            col_name = 'col_' + col_name
        
        # Avoid conflict with primary key
        if col_name == 'id':
            col_name = 'record_id'
        
        # Ensure it's not empty
        if not col_name:
            col_name = 'column'
        
        return col_name
    
    def _get_sql_type_name(self, value: Any) -> str:
        """Get SQL type name as string"""
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, str) and len(value) > 255:
            return "TEXT"
        else:
            return "VARCHAR(255)"
    
    def insert_data(self, table_name: str, data: List[Dict[str, Any]]):
        """
        Insert data into table
        
        Args:
            table_name: Name of the table
            data: List of records to insert
        """
        if not data:
            return
        
        # Ensure table name is valid
        table_name = table_name.lower().replace(' ', '_').replace('-', '_')
        
        # First, create/update table schema based on first record
        self.create_or_update_table(table_name, data[0])
        
        # Ensure all subsequent records have consistent schema
        for record in data[1:]:
            self.create_or_update_table(table_name, record)
        
        # Load table metadata
        self.metadata.reflect(bind=self.engine)
        table = self.metadata.tables[table_name]
        
        # Normalize all records
        normalized_data = []
        for record in data:
            normalized_record = {}
            for key, value in record.items():
                col_name = self._normalize_column_name(str(key))
                normalized_record[col_name] = value
            normalized_data.append(normalized_record)
        
        # Insert data
        with self.engine.connect() as conn:
            conn.execute(table.insert(), normalized_data)
            conn.commit()
        
        print(f"Inserted {len(normalized_data)} records into '{table_name}'")
    
    def get_all_data(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Retrieve all data from a table
        
        Args:
            table_name: Name of the table
        
        Returns:
            List of records as dictionaries
        """
        table_name = table_name.lower().replace(' ', '_').replace('-', '_')
        
        inspector = inspect(self.engine)
        if not inspector.has_table(table_name):
            return []
        
        self.metadata.reflect(bind=self.engine)
        table = self.metadata.tables[table_name]
        
        with self.engine.connect() as conn:
            result = conn.execute(table.select())
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result]
    
    def get_all_tables(self) -> List[str]:
        """Get list of all tables in database"""
        inspector = inspect(self.engine)
        return inspector.get_table_names()
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """
        Get schema of a table
        
        Args:
            table_name: Name of the table
        
        Returns:
            List of column definitions
        """
        table_name = table_name.lower().replace(' ', '_').replace('-', '_')
        
        inspector = inspect(self.engine)
        if not inspector.has_table(table_name):
            return []
        
        columns = inspector.get_columns(table_name)
        return [
            {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"]
            }
            for col in columns
        ]
    
    def export_to_excel(self, table_name: str, file_path: str):
        """
        Export table data to Excel file
        
        Args:
            table_name: Name of the table
            file_path: Path where Excel file should be saved
        """
        table_name = table_name.lower().replace(' ', '_').replace('-', '_')
        
        # Get data
        data = self.get_all_data(table_name)
        
        if not data:
            raise ValueError(f"No data found in table '{table_name}'")
        
        # Convert to DataFrame and save
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False, sheet_name=table_name[:31])  # Excel sheet name limit 31 chars
        print(f"Exported {len(data)} records to {file_path}")
    
    def delete_table(self, table_name: str):
        """
        Delete a table from the database
        
        Args:
            table_name: Name of the table to delete
        """
        table_name = table_name.lower().replace(' ', '_').replace('-', '_')
        
        inspector = inspect(self.engine)
        if not inspector.has_table(table_name):
            raise ValueError(f"Table '{table_name}' not found")
        
        with self.engine.connect() as conn:
            conn.execute(text(f'DROP TABLE {table_name}'))
            conn.commit()
        
        print(f"Deleted table '{table_name}'")
    
    def delete_row(self, table_name: str, row_id: int):
        """
        Delete a specific row from a table
        
        Args:
            table_name: Name of the table
            row_id: ID of the row to delete
        """
        table_name = table_name.lower().replace(' ', '_').replace('-', '_')
        
        self.metadata.reflect(bind=self.engine)
        table = self.metadata.tables[table_name]
        
        with self.engine.connect() as conn:
            conn.execute(table.delete().where(table.c.id == row_id))
            conn.commit()
        
        print(f"Deleted row {row_id} from '{table_name}'")
    
    def update_row(self, table_name: str, row_id: int, updates: Dict[str, Any]):
        """
        Update a specific row in a table
        
        Args:
            table_name: Name of the table
            row_id: ID of the row to update
            updates: Dictionary of column:value pairs to update
        """
        table_name = table_name.lower().replace(' ', '_').replace('-', '_')
        
        # Normalize column names in updates
        normalized_updates = {}
        for key, value in updates.items():
            col_name = self._normalize_column_name(str(key))
            normalized_updates[col_name] = value
        
        self.metadata.reflect(bind=self.engine)
        table = self.metadata.tables[table_name]
        
        with self.engine.connect() as conn:
            conn.execute(
                table.update().where(table.c.id == row_id).values(**normalized_updates)
            )
            conn.commit()
        
        print(f"Updated row {row_id} in '{table_name}'")
    
    def add_row(self, table_name: str, row_data: Dict[str, Any]):
        """
        Add a new row to a table
        
        Args:
            table_name: Name of the table
            row_data: Dictionary of column:value pairs for the new row
        """
        table_name = table_name.lower().replace(' ', '_').replace('-', '_')
        
        # Ensure table has all necessary columns
        self.create_or_update_table(table_name, row_data)
        
        # Normalize column names
        normalized_data = {}
        for key, value in row_data.items():
            col_name = self._normalize_column_name(str(key))
            normalized_data[col_name] = value
        
        self.metadata.reflect(bind=self.engine)
        table = self.metadata.tables[table_name]
        
        with self.engine.connect() as conn:
            conn.execute(table.insert(), [normalized_data])
            conn.commit()
        
        print(f"Added new row to '{table_name}'")
