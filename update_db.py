# from sqlalchemy import create_engine, text

# engine = create_engine('sqlite:///database/main.db') 

# with engine.connect() as connection:
#     # Check if 'is_muted' is in User table columns
#     result = connection.execute(text("PRAGMA table_info(Article)"))
#     columns = [column[1] for column in result]

#     if 'post_private' not in columns:
#         connection.execute(text("ALTER TABLE Article ADD COLUMN post_private VARCHAR"))
#         print("Created 'post_private' column successfully.")
#     else:
#         print("'post_private' column already exists.")

# ===========================================================================

#  -- ALTER USER TABLE FOR 'user_id' NOT NULL --
# from sqlalchemy import create_engine, text

# engine = create_engine('sqlite:///database/main.db') 

# with engine.connect() as connection:
#     connection.execute(text("PRAGMA foreign_keys=OFF;"))
    
#     # Step 1: Rename the existing table to a temporary name
#     connection.execute(text("ALTER TABLE user RENAME TO temp_user;"))

#     # Step 2: Create a new table with the corrected schema.
#     connection.execute(text(
#         """
#         CREATE TABLE user(
#             user_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username VARCHAR NOT NULL,
#             role VARCHAR NOT NULL,
#             password VARCHAR NOT NULL,
#             salt VARCHAR NOT NULL,
#             is_muted VARCHAR NOT NULL
#         );
#         """
#     ))

#     # Step 3: Copy the data from the old table into the new one
#     connection.execute(text(
#         """
#         INSERT INTO user (username, role, password, salt, is_muted)
#         SELECT username, role, password, salt, is_muted FROM temp_user;
#         """
#     ))
    
#     # Step 4: Delete the old table
#     connection.execute(text("DROP TABLE temp_user;"))
    
#     connection.execute(text("PRAGMA foreign_keys=ON;"))


# ===========================================================================

# from sqlalchemy import create_engine, text

# engine = create_engine('sqlite:///database/main.db') 

# with engine.connect() as connection:

#     # Copy the data from the temp_user table into the user table
#     connection.execute(text(
#         """
#         INSERT INTO user (username, role, password, salt, is_muted)
#         SELECT username, role, password, salt, is_muted FROM temp_user;
#         """
#     ))

#     # Delete the temp_user table
#     connection.execute(text("DROP TABLE temp_user;"))