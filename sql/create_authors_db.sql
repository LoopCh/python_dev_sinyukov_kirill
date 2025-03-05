CREATE TABLE users (
    id INT,
    email VARCHAR,
    login VARCHAR,

    CONSTRAINT users_pk PRIMARY KEY (id)
);

CREATE TABLE blog (
    id INT,
    owner_id INT,
    name VARCHAR,
    description VARCHAR,

    CONSTRAINT blog_pk PRIMARY KEY (id),
    CONSTRAINT blog_users_fk FOREIGN KEY (owner_id) REFERENCES users (id)
);

CREATE TABLE post(
    id INT,
    header VARCHAR,
    text VARCHAR,
    author_id INT,
    blog_id INT,

    CONSTRAINT post_pk PRIMARY KEY (id),
    CONSTRAINT post_users_fk FOREIGN KEY (author_id) REFERENCES users (id),
    CONSTRAINT post_blog_fk FOREIGN KEY (blog_id) REFERENCES blog (id)
);