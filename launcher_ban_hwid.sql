/*
 Navicat Premium Data Transfer

 Source Server         : localhost_5432
 Source Server Type    : PostgreSQL
 Source Server Version : 130020 (130020)
 Source Host           : localhost:5432
 Source Catalog        : postgres
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 130020 (130020)
 File Encoding         : 65001

 Date: 28/05/2025 14:39:13
*/


-- ----------------------------
-- Table structure for launcher_ban
-- ----------------------------
DROP TABLE IF EXISTS "public"."launcher_ban";
CREATE TABLE "public"."launcher_ban" (
  "id" int4 NOT NULL DEFAULT nextval('launcher_ban_hwid_id_seq'::regclass),
  "hwid" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "serial_number" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "razon" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "mac_address" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "is_banned" bool NOT NULL DEFAULT false,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON TABLE "public"."launcher_ban" IS 'HWIDs baneados del launcher';

-- ----------------------------
-- Table structure for launcher_download_log
-- ----------------------------
DROP TABLE IF EXISTS "public"."launcher_download_log";
CREATE TABLE "public"."launcher_download_log" (
  "id" int4 NOT NULL DEFAULT nextval('launcher_download_log_id_seq'::regclass),
  "ip_address" inet NOT NULL,
  "user_agent" varchar(500) COLLATE "pg_catalog"."default",
  "file_requested" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "file_type" varchar(50) COLLATE "pg_catalog"."default",
  "success" bool DEFAULT false,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON TABLE "public"."launcher_download_log" IS 'Log de descargas de archivos';

-- ----------------------------
-- Table structure for launcher_game_file
-- ----------------------------
DROP TABLE IF EXISTS "public"."launcher_game_file";
CREATE TABLE "public"."launcher_game_file" (
  "id" int4 NOT NULL DEFAULT nextval('launcher_game_file_id_seq'::regclass),
  "filename" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "relative_path" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "md5_hash" char(32) COLLATE "pg_catalog"."default" NOT NULL,
  "file_size" int8,
  "version_id" int4 NOT NULL,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON TABLE "public"."launcher_game_file" IS 'Archivos asociados a versiones del juego';

-- ----------------------------
-- Table structure for launcher_game_version
-- ----------------------------
DROP TABLE IF EXISTS "public"."launcher_game_version";
CREATE TABLE "public"."launcher_game_version" (
  "id" int4 NOT NULL DEFAULT nextval('launcher_game_version_id_seq'::regclass),
  "version" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "is_latest" bool DEFAULT false,
  "release_notes" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "created_by" int4
)
;
COMMENT ON TABLE "public"."launcher_game_version" IS 'Versiones del juego';

-- ----------------------------
-- Table structure for launcher_news_message
-- ----------------------------
DROP TABLE IF EXISTS "public"."launcher_news_message";
CREATE TABLE "public"."launcher_news_message" (
  "id" int4 NOT NULL DEFAULT nextval('launcher_news_message_id_seq'::regclass),
  "type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "message" text COLLATE "pg_catalog"."default" NOT NULL,
  "is_active" bool DEFAULT true,
  "priority" int4 DEFAULT 0,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "created_by" int4
)
;
COMMENT ON TABLE "public"."launcher_news_message" IS 'Mensajes y noticias del launcher';

-- ----------------------------
-- Table structure for launcher_server_settings
-- ----------------------------
DROP TABLE IF EXISTS "public"."launcher_server_settings";
CREATE TABLE "public"."launcher_server_settings" (
  "id" int4 NOT NULL DEFAULT nextval('launcher_server_settings_id_seq'::regclass),
  "key" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "value" text COLLATE "pg_catalog"."default" NOT NULL,
  "description" varchar(255) COLLATE "pg_catalog"."default",
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_by" int4
)
;
COMMENT ON TABLE "public"."launcher_server_settings" IS 'Configuraciones del servidor';

-- ----------------------------
-- Table structure for launcher_update_package
-- ----------------------------
DROP TABLE IF EXISTS "public"."launcher_update_package";
CREATE TABLE "public"."launcher_update_package" (
  "id" int4 NOT NULL DEFAULT nextval('launcher_update_package_id_seq'::regclass),
  "filename" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "version_id" int4 NOT NULL,
  "file_path" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "file_size" int8,
  "md5_hash" char(32) COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "uploaded_by" int4
)
;
COMMENT ON TABLE "public"."launcher_update_package" IS 'Paquetes de actualización';

-- ----------------------------
-- Table structure for launcher_user
-- ----------------------------
DROP TABLE IF EXISTS "public"."launcher_user";
CREATE TABLE "public"."launcher_user" (
  "id" int4 NOT NULL DEFAULT nextval('launcher_user_id_seq'::regclass),
  "username" varchar(80) COLLATE "pg_catalog"."default" NOT NULL,
  "email" varchar(120) COLLATE "pg_catalog"."default" NOT NULL,
  "password_hash" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "is_admin" bool DEFAULT false,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "last_login" timestamp(6)
)
;
COMMENT ON TABLE "public"."launcher_user" IS 'Usuarios del sistema launcher';

-- ----------------------------
-- Table structure for launcher_version
-- ----------------------------
DROP TABLE IF EXISTS "public"."launcher_version";
CREATE TABLE "public"."launcher_version" (
  "id" int4 NOT NULL DEFAULT nextval('launcher_version_id_seq'::regclass),
  "version" varchar(20) COLLATE "pg_catalog"."default" NOT NULL,
  "filename" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "file_path" varchar(500) COLLATE "pg_catalog"."default" NOT NULL,
  "is_current" bool DEFAULT false,
  "release_notes" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "created_by" int4
)
;
COMMENT ON TABLE "public"."launcher_version" IS 'Versiones del launcher';

-- ----------------------------
-- Indexes structure for table launcher_ban
-- ----------------------------
CREATE INDEX "idx_ban_hwid_hwid" ON "public"."launcher_ban" USING btree (
  "hwid" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE INDEX "idx_ban_hwid_serial" ON "public"."launcher_ban" USING btree (
  "serial_number" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table launcher_ban
-- ----------------------------
ALTER TABLE "public"."launcher_ban" ADD CONSTRAINT "launcher_ban_hwid_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table launcher_download_log
-- ----------------------------
CREATE INDEX "idx_download_log_created" ON "public"."launcher_download_log" USING btree (
  "created_at" "pg_catalog"."timestamp_ops" ASC NULLS LAST
);
CREATE INDEX "idx_download_log_ip" ON "public"."launcher_download_log" USING btree (
  "ip_address" "pg_catalog"."inet_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table launcher_download_log
-- ----------------------------
ALTER TABLE "public"."launcher_download_log" ADD CONSTRAINT "launcher_download_log_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table launcher_game_file
-- ----------------------------
CREATE INDEX "idx_game_file_hash" ON "public"."launcher_game_file" USING btree (
  "md5_hash" COLLATE "pg_catalog"."default" "pg_catalog"."bpchar_ops" ASC NULLS LAST
);
CREATE INDEX "idx_game_file_version" ON "public"."launcher_game_file" USING btree (
  "version_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table launcher_game_file
-- ----------------------------
CREATE TRIGGER "update_launcher_game_file_modtime" BEFORE UPDATE ON "public"."launcher_game_file"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_modified_column"();

-- ----------------------------
-- Primary Key structure for table launcher_game_file
-- ----------------------------
ALTER TABLE "public"."launcher_game_file" ADD CONSTRAINT "launcher_game_file_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table launcher_game_version
-- ----------------------------
CREATE UNIQUE INDEX "idx_game_version_latest" ON "public"."launcher_game_version" USING btree (
  "is_latest" "pg_catalog"."bool_ops" ASC NULLS LAST
) WHERE is_latest = true;

-- ----------------------------
-- Uniques structure for table launcher_game_version
-- ----------------------------
ALTER TABLE "public"."launcher_game_version" ADD CONSTRAINT "launcher_game_version_version_key" UNIQUE ("version");

-- ----------------------------
-- Checks structure for table launcher_game_version
-- ----------------------------
ALTER TABLE "public"."launcher_game_version" ADD CONSTRAINT "chk_version_format" CHECK (version::text ~ '^[0-9]+\.[0-9]+(\.[0-9]+)?$'::text);

-- ----------------------------
-- Primary Key structure for table launcher_game_version
-- ----------------------------
ALTER TABLE "public"."launcher_game_version" ADD CONSTRAINT "launcher_game_version_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table launcher_news_message
-- ----------------------------
CREATE INDEX "idx_news_active" ON "public"."launcher_news_message" USING btree (
  "is_active" "pg_catalog"."bool_ops" ASC NULLS LAST
);
CREATE INDEX "idx_news_priority" ON "public"."launcher_news_message" USING btree (
  "priority" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Checks structure for table launcher_news_message
-- ----------------------------
ALTER TABLE "public"."launcher_news_message" ADD CONSTRAINT "chk_priority_range" CHECK (priority >= 0 AND priority <= 100);

-- ----------------------------
-- Primary Key structure for table launcher_news_message
-- ----------------------------
ALTER TABLE "public"."launcher_news_message" ADD CONSTRAINT "launcher_news_message_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table launcher_server_settings
-- ----------------------------
CREATE INDEX "idx_server_settings_key" ON "public"."launcher_server_settings" USING btree (
  "key" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Triggers structure for table launcher_server_settings
-- ----------------------------
CREATE TRIGGER "update_launcher_server_settings_modtime" BEFORE UPDATE ON "public"."launcher_server_settings"
FOR EACH ROW
EXECUTE PROCEDURE "public"."update_modified_column"();

-- ----------------------------
-- Uniques structure for table launcher_server_settings
-- ----------------------------
ALTER TABLE "public"."launcher_server_settings" ADD CONSTRAINT "launcher_server_settings_key_key" UNIQUE ("key");

-- ----------------------------
-- Primary Key structure for table launcher_server_settings
-- ----------------------------
ALTER TABLE "public"."launcher_server_settings" ADD CONSTRAINT "launcher_server_settings_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table launcher_update_package
-- ----------------------------
CREATE INDEX "idx_update_package_version" ON "public"."launcher_update_package" USING btree (
  "version_id" "pg_catalog"."int4_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table launcher_update_package
-- ----------------------------
ALTER TABLE "public"."launcher_update_package" ADD CONSTRAINT "launcher_update_package_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table launcher_user
-- ----------------------------
ALTER TABLE "public"."launcher_user" ADD CONSTRAINT "launcher_user_username_key" UNIQUE ("username");
ALTER TABLE "public"."launcher_user" ADD CONSTRAINT "launcher_user_email_key" UNIQUE ("email");

-- ----------------------------
-- Primary Key structure for table launcher_user
-- ----------------------------
ALTER TABLE "public"."launcher_user" ADD CONSTRAINT "launcher_user_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Indexes structure for table launcher_version
-- ----------------------------
CREATE UNIQUE INDEX "idx_launcher_version_current" ON "public"."launcher_version" USING btree (
  "is_current" "pg_catalog"."bool_ops" ASC NULLS LAST
) WHERE is_current = true;
CREATE INDEX "idx_version_current" ON "public"."launcher_version" USING btree (
  "is_current" "pg_catalog"."bool_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table launcher_version
-- ----------------------------
ALTER TABLE "public"."launcher_version" ADD CONSTRAINT "launcher_version_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Foreign Keys structure for table launcher_game_file
-- ----------------------------
ALTER TABLE "public"."launcher_game_file" ADD CONSTRAINT "launcher_game_file_version_id_fkey" FOREIGN KEY ("version_id") REFERENCES "public"."launcher_game_version" ("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- ----------------------------
-- Foreign Keys structure for table launcher_game_version
-- ----------------------------
ALTER TABLE "public"."launcher_game_version" ADD CONSTRAINT "launcher_game_version_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."launcher_user" ("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- ----------------------------
-- Foreign Keys structure for table launcher_news_message
-- ----------------------------
ALTER TABLE "public"."launcher_news_message" ADD CONSTRAINT "launcher_news_message_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."launcher_user" ("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- ----------------------------
-- Foreign Keys structure for table launcher_server_settings
-- ----------------------------
ALTER TABLE "public"."launcher_server_settings" ADD CONSTRAINT "launcher_server_settings_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "public"."launcher_user" ("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- ----------------------------
-- Foreign Keys structure for table launcher_update_package
-- ----------------------------
ALTER TABLE "public"."launcher_update_package" ADD CONSTRAINT "launcher_update_package_uploaded_by_fkey" FOREIGN KEY ("uploaded_by") REFERENCES "public"."launcher_user" ("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "public"."launcher_update_package" ADD CONSTRAINT "launcher_update_package_version_id_fkey" FOREIGN KEY ("version_id") REFERENCES "public"."launcher_game_version" ("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- ----------------------------
-- Foreign Keys structure for table launcher_version
-- ----------------------------
ALTER TABLE "public"."launcher_version" ADD CONSTRAINT "launcher_version_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."launcher_user" ("id") ON DELETE SET NULL ON UPDATE CASCADE;
