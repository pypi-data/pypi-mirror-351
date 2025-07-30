DROP TABLE IF EXISTS cchangelog;
CREATE TABLE cchangelog (
    id INT NOT NULL AUTO_INCREMENT,
    entity_type VARCHAR(64),
    entity_id INT NOT NULL,
    user_id INT,
    action VARCHAR(64),
    insdate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    new_values JSON,
    PRIMARY KEY(id)
);
