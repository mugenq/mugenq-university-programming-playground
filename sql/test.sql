-- CREATE TABLE USERS (username TEXT NOT NULL PRIMARY KEY,
-- password TEXT NOT NULL, email TEXT NOT NULL);

-- primary key means we cant have two people with the same name

-- INSERT INTO users (username, password, email)
-- VALUES ("berg", "mypassdd", "berg@berr.u.com");


select * from users;

-- SELECT email FROM USERS
-- WHERE username = "mike"
-- AND password = "mypass";

select username from users
where email like "%@yahoo%";

-- update users set email ="notmike@gmail.com"
-- where username = "mike";

-- delete from users where username = "berg";