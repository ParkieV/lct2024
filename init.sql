\c lct_postgres

CREATE TABLE "users" (
  "id" uuid,
  "email" varchar(255),
  "password" varchar(100),
  "first_name" varchar(50),
  "middle_name" varchar(50),
  "last_name" varchar(50),
  "telegram_nickname" varchar(100),
  "phone" varchar(12),
  "work_org_id" uuid DEFAULT (NULL),
  "position_id" uuid DEFAULT (NULL)
);

CREATE TABLE "organization" (
  "id" uuid,
  "name" varchar(150)
);

CREATE TABLE "work_position" (
  "id" uuid,
  "name" varchar(150),
  "work_org_id" uuid DEFAULT (NULL)
);

CREATE TABLE "system_right" (
  "id" uuid,
  "name" varchar(150)
);

CREATE TABLE user_right_association (
    user_id UUID NOT NULL,
    right_id UUID NOT NULL,
    PRIMARY KEY (user_id, right_id)
);

ALTER TABLE "user" ADD FOREIGN KEY ("work_org_id") REFERENCES "organization" ("id");

ALTER TABLE "user" ADD FOREIGN KEY ("position_id") REFERENCES "work_position" ("id");

ALTER TABLE "work_position" ADD FOREIGN KEY ("work_org_id") REFERENCES "organization" ("id");

ALTER TABLE "user_right_association" ADD PRIMARY KEY("user_id", "right_id");

ALTER TABLE "user_right_association" ADD FOREIGN KEY("user_id") REFERENCES "user" ("id");

ALTER TABLE "user_right_association" ADD FOREIGN KEY("right_id") REFERENCES "system_right" ("id");
