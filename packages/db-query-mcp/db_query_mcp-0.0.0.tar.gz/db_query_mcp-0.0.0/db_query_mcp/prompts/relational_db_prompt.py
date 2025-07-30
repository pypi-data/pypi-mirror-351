query_prompt = '''查询数据库返回用户所需信息，确保生成的 SQL 严谨、专业、高效，可执行

## Database type: {db_type}

{db_schema}
'''

export_prompt = '''查询数据库返回用户所需信息，然后到处到指定csv文件中
确保生成的 SQL 严谨、专业、高效，可执行

## Database type: {db_type}

{db_schema}
'''
