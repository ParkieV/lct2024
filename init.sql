\c lct_postgres

CREATE EXTENSION pgcrypto;

CREATE TABLE "users" (
  "id" uuid DEFAULT gen_random_uuid(),
  "email" varchar(255),
  "password" varchar(100),
  "first_name" varchar(50),
  "middle_name" varchar(50),
  "last_name" varchar(50),
  "telegram_nickname" varchar(100),
  "phone" varchar(12),
  "work_org_id" uuid DEFAULT (NULL),
  "position" varchar(100),
  "rights" varchar(100),
  PRIMARY KEY ("id")
);

CREATE TABLE "organization" (
  "id" uuid DEFAULT gen_random_uuid(),
  "name" varchar(150),
  PRIMARY KEY ("id")
);

CREATE TABLE "balance" (
  "id" uuid DEFAULT gen_random_uuid(),
  "name" varchar(150),
  "amount" numeric(14, 2),
  "user_id" uuid,
  PRIMARY KEY ("id")
);

CREATE TABLE "purchase" (
  "id_pk" uuid DEFAULT gen_random_uuid(),
  "id" varchar(50),
  "user_id" uuid,
  "lotEntityId" varchar(40),
  "customerId" varchar(40),
  PRIMARY KEY ("id_pk")
);


CREATE TABLE "purchase_position" (
  "id" uuid DEFAULT gen_random_uuid(),
  "purchase_id" uuid,
  "DeliverySchedule__dates__end_date" varchar(50),
  "DeliverySchedule__dates__start_date" varchar(50),
  "DeliverySchedule__deliveryAmount" numeric(14, 2),
  "DeliverySchedule__deliveryConditions" varchar(50),
  "DeliverySchedule__year" integer,
  "address__gar_id" varchar(50),
  "address__text" varchar(300),
  "entityId" varchar(50),
  "spgz_id" varchar(50),
  "nmc" numeric(14, 2),
  "okei_code" varchar(50),
  "purchaseAmount" numeric(14, 2),
  "spgzCharacteristics__characteristicName" varchar(50),
  "spgzCharacteristics__characteristicEnums__value" varchar(50),
  "spgzCharacteristics__conditionTypeId" varchar(50),
  "spgzCharacteristics__kpgzCharacteristicId" varchar(50),
  "spgzCharacteristics__okei_id" varchar(50),
  "spgzCharacteristics__selectType" varchar(50),
  "spgzCharacteristics__typeId" varchar(50),
  "spgzCharacteristics__value1" varchar(50),
  "spgzCharacteristics__value2" varchar(50),
  PRIMARY KEY ("id")
);

ALTER TABLE "users" ADD FOREIGN KEY ("work_org_id") REFERENCES "organization" ("id");

ALTER TABLE "balance" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "balance" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "purchase" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id");

ALTER TABLE "purchase_position" ADD FOREIGN KEY ("purchase_id") REFERENCES "purchase" ("id_pk");
