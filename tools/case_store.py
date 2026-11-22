import os
import sqlite3
from datetime import datetime

DB_PATH = "data/test_platform.db"

class CaseStore:
    def __init__(self,db_path:str=DB_PATH):
        os.makedirs(os.path.dirname(db_path),exist_ok=True)
        #  连接数据库（如果文件不存在，会自动创建）
        self.conn = sqlite3.connect(db_path)
        # 让查询结果可以按列名访问，比如 r["case_id"] 而不是 r[0]
        self.conn.row_factory = sqlite3.Row
        #  初始化建表
        self._create_tables()

    def _create_tables(self):
        """建表语句：翻译自 platform_data_notes.md"""
        self.conn.executescript("""
                                CREATE TABLE IF NOT EXISTS case_info
                                (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    case_id TEXT UNIQUE NOT NULL,
                                    title TEXT NOT NULL,
                                    module TEXT,
                                    priority TEXT DEFAULT 'P1',
                                    precondition TEXT,
                                    steps TEXT,
                                    expected TEXT,
                                    yaml_path TEXT,
                                    enabled INTEGER DEFAULT 1,
                                    created_at TEXT
                                );

                                CREATE TABLE IF NOT EXISTS case_set
                                (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    set_name TEXT UNIQUE NOT NULL,
                                    description TEXT
                                );

                                CREATE TABLE IF NOT EXISTS case_set_mapping
                                (
                                    set_id INTEGER,
                                    case_info_id INTEGER,
                                    PRIMARY KEY (set_id, case_info_id)
                                );

                                CREATE TABLE IF NOT EXISTS execution
                                (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    set_id INTEGER,
                                    env TEXT,
                                    started_at TEXT,
                                    finished_at TEXT,
                                    total INTEGER DEFAULT 0,
                                    passed INTEGER DEFAULT 0,
                                    failed INTEGER DEFAULT 0
                                );

                                CREATE TABLE IF NOT EXISTS execution_detail
                                (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    execution_id INTEGER,
                                    case_info_id INTEGER,
                                    case_id TEXT,
                                    status TEXT,
                                    error_msg TEXT,
                                    duration_ms INTEGER
                                );
        """)
        self.conn.commit()

    def add_case(self, case_id: str, title: str, module: str = "",
                 priority: str = "P1", yaml_path: str = "") -> int:
        """写入一条用例（模拟从 yaml 同步过来）"""
        cur = self.conn.execute(
            "INSERT INTO case_info (case_id, title, module, priority, yaml_path, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (case_id, title, module, priority, yaml_path, datetime.now().isoformat()),
        )
        self.conn.commit()
        return cur.lastrowid

    def add_case_set(self, set_name: str, description: str = "") -> int:
        """新建一个用例集"""
        cur = self.conn.execute(
            "INSERT INTO case_set (set_name, description) VALUES (?, ?)",
            (set_name, description),
        )
        self.conn.commit()
        return cur.lastrowid

    def add_case_to_set(self, set_name: str, case_id: str):
        """把用例加入某个集合"""
        set_row = self.conn.execute(
            "SELECT id FROM case_set WHERE set_name = ?", (set_name,)
        ).fetchone()
        case_row = self.conn.execute(
            "SELECT id FROM case_info WHERE case_id = ?", (case_id,)
        ).fetchone()

        if not set_row or not case_row:
            raise ValueError(f"集合或用例不存在: {set_name}, {case_id}")

        self.conn.execute(
            "INSERT OR IGNORE INTO case_set_mapping (set_id, case_info_id) VALUES (?, ?)",
            (set_row["id"], case_row["id"]),
        )
        self.conn.commit()

    def list_cases(self, module: str = None, priority: str = None):
        """按条件查询用例（体验数据库的动态查询优势）"""
        sql = "SELECT * FROM case_info WHERE 1=1"
        params = []
        if module:
            sql += " AND module = ?"
            params.append(module)
        if priority:
            sql += " AND priority = ?"
            params.append(priority)
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def start_execution(self, set_name: str, env: str) -> int:
        """开始一次执行，生成一条执行记录，返回执行ID"""
        set_row = self.conn.execute(
            "SELECT id FROM case_set WHERE set_name = ?", (set_name,)
        ).fetchone()
        if not set_row:
            raise ValueError(f"集合不存在: {set_name}")

        cur = self.conn.execute(
            "INSERT INTO execution (set_id, env, started_at) VALUES (?, ?, ?)",
            (set_row["id"], env, datetime.now().isoformat()),
        )
        self.conn.commit()
        return cur.lastrowid

    def record_detail(self, execution_id: int, case_id: str,
                      status: str, error_msg: str = "", duration_ms: int = 0):
        """记录一条用例的执行明细"""
        case_row = self.conn.execute(
            "SELECT id FROM case_info WHERE case_id = ?", (case_id,)
        ).fetchone()
        if not case_row:
            raise ValueError(f"用例不存在: {case_id}")

        self.conn.execute(
            "INSERT INTO execution_detail (execution_id, case_info_id, case_id, status, error_msg, duration_ms) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (execution_id, case_row["id"], case_id, status, error_msg, duration_ms),
        )
        self.conn.commit()

    def finish_execution(self, execution_id: int):
        """执行结束，从明细表汇总数据，回写总通过数/失败数"""
        rows = self.conn.execute(
            "SELECT status, COUNT(*) as cnt FROM execution_detail "
            "WHERE execution_id = ? GROUP BY status",
            (execution_id,),
        ).fetchall()

        stats = {r["status"]: r["cnt"] for r in rows}
        total = sum(stats.values())
        passed = stats.get("passed", 0)
        failed = stats.get("failed", 0)

        self.conn.execute(
            "UPDATE execution SET finished_at = ?, total = ?, passed = ?, failed = ? WHERE id = ?",
            (datetime.now().isoformat(), total, passed, failed, execution_id),
        )
        self.conn.commit()

    def query_failed_cases(self, set_name: str = None):
        """核心查询：查最近一次执行中失败的用例，支持三表 JOIN"""
        sql = """
              SELECT ci.case_id, ci.title, ci.module, ed.error_msg, e.finished_at
              FROM execution_detail ed
                       JOIN execution e ON ed.execution_id = e.id
                       JOIN case_info ci ON ed.case_info_id = ci.id
              WHERE ed.status = 'failed'
                AND e.id = (SELECT MAX(id) FROM execution) \
              """
        params = []
        if set_name:
            sql += " AND e.set_id = (SELECT id FROM case_set WHERE set_name = ?)"
            params.append(set_name)
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def close(self):
        """关闭数据库连接"""
        self.conn.close()

if __name__ == '__main__':
    # 0. 初始化数据库
    store = CaseStore()

    # 1. 建用例集
    store.add_case_set("smoke", "冒烟用例")
    store.add_case_set("full", "全量回归")

    # 2. 写入用例（模拟从yaml同步过来）
    store.add_case("login_001", "正确账号密码登录成功", "登录", "P0", "cases/login_case.yaml")
    store.add_case("login_002", "用户名为空", "登录", "P1", "cases/login_case.yaml")
    store.add_case("get_user_001", "查询存在的用户", "用户", "P0", "cases/get_user_case.yaml")

    # 3. 加入集合
    store.add_case_to_set("smoke", "login_001")
    store.add_case_to_set("smoke", "get_user_001")
    store.add_case_to_set("full", "login_001")
    store.add_case_to_set("full", "login_002")
    store.add_case_to_set("full", "get_user_001")

    # 4. 模拟一次执行
    print("=== 开始模拟执行 ===")
    exec_id = store.start_execution("smoke", "dev")
    store.record_detail(exec_id, "login_001", "passed", duration_ms=120)
    store.record_detail(exec_id, "get_user_001", "failed", error_msg="HTTP 401: token无效", duration_ms=80)
    store.finish_execution(exec_id)
    print(f"执行完成，执行ID: {exec_id}")

    # 5. 查询验证
    print("\n=== 所有P0用例 ===")
    for c in store.list_cases(priority="P0"):
        print(f"{c['case_id']} | {c['title']}")

    print("\n=== 最近一次执行失败的用例 ===")
    for c in store.query_failed_cases():
        print(f"{c['case_id']} | {c['module']} | {c['title']} | 失败原因: {c['error_msg']}")

    # 6. 关闭连接
    store.close()