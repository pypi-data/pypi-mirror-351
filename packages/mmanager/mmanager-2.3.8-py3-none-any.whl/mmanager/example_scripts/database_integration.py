from mmanager.mmanager import TableInfo, FieldInfo

secret_key = 'YOUR_SECRET_KEY'
url = 'YOUR_API_URL'

table_data = {
    "table_type": "actual",
    "table_name": "daily_act2",
    "db_link": 11
}
table_response = TableInfo(secret_key, url).post_table_info(data=table_data)
print("Table added:", table_response)

field_data = {
    "table_id": 9,
    "display_name": "actual2",
    "field_type": "",
    "field_name": ""
}
field_response = FieldInfo(secret_key, url).post_field_info(data=field_data)
print("Field added:", field_response)
