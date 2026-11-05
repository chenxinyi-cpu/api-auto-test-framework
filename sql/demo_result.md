**Schema (MySQL v8)**

    -- 建表
    CREATE TABLE user (
        id INT PRIMARY KEY,
        username VARCHAR(50),
        password VARCHAR(100),
        status TINYINT  -- 1正常，0禁用
    );
    
    CREATE TABLE user_info (
        user_id INT PRIMARY KEY,
        email VARCHAR(100),
        phone VARCHAR(20)
    );
    
    -- 插入测试数据
    INSERT INTO user VALUES (1, 'alice', '123456', 1);
    INSERT INTO user VALUES (2, 'bob', 'abcdef', 1);
    INSERT INTO user VALUES (3, 'charlie', 'pass', 0);
    
    INSERT INTO user_info VALUES (1, 'alice@test.com', '13800000001');
    INSERT INTO user_info VALUES (2, 'bob@test.com', '13800000002');

---

**Query #1**

    -- 查询1：状态正常的用户
    SELECT * FROM user WHERE status = 1;

| id  | username | password | status |
| --- | -------- | -------- | ------ |
| 1   | alice    | 123456   | 1      |
| 2   | bob      | abcdef   | 1      |

---
**Query #2**

    -- 查询2：用户名包含 a 的用户
    SELECT * FROM user WHERE username LIKE '%a%';

| id  | username | password | status |
| --- | -------- | -------- | ------ |
| 1   | alice    | 123456   | 1      |
| 3   | charlie  | pass     | 0      |

---
**Query #3**

    -- 查询3：密码长度 >= 6 的用户
    SELECT * FROM user WHERE LENGTH(password) >= 6;

| id  | username | password | status |
| --- | -------- | -------- | ------ |
| 1   | alice    | 123456   | 1      |
| 2   | bob      | abcdef   | 1      |

---
**Query #4**

    -- 查询4：状态正常且用户名以 a 开头
    SELECT * FROM user WHERE status = 1 AND username LIKE 'a%';

| id  | username | password | status |
| --- | -------- | -------- | ------ |
| 1   | alice    | 123456   | 1      |

---
**Query #5**

    -- 查询5：联表查询用户和邮箱
    SELECT u.id, u.username, ui.email
    FROM user u
    INNER JOIN user_info ui ON u.id = ui.user_id;

| id  | username | email          |
| --- | -------- | -------------- |
| 1   | alice    | alice@test.com |
| 2   | bob      | bob@test.com   |

---

[View on DB Fiddle](https://www.db-fiddle.com/)