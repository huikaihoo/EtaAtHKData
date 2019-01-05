import sqlite3

CT_ROUTE = """
    CREATE TABLE IF NOT EXISTS `Route` (
        `direction` INTEGER,
        `specialCode` INTEGER,
        `companyDetails` TEXT,
        `locFrom` TEXT,
        `locTo` TEXT,
        `details` TEXT,
        `path` TEXT,
        `info` TEXT,
        `eta` INTEGER,
        `displaySeq` INTEGER ,
        `typeSeq` INTEGER,
        `updateTime` INTEGER,
        `typeCode` INTEGER,
        `routeStr` TEXT,
        `company` TEXT NOT NULL,
        `routeNo` TEXT NOT NULL,
        `bound` INTEGER NOT NULL,
        `variant` INTEGER NOT NULL,
        PRIMARY KEY(`company`, `routeNo`, `bound`, `variant`)
    );
"""

CT_STOP = """
    CREATE TABLE IF NOT EXISTS `Stop` (
        `stopStr` TEXT,
        `seq` INTEGER,
        `name` TEXT,
        `locTo` TEXT,
        `details` TEXT,
        `latitude` REAL,
        `longitude` REAL,
        `fare` REAL,
        `info` TEXT,
        `etaStatus` TEXT,
        `etaResults` TEXT,
        `etaUpdateTime` INTEGER,
        `updateTime` INTEGER,
        `typeCode` INTEGER,
        `routeStr` TEXT,
        `company` TEXT NOT NULL,
        `routeNo` TEXT NOT NULL,
        `bound` INTEGER NOT NULL,
        `variant` INTEGER NOT NULL,
        PRIMARY KEY(`company`, `routeNo`, `bound`, `variant`, `seq`)
    );
"""

if __name__ == "__main__":
    # Create app database
    with sqlite3.connect("db/app.db") as conn:
        db = conn.cursor()
        cursor = db.execute(CT_ROUTE)
        cursor = db.execute(CT_STOP)
