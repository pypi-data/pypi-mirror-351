ALTER TABLE cfiledata ADD COLUMN order_priority INT NOT NULL DEFAULT 100 AFTER blake2shash;
ALTER TABLE cfiledata ADD COLUMN visibility INT NOT NULL DEFAULT 1 AFTER blake2shash;
