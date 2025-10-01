import mysql.connector

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='als32@#nss',
        database='midnight'
    )
    
    cursor = connection.cursor()
    
    # Check the volume column definition
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, COLUMN_TYPE, NUMERIC_PRECISION, NUMERIC_SCALE
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'midnight' 
        AND TABLE_NAME = 'itens_estoque' 
        AND COLUMN_NAME = 'volume'
    """)
    
    result = cursor.fetchone()
    if result:
        print(f"Column definition: {result}")
    else:
        print("Volume column not found!")
    
    # Check a few existing volume values
    cursor.execute("SELECT id, nome, volume FROM itens_estoque WHERE volume IS NOT NULL LIMIT 5")
    items = cursor.fetchall()
    
    print("\nExisting volume values:")
    for item in items:
        print(f"ID: {item[0]}, Nome: {item[1]}, Volume: {item[2]} (tipo: {type(item[2])})")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")
