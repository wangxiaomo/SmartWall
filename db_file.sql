PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE "SW_messages" (
    "src" TEXT NOT NULL,
    "dst" TEXT NOT NULL,
    "message" TEXT NOT NULL,
    "pub_time" TEXT NOT NULL
);
CREATE TABLE "sw_app" (
    "cfg_name" TEXT NOT NULL,
    "cfg_value" TEXT NOT NULL
);
INSERT INTO "sw_app" VALUES('message_time','1990-01-01 07:00:00');
INSERT INTO "sw_app" VALUES('post_time','1990-01-01 07:00:00');
CREATE TABLE "sw_users" (
    "user_id" TEXT NOT NULL,
    "screen_name" TEXT NOT NULL,
    "sex" TEXT NOT NULL,
    "school" TEXT NOT NULL
);
COMMIT;
