-- Bảng thông tin platform (PHẢI TẠO TRƯỚC)
CREATE TABLE IF NOT EXISTS platforms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,                   -- Tên platform (LQDOJ, CodeMath, etc.)
    url TEXT,                                          -- URL gốc của platform (https://lqdoj.edu.vn, https://laptrinh.codemath.vn, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- Thời gian khởi tạo
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- Thời gian cập nhật cuối
    del_flag BOOLEAN DEFAULT 0                          -- Trạng thái xóa (0: Chưa xóa, 1: Đã xóa)
);

-- Insert dữ liệu platforms trước
INSERT OR IGNORE INTO platforms (name, url) VALUES ('CodeMath', 'https://laptrinh.codemath.vn');
INSERT OR IGNORE INTO platforms (name, url) VALUES ('LQDOJ', 'https://lqdoj.edu.vn');

-- Bảng chính lưu thông tin bài toán
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_code VARCHAR(50) NOT NULL,                  -- Mã bài toán (tt25candy)
    problem_name TEXT NOT NULL,                         -- Tên bài toán (Thích kẹo ngọt)
    platform INT NOT NULL,                              -- ID Nền tảng
    problem_url TEXT,                                   -- URL chi tiết bài toán
    category VARCHAR(20),                               -- Danh mục (ABC, etc.)
    difficulty INT DEFAULT 1,                           -- Độ khó (1: Easy, 2: Medium, 3: Hard)
    points INTEGER,                                     -- Điểm số
    ac_rate DECIMAL(5,2),                               -- Tỷ lệ AC (17.00)
    users_solved INTEGER,                               -- Số người đã giải
    solved_status INT DEFAULT -1,                       -- Trạng thái đã giải (-1: Unsolved, 0: N/A, 1: Solved)
    submission_count INTEGER DEFAULT 0,                 -- Số lần nạp bài
    best_submission_id INTEGER,                         -- ID submission tốt nhất
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- Thời gian khởi tạo
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- Thời gian cập nhật cuối
    del_flag BOOLEAN DEFAULT 0,                         -- Trạng thái xóa (0: Chưa xóa, 1: Đã xóa)
    notes TEXT,                                          -- Ghi chú bổ sung
    FOREIGN KEY (platform) REFERENCES platforms(id) ON DELETE CASCADE,
    UNIQUE(problem_code, platform)                      -- Unique constraint trên cả problem_code và platform
);

-- Bảng lưu thông tin submission
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL,                        -- FK đến problems
    submission_code TEXT,                               -- Code đáp án
    language VARCHAR(20) DEFAULT 'Python',              -- Ngôn ngữ lập trình
    status VARCHAR(20),                                 -- Trạng thái (AC, WA, TLE, etc.)
    execution_time INTEGER,                             -- Thời gian thực thi (ms)
    memory_used INTEGER,                                -- Bộ nhớ sử dụng (KB)
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- Thời gian nạp
    is_best BOOLEAN DEFAULT 0,                          -- Có phải submission tốt nhất
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
);

-- Bảng lưu thông tin tag/category
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,                   -- Tên tag
    description TEXT,                                   -- Mô tả tag
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng quan hệ many-to-many giữa problems và tags
CREATE TABLE IF NOT EXISTS problem_tags (
    problem_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (problem_id, tag_id),
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Bảng lưu thông tin giải thích/solution
CREATE TABLE IF NOT EXISTS solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL,                        -- FK đến problems
    solution_type VARCHAR(20) DEFAULT 'Explanation',    -- Loại (Explanation, Hint, Full Solution)
    content TEXT,                                       -- Nội dung giải thích
    language VARCHAR(10) DEFAULT 'Vietnamese',          -- Ngôn ngữ giải thích
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE
);

-- Indexes để tối ưu performance
CREATE INDEX IF NOT EXISTS idx_problems_code_platform ON problems(problem_code, platform);
CREATE INDEX IF NOT EXISTS idx_problems_code ON problems(problem_code);
CREATE INDEX IF NOT EXISTS idx_problems_category ON problems(category);
CREATE INDEX IF NOT EXISTS idx_problems_difficulty ON problems(difficulty);
CREATE INDEX IF NOT EXISTS idx_problems_solved_status ON problems(solved_status);
CREATE INDEX IF NOT EXISTS idx_problems_created_at ON problems(created_at);
CREATE INDEX IF NOT EXISTS idx_submissions_problem_id ON submissions(problem_id);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_submitted_at ON submissions(submitted_at);
CREATE INDEX IF NOT EXISTS idx_solutions_problem_id ON solutions(problem_id);

-- Triggers để tự động cập nhật updated_at
CREATE TRIGGER IF NOT EXISTS update_problems_updated_at
    AFTER UPDATE ON problems
    FOR EACH ROW
    BEGIN
        UPDATE problems SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_solutions_updated_at
    AFTER UPDATE ON solutions
    FOR EACH ROW
    BEGIN
        UPDATE solutions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Trigger để cập nhật submission_count trong problems
CREATE TRIGGER IF NOT EXISTS update_problem_submission_count
    AFTER INSERT ON submissions
    FOR EACH ROW
    BEGIN
        UPDATE problems
        SET submission_count = (
            SELECT COUNT(*) FROM submissions WHERE problem_id = NEW.problem_id
        )
        WHERE id = NEW.problem_id;
    END;

-- Trigger để cập nhật best_submission_id
CREATE TRIGGER IF NOT EXISTS update_best_submission
    AFTER INSERT ON submissions
    FOR EACH ROW
    WHEN NEW.is_best = 1
    BEGIN
        UPDATE problems
        SET best_submission_id = NEW.id
        WHERE id = NEW.problem_id;
    END;
