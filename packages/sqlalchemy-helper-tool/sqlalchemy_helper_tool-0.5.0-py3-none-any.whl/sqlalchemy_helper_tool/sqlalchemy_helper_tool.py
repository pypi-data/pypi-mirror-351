from sqlalchemy import create_engine, inspect
import pandas as pd

class DbApi:
	"""
		Usage:
			dbApi = DbApi()
	"""
	def __init__(self, server, database, username, password, dict_params=None):
		self.server = server
		self.database = database
		self.username = username
		self.password = password
		self.con = 	self.connect(dict_params)

	# Make connection to server
	def connect(self, dict_params=None):	
		# create sqlalchemy engine
		engine = create_engine("mysql+pymysql://{user}:{pw}@{server}/{db}"
			 .format(user=self.username,
				pw=self.password,
				server=self.server,
				db=self.database),
				connect_args=dict_params
				)
		return engine
	
	def execute_query(self, query):
		id=self.con.execute(query)
		return id

	def table_in_db(self, table_name):
		tables_list = self.con.table_names()
		table_in = table_name in tables_list
		return table_in
	
	def table_info(self, table_name):
		insp = inspect(self.con)
		columns_table = insp.get_columns(table_name)
		return columns_table
	
	def read_sql(self, my_query, dict_params=None):
		if dict_params:  # Solo ejecuta si dict_params no es None o vacío
			for k, v in dict_params.items():
				self.con.execute(f"SET @{k} := '{v}';")
    
		# Run SQL
		return pd.read_sql_query(sql=my_query, con=self.con)
	
	def read_columns_table_db(self,table_name):
		df = self.read_sql(f'SELECT * FROM {table_name} LIMIT 1;')
		columns_name = df.columns.to_list()
		return columns_name
	
	def add_column(self, table_name, column_name, existing_column):
		if ' ' in column_name: column_name = "`" + column_name + "`"
		if ' ' in existing_column: existing_column = "`" + existing_column + "`"
		query=f"ALTER TABLE {table_name} ADD {column_name} TEXT AFTER {existing_column}"
		id=self.con.execute(query)

	# Just insert new values (new keys)
	def write_sql_key(self, df, table_name):
		tuple_ = ['%s']*len(df.columns)
		tuple_ = ','.join(tuple_)

		tuples = [tuple(x) for x in df.values]
		query = f"INSERT IGNORE INTO `{self.database}`.{table_name} VALUES({tuple_})"
		id=self.con.execute(query, tuples)

	def write_sql_key2(self, df, table_name):
		# Evita problemas con valores nulos
		df = df.where(df.notnull(), None)

		# Asegura que los nombres de columnas estén limpios y escapados
		columns = [f"`{col.strip().replace('`', '')}`" for col in df.columns]
		values_columns = ', '.join(columns)

		# Placeholders para cada columna
		tuple_ = ','.join(['%s'] * len(df.columns))

		# Datos como lista de tuplas
		tuples = [tuple(x) for x in df.values]

		# Query final
		query = f"INSERT IGNORE INTO `{self.database}`.{table_name} ({values_columns}) VALUES({tuple_})"

		# Ejecuta
		id = self.con.execute(query, tuples)

	
	# Add new rows (if you add a row with a key that is already in table_name it will give an error)
	def write_sql_df_append(self, df, table_name):																		
		df.to_sql(table_name, con=self.con, if_exists='append', index=False)

	def delete_table(self,table_name):
		if self.table_in_db(table_name):
			query = f"DELETE FROM {table_name}"	
			id=self.con.execute(query)

	def delete_column(self,table_name, column_name):
		if ' ' in column_name: column_name = "`" + column_name + "`"
		if self.table_in_db(table_name):
			query = f"ALTER TABLE {table_name} DROP {column_name}"	
			id=self.con.execute(query)

	# Replace table
	def write_sql_df_replace(self, df, table_name):
		# Delete table values                                 # If I use
		self.delete_table(table_name)                         # df.to_sql(table_name, con=con, if_exists='replace', index=False)
																# instead of this code the table table_name
												 				# is deleted first and I lose the characteristics 
																# of the table I already created initially
																# (keys, column's types....)
		df.to_sql(table_name, con=self.con, if_exists='append', index=False)			

	# Replace only certain columns
	def replace_sql_values(self, df, table_name, column_replace, columns_key):
		df = df[[columns_key] + [column_replace]]
	
		values_columns = str(tuple(df.columns))              # See if I can see all this prittier
		values_columns = values_columns.replace('(', '')     #
		values_columns = values_columns.replace(')', '')     #
		values_columns = values_columns.replace("'", '')     #
		tuples = ','.join([str(tuple(x)) for x in df.values])

		print("TESTING")
		id=self.con.execute(f"INSERT INTO {table_name} ({values_columns}) VALUES {tuples} ON DUPLICATE KEY UPDATE {column_replace}=VALUES({column_replace});")