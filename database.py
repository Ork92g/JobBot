import sqlite3


DATABASE = "jobs.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE
    )

    return connection


# ==========================================
# CREATE / MIGRATE DATABASE
# ==========================================

def create_database():

    connection = get_connection()

    cursor = connection.cursor()

    # Create table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            link TEXT,
            description TEXT DEFAULT '',
            score INTEGER DEFAULT 0,
            skills TEXT DEFAULT '',
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --------------------------------------
    # MIGRATION
    # --------------------------------------
    # If jobs.db already existed with the old
    # schema, add the missing columns.
    # --------------------------------------

    cursor.execute(
        "PRAGMA table_info(jobs)"
    )

    existing_columns = {
        row[1]
        for row in cursor.fetchall()
    }

    migrations = {

        "description":
            "ALTER TABLE jobs ADD COLUMN description TEXT DEFAULT ''",

        "score":
            "ALTER TABLE jobs ADD COLUMN score INTEGER DEFAULT 0",

        "skills":
            "ALTER TABLE jobs ADD COLUMN skills TEXT DEFAULT ''",
    }

    for column, sql in migrations.items():

        if column not in existing_columns:

            try:

                cursor.execute(sql)

                print(
                    f"Database migration: added {column}"
                )

            except sqlite3.OperationalError as error:

                print(
                    f"Migration warning ({column}): {error}"
                )

    connection.commit()

    connection.close()


# ==========================================
# CHECK NEW JOB
# ==========================================

def is_new_job(job_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT job_id
        FROM jobs
        WHERE job_id = ?
        """,
        (job_id,)
    )

    result = cursor.fetchone()

    connection.close()

    return result is None


# ==========================================
# SAVE JOB
# ==========================================

def save_job(job):

    connection = get_connection()

    cursor = connection.cursor()

    skills = job.get(
        "skills",
        []
    )

    # Convert skills list to text
    if isinstance(skills, list):

        skills = ", ".join(
            skills
        )

    cursor.execute(
        """
        INSERT OR IGNORE INTO jobs
        (
            job_id,
            title,
            company,
            location,
            link,
            description,
            score,
            skills
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job.get("job_id", ""),
            job.get("title", ""),
            job.get("company", ""),
            job.get("location", ""),
            job.get("link", ""),
            job.get("description", ""),
            job.get("score", 0),
            skills
        )
    )

    connection.commit()

    connection.close()


# ==========================================
# GET JOB
# ==========================================

def get_job(job_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            job_id,
            title,
            company,
            location,
            link,
            description,
            score,
            skills,
            first_seen
        FROM jobs
        WHERE job_id = ?
        """,
        (job_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if not row:

        return None

    return {
        "job_id": row[0],
        "title": row[1],
        "company": row[2],
        "location": row[3],
        "link": row[4],
        "description": row[5],
        "score": row[6],
        "skills": (
            row[7].split(", ")
            if row[7]
            else []
        ),
        "first_seen": row[8]
    }


# ==========================================
# DATABASE STATS
# ==========================================

def get_job_count():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM jobs"
    )

    count = cursor.fetchone()[0]

    connection.close()

    return count