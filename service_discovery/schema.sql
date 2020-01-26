DROP TABLE IF EXISTS registry;

CREATE TABLE registry (
  address TEXT PRIMARY KEY NOT NULL,
  app_name TEXT NOT NULL,
  last_update INT NOT NULL
);

INSERT INTO registry (address, app_name, last_update)
VALUES ("127.0.0.1:8000", "service-discovery", 0);
