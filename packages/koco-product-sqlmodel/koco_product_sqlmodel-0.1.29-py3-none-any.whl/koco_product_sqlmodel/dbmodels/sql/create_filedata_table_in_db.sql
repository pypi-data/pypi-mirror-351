DROP TABLE IF EXISTS cfiledata;
CREATE TABLE cfiledata (
    id INT NOT NULL AUTO_INCREMENT,
    entity_type VARCHAR(64),
    entity_id INT NOT NULL,
    documenttype VARCHAR(64),
    description_json JSON,
    oldfilename VARCHAR(1024),
    mimetype VARCHAR(256),
    blake2shash VARCHAR(64),
    user_id INT,
    insdate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    upddate timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY(id)
);

