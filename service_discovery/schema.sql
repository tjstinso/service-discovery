DROP TABLE IF EXISTS registry;

CREATE TABLE registry (
  address TEXT PRIMARY KEY NOT NULL,
  app_name TEXT NOT NULL,
  last_update INT NOT NULL
);
