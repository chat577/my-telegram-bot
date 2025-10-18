import os
import psycopg2
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Подключение к базе данных
def get_connection():
    try:
        # Railway автоматически предоставляет DATABASE_URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.warning("DATABASE_URL not found, using SQLite fallback")
            return None
            
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

# Инициализация базы данных
def init_database():
    conn = get_connection()
    if not conn:
        logger.warning("Could not initialize database")
        return
        
    try:
        with conn.cursor() as cur:
            # Таблица пользователей
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(100),
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица истории запросов
            cur.execute('''
                CREATE TABLE IF NOT EXISTS user_requests (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    request_type VARCHAR(50),
                    request_data TEXT,
                    response_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица избранных фактов/шуток
            cur.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    content_type VARCHAR(50),
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    finally:
        conn.close()

# Регистрация/обновление пользователя
def update_user(user_id, username=None, first_name=None, last_name=None):
    conn = get_connection()
    if not conn:
        return
        
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, last_active)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    last_active = EXCLUDED.last_active
            ''', (user_id, username, first_name, last_name, datetime.now()))
            
        conn.commit()
    except Exception as e:
        logger.error(f"Error updating user: {e}")
    finally:
        conn.close()

# Сохранение запроса в историю
def save_request(user_id, request_type, request_data, response_data):
    conn = get_connection()
    if not conn:
        return
        
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO user_requests (user_id, request_type, request_data, response_data)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, request_type, request_data, response_data))
            
        conn.commit()
    except Exception as e:
        logger.error(f"Error saving request: {e}")
    finally:
        conn.close()

# Получение статистики пользователя
def get_user_stats(user_id):
    conn = get_connection()
    if not conn:
        return None
        
    try:
        with conn.cursor() as cur:
            # Общее количество запросов
            cur.execute('''
                SELECT COUNT(*) FROM user_requests WHERE user_id = %s
            ''', (user_id,))
            total_requests = cur.fetchone()[0]
            
            # Популярные типы запросов
            cur.execute('''
                SELECT request_type, COUNT(*) 
                FROM user_requests 
                WHERE user_id = %s 
                GROUP BY request_type 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            ''', (user_id,))
            popular_types = cur.fetchall()
            
            # Последняя активность
            cur.execute('''
                SELECT last_active FROM users WHERE user_id = %s
            ''', (user_id,))
            last_active = cur.fetchone()
            
            return {
                'total_requests': total_requests,
                'popular_types': popular_types,
                'last_active': last_active[0] if last_active else None
            }
            
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        return None
    finally:
        conn.close()

# Добавление в избранное
def add_to_favorites(user_id, content_type, content):
    conn = get_connection()
    if not conn:
        return False
        
    try:
        with conn.cursor() as cur:
            cur.execute('''
                INSERT INTO favorites (user_id, content_type, content)
                VALUES (%s, %s, %s)
            ''', (user_id, content_type, content))
            
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error adding to favorites: {e}")
        return False
    finally:
        conn.close()

# Получение избранного
def get_favorites(user_id, content_type=None):
    conn = get_connection()
    if not conn:
        return []
        
    try:
        with conn.cursor() as cur:
            if content_type:
                cur.execute('''
                    SELECT content, created_at 
                    FROM favorites 
                    WHERE user_id = %s AND content_type = %s
                    ORDER BY created_at DESC
                ''', (user_id, content_type))
            else:
                cur.execute('''
                    SELECT content_type, content, created_at 
                    FROM favorites 
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT 20
                ''', (user_id,))
                
            return cur.fetchall()
            
    except Exception as e:
        logger.error(f"Error getting favorites: {e}")
        return []
    finally:
        conn.close()
