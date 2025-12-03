from invoke import task
import os
import sqlite3
import json

@task
def init(c):
    """Initialize the SQLite database file"""
    db_path = os.path.join(os.path.dirname(__file__), 'words.db')
    
    if os.path.exists(db_path):
        print(f"✓ Database {db_path} already exists")
        return
    
    conn = sqlite3.connect(db_path)
    conn.close()
    print(f"✓ Database initialized at {db_path}")

@task
def migrate(c):
    """Run database migrations"""
    db_path = os.path.join(os.path.dirname(__file__), 'words.db')
    migrations_dir = os.path.join(os.path.dirname(__file__), 'db', 'migrations')
    
    if not os.path.exists(db_path):
        print("✗ Database not initialized. Run 'invoke init' first.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
    
    for migration_file in migration_files:
        file_path = os.path.join(migrations_dir, migration_file)
        print(f"  Running: {migration_file}")
        
        with open(file_path, 'r') as f:
            sql = f.read()
        
        cursor.executescript(sql)
        conn.commit()
    
    conn.close()
    print("✓ Migrations completed successfully")

@task
def seed(c):
    """Seed the database with initial data from JSON files"""
    db_path = os.path.join(os.path.dirname(__file__), 'words.db')
    seeds_dir = os.path.join(os.path.dirname(__file__), 'db', 'seeds')
    
    if not os.path.exists(db_path):
        print("✗ Database not initialized. Run 'invoke init' first.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for seed_file in sorted(os.listdir(seeds_dir)):
        if seed_file.endswith('.json'):
            group_name = seed_file.replace('.json', '').replace('_', ' ').title()
            print(f"  Seeding: {group_name}")
            
            with open(os.path.join(seeds_dir, seed_file)) as f:
                words_data = json.load(f)
            
            # Insert group
            cursor.execute('INSERT OR IGNORE INTO groups (name) VALUES (?)', (group_name,))
            conn.commit()
            
            cursor.execute('SELECT id FROM groups WHERE name = ?', (group_name,))
            group_id = cursor.fetchone()[0]
            
            # Insert words
            for word_data in words_data:
                cursor.execute(
                    'INSERT INTO words (japanese, romaji, english, parts) VALUES (?, ?, ?, ?)',
                    (word_data.get('kanji', ''), word_data.get('romaji', ''), word_data.get('english', ''), json.dumps(word_data.get('parts', [])))
                )
                conn.commit()
                
                word_id = cursor.lastrowid
                cursor.execute('INSERT INTO words_groups (word_id, group_id) VALUES (?, ?)', (word_id, group_id))
                conn.commit()
    
    conn.close()
    print("✓ Seeding completed successfully")
