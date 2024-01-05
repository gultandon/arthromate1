-- Initial schema for ArthroMate
-- mysql -h <DB_HOST> -u arthromate -p arthromate < migrations/001_init.sql

CREATE TABLE IF NOT EXISTS users (
    userId    VARCHAR(128) NOT NULL,
    email     VARCHAR(255),
    createdAt VARCHAR(50),
    updatedAt VARCHAR(50),
    profile   JSON,
    PRIMARY KEY (userId)
);

CREATE TABLE IF NOT EXISTS pain_reports (
    reportId       VARCHAR(36)  NOT NULL,
    userId         VARCHAR(128) NOT NULL,
    timestamp      VARCHAR(50)  NOT NULL,
    painLevel      INT          NOT NULL,
    affectedJoints JSON         NOT NULL,
    notes          TEXT,
    mobility       VARCHAR(10),
    PRIMARY KEY (reportId),
    KEY idx_user_timestamp (userId, timestamp)
);
