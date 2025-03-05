CREATE TABLE space_type (
    id INT,
    name VARCHAR,

    CONSTRAINT space_type_pk PRIMARY KEY (id)
);

CREATE TABLE event_type (
    id INT,
    name VARCHAR,

    CONSTRAINT event_type_pk PRIMARY KEY (id)
);

CREATE TABLE logs (
    id INT,
    datetime TIMESTAMP,
    user_id INT,
    space_type_id INT,
    event_type_id INT,
    target_id INT,

    CONSTRAINT logs_pk PRIMARY KEY (id),
    CONSTRAINT logs_space_type_fk FOREIGN KEY (space_type_id) REFERENCES space_type,
    CONSTRAINT logs_event_type_fk FOREIGN KEY (event_type_id) REFERENCES event_type
);