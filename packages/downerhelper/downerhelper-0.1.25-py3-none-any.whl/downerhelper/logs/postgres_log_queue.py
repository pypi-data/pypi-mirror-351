import logging
import psycopg2 as pg
from psycopg2 import sql
from datetime import datetime, timezone
from downerhelper.secrets import get_config_dict
from downerhelper.logicapp import send_email

class PostgresLogQueue():
    def __init__(self, logger_name, job_id, table, db_config, print_logs=False):
        try:
            if '' in [logger_name, job_id, table] or \
                None in [logger_name, job_id, table] or db_config == {}:
                raise Exception("Invalid parameters")
            self.logger_name = logger_name
            self.job_id = job_id
            self.db_config = db_config
            self.table = table
            self.print_logs = print_logs
            self.queue = [
                {
                    'levelname': 'INFO',
                    'message': f'queue: {logger_name} created for job_id: {job_id}',
                    'created_at': datetime.now(timezone.utc)
                }
            ]
        except Exception as e:
            logging.error(f"Error setting up PostgresLogHandler: {e}")
            raise e

    def add(self, levelname, message):
        if levelname not in ["INFO", "DEBUG", "WARN", "ERROR"]:
            message = f"Invalid levelname '{levelname}'"
            self.add("ERROR", message)
            raise Exception(message)

        self.queue.append({
            'levelname': levelname,
            'message': message,
            'created_at': datetime.now(timezone.utc)
        })
        if not self.print_logs: return
        
        if levelname == 'ERROR':
            logging.error(message)
        elif levelname == 'WARNING':
            logging.warning(message)
        elif levelname == 'DEBUG':
            logging.debug(message)
        elif levelname == "INFO":
            logging.info(message)

    def save(self, throw_error=False):
        conn = cur = None
        try:
            conn = pg.connect(**self.db_config)
            cur = conn.cursor()
            cur.execute("set time zone 'UTC'")
            cur.execute(f"""
            create table if not exists {self.table} (
                id serial primary key,
                created_at timestamptz default now(),
                name varchar(255),
                levelname varchar(50),
                message text,
                job_id varchar(255) not null,
                is_checked boolean default false
            )""")
            conn.commit()
            
            for log in self.queue:
                cur.execute(f"""
                insert into {self.table} (name, levelname, message, job_id, created_at)
                values (%s, %s, %s, %s, %s)
                """, (self.logger_name, log['levelname'], log['message'], self.job_id, log['created_at']))
            conn.commit()

            self.queue = []

        except Exception as e:
            message = f"Error saving logs: {e}"
            logging.error(message)
            if throw_error: raise Exception(message)
        finally:
            if cur: cur.close()
            if conn: conn.close()

    def check_logs(self, key_url, recipients, interval_hours=24):
        conn = cur = None
        is_error = False
        try:
            conn = pg.connect(**self.db_config)
            cur = conn.cursor()

            cur.execute(sql.SQL("""
                select name, levelname, message, job_id, id
                from {}
                where is_checked = false
                and created_at > now() - interval {};
            """).format(
                sql.Identifier(self.table),
                sql.Literal(f'{interval_hours} hours')
            ))
            rows = cur.fetchall()

            ids = [row[4] for row in rows]
            
            error_job_ids = []
            for row in rows:
                if row[1] not in ['ERROR', 'WARN'] or \
                row[3] in error_job_ids: continue
                
                error_job_ids.append(row[3])

            if len(error_job_ids) == 0:
                return mark_logs_as_checked(ids, conn, cur, self.table)

            table_html = """
            <table border="1">
                <tr>
                    <th>Name</th>
                    <th>Level</th>
                    <th>Message</th>
                    <th>Job ID</th>
                </tr>
            """
            for row in rows:
                if row[1] not in ['ERROR', 'WARN']: continue
                table_html += f"""
                <tr>
                    <td>{row[0]}</td>
                    <td>{row[1]}</td>
                    <td>{row[2]}</td>
                    <td>{row[3]}</td>
                </tr>
                """


            subject = f"[ERROR] Log Check: {self.table}"
            body = f"""Jobs in error:<br/>{error_job_ids}<br/><br/>
Logs in error:<br/>{table_html}"""
            send_email(key_url, recipients, subject, body)

            mark_logs_as_checked(ids, conn, cur, self.table)

        except Exception as e:
            self.add('ERROR', f"Error checking logs: {e}")
            is_error = True
        finally:
            if cur: cur.close()
            if conn: conn.close()
            self.save()

            if is_error:
                raise Exception("Encountered an exception")

def setup_queue(logger_name, job_id, table, db_config_name, keyvault_url, dbname=None, print_logs=False):
    try:
        db_config = get_config_dict(db_config_name, keyvault_url, dbname=dbname)
        return PostgresLogQueue(logger_name, job_id, table, db_config, print_logs)
    except Exception as e:
        logging.error(f"Error setting up logger: {e}")
        raise Exception("Error setting up logger")
    
def mark_logs_as_checked(ids, conn, cur, table):
    cur.execute(sql.SQL("""
        update {}
        set is_checked = true
        where id = any(%s);
    """).format(
        sql.Identifier(table)
    ), (ids,))
    conn.commit()