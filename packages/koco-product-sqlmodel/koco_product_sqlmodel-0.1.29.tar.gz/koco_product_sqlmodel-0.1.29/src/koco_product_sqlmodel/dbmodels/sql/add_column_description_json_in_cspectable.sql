ALTER TABLE cspectable ADD COLUMN description_json LONGTEXT DEFAULT NULL AFTER user_id;
ALTER TABLE cspectable MODIFY description_json LONGTEXT CHECK(JSON_VALID(description_json));