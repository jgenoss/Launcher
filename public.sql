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

 Date: 29/05/2025 12:48:14
*/


-- ----------------------------
-- Table structure for launcher_ban
-- ----------------------------
DROP TABLE IF EXISTS "public"."launcher_ban";
CREATE TABLE "public"."launcher_ban" (
  "id" int4 NOT NULL DEFAULT nextval('launcher_ban_hwid_id_seq'::regclass),
  "hwid" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "serial_number" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "reason" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "mac_address" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "is_banned" bool NOT NULL DEFAULT false,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;
COMMENT ON TABLE "public"."launcher_ban" IS 'HWIDs baneados del launcher';

-- ----------------------------
-- Records of launcher_ban
-- ----------------------------
INSERT INTO "public"."launcher_ban" VALUES (1, '0AE8DE75850D92FF5F877522F16FBA538E71AFB653E049E35A34144B72FD7D05', '2L082LANS6JT', 'None', '0250EC5321A4', 'f', '2025-05-28 20:09:55.456767');

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
-- Records of launcher_download_log
-- ----------------------------
INSERT INTO "public"."launcher_download_log" VALUES (1, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 'banner.html', 'banner', 't', '2025-05-28 20:16:31.028748');
INSERT INTO "public"."launcher_download_log" VALUES (2, '127.0.0.1', 'GameLauncher/1.0', 'update.json', 'update_check', 't', '2025-05-28 20:17:22.394018');
INSERT INTO "public"."launcher_download_log" VALUES (3, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 'banner.html', 'banner', 't', '2025-05-28 20:20:15.482372');
INSERT INTO "public"."launcher_download_log" VALUES (4, '127.0.0.1', 'GameLauncher/1.0', 'update', 'update_check', 't', '2025-05-28 20:20:21.332369');
INSERT INTO "public"."launcher_download_log" VALUES (5, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 'banner.html', 'banner', 't', '2025-05-28 20:21:33.513599');
INSERT INTO "public"."launcher_download_log" VALUES (6, '127.0.0.1', 'GameLauncher/1.0', 'update', 'update_check', 't', '2025-05-28 20:21:34.432414');
INSERT INTO "public"."launcher_download_log" VALUES (7, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 'launcher_update', 'launcher_check', 't', '2025-05-28 20:24:04.050196');
INSERT INTO "public"."launcher_download_log" VALUES (8, '127.0.0.1', '', 'launcher_update', 'launcher_check', 't', '2025-05-28 20:24:20.777958');
INSERT INTO "public"."launcher_download_log" VALUES (9, '127.0.0.1', 'GameLauncher/1.0', 'update', 'update_check', 't', '2025-05-28 20:24:20.814641');
INSERT INTO "public"."launcher_download_log" VALUES (10, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 'banner.html', 'banner', 't', '2025-05-28 20:24:21.138359');
INSERT INTO "public"."launcher_download_log" VALUES (11, '127.0.0.1', '', 'launcher_update', 'launcher_check', 't', '2025-05-28 20:31:57.244654');
INSERT INTO "public"."launcher_download_log" VALUES (12, '127.0.0.1', 'GameLauncher/1.0', 'update', 'update_check', 't', '2025-05-28 20:31:57.326186');
INSERT INTO "public"."launcher_download_log" VALUES (13, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 'banner.html', 'banner', 't', '2025-05-28 20:31:57.591091');
INSERT INTO "public"."launcher_download_log" VALUES (14, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 'launcher_update', 'launcher_check', 't', '2025-05-29 01:27:58.864266');
INSERT INTO "public"."launcher_download_log" VALUES (15, '127.0.0.1', '', 'launcher_update', 'launcher_check', 't', '2025-05-29 01:35:16.284217');
INSERT INTO "public"."launcher_download_log" VALUES (16, '127.0.0.1', 'GameLauncher/1.0', 'update', 'update_check', 't', '2025-05-29 01:35:16.391231');
INSERT INTO "public"."launcher_download_log" VALUES (17, '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36', 'banner.html', 'banner', 't', '2025-05-29 01:35:16.714476');

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
-- Records of launcher_game_file
-- ----------------------------

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
-- Records of launcher_game_version
-- ----------------------------
INSERT INTO "public"."launcher_game_version" VALUES (4, '1.0.0.0', 't', '', '2025-05-28 19:51:28.815911', 1);

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
-- Records of launcher_news_message
-- ----------------------------
INSERT INTO "public"."launcher_news_message" VALUES (1, 'Actualización', 'Nueva versión disponible con mejoras de rendimiento y corrección de errores. ¡Actualiza ahora para obtener la mejor experiencia de juego!', 't', 5, '2025-05-29 01:30:45.101823', 1);

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
-- Records of launcher_server_settings
-- ----------------------------
INSERT INTO "public"."launcher_server_settings" VALUES (1, 'maintenance_mode', 'false', 'Modo de mantenimiento', '2025-05-28 19:42:09.792872', NULL);
INSERT INTO "public"."launcher_server_settings" VALUES (2, 'allow_registration', 'false', 'Permitir registro de usuarios', '2025-05-28 19:42:09.792876', NULL);
INSERT INTO "public"."launcher_server_settings" VALUES (3, 'max_file_size', '524288000', 'Tamaño máximo de archivo en bytes', '2025-05-28 19:42:09.792878', NULL);
INSERT INTO "public"."launcher_server_settings" VALUES (4, 'launcher_update_check_interval', '300', 'Intervalo de verificación de actualización del launcher (segundos)', '2025-05-28 19:42:09.792879', NULL);
INSERT INTO "public"."launcher_server_settings" VALUES (5, 'auto_backup_enabled', 'true', 'Backup automático habilitado', '2025-05-28 19:42:09.792881', NULL);
INSERT INTO "public"."launcher_server_settings" VALUES (6, 'log_retention_days', '30', 'Días de retención de logs', '2025-05-28 19:42:09.792882', NULL);

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
-- Records of launcher_update_package
-- ----------------------------

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
-- Records of launcher_user
-- ----------------------------
INSERT INTO "public"."launcher_user" VALUES (1, 'azpirin4', 'granadillo33@gmail.com', 'scrypt:32768:8:1$tODmpVxkXtLLKfc0$fd7b9ccb464e7e75018f679fea8e1529ca709f418e9acc2a6bd1659b251039bf01a27d03851cb3436da53f5f19a71e2335bce6c12d7ce734219841d92aa8b227', 't', '2025-05-28 19:42:09.795977', NULL);

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
-- Records of launcher_version
-- ----------------------------
INSERT INTO "public"."launcher_version" VALUES (1, '1.0.0.0', 'PBLauncher.exe', 'static/downloads\PBLauncher.exe', 't', '', '2025-05-28 20:23:43.187944', 1);

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
ALTER TABLE "public"."launcher_game_version" ADD CONSTRAINT "chk_version_format" CHECK (version::text ~ '^[0-9]+(\.[0-9]+){1,3}$'::text);

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
