CREATE TABLE block
(
  cid VARCHAR(255) NOT NULL,
  miner VARCHAR(255) NOT NULL,
  parent_weight BIGINT NOT NULL,
  parent_stateroot VARCHAR(255) NOT NULL,
  height INT NOT NULL,
  parent_message_recipt VARCHAR(255) NOT NULL,
  messages VARCHAR(255) NOT NULL,
  timestamp DATE NOT NULL,
  PRIMARY KEY (cid)
);

CREATE TABLE block_messages
(
  messages_cid VARCHAR(255) NOT NULL,
  to_miner VARCHAR(255) NOT NULL,
  from_miner VARCHAR(255) NOT NULL,
  nonc VARCHAR(255) NOT NULL,
  value INT NOT NULL,
  gas INT NULL,
  cid VARCHAR(255) NOT NULL,
  FOREIGN KEY (cid) REFERENCES block(cid)
);

CREATE TABLE tipset
(
  cid VARCHAR(255) NOT NULL,
  miner VARCHAR(255) NOT NULL,
  height INT NOT NULL,
  parent_weight BIGINT NOT NULL,
  messages VARCHAR(255) NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  PRIMARY KEY (cid)
);

CREATE TABLE cid_parents
(
  cid VARCHAR(255) NOT NULL,
  cid_parent INT NOT NULL,
  PRIMARY KEY (cid),
  FOREIGN KEY (cid) REFERENCES block(cid)
);