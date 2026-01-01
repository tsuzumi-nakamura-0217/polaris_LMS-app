# User（統合ユーザーテーブル）
|      | id  | user_name   | password | user_type   | full_name   | grade | is_active | created_at | updated_at |
| ---- | --- | ----------- | -------- | ----------- | ----------- | ----- | --------- | ---------- | ---------- |
| 制約   | 必須  | 必須・ユニーク    | 必須       | 必須          | 必須          |       | 必須        |            |            |
| データ型 | INT | VARCHAR(50) | CHAR(64) | VARCHAR(20) | VARCHAR(50) | INT   | BOOL      | DATETIME   | DATETIME   |
| 主キー  | ○   |             |          |             |             |       |           |            |            |
| 外部キー |     |             |          |             |             |       |           |            |            |
| 備考   |     | ログイン用ID     | ハッシュ化    | student/guardian/staff/administrator | 表示名         | 生徒の場合のみ | デフォルトTrue |            |            |

# Guardian_Student（保護者-生徒 関係テーブル）
|      | id  | guardian_id | student_id | relation    | created_at |
| ---- | --- | ----------- | ---------- | ----------- | ---------- |
| 制約   | 必須  | 必須          | 必須         |             |            |
| データ型 | INT | INT         | INT        | VARCHAR(20) | DATETIME   |
| 主キー  | ○   |             |            |             |            |
| 外部キー |     | User        | User       |             |            |
| 備考   |     |             |            | 父・母・祖父母など  |            |

# Staff_Student（スタッフ-生徒 担当関係テーブル）
|      | id  | staff_id | student_id | assigned_at | is_active |
| ---- | --- | -------- | ---------- | ----------- | --------- |
| 制約   | 必須  | 必須       | 必須         |             | 必須        |
| データ型 | INT | INT      | INT        | DATETIME    | BOOL      |
| 主キー  | ○   |          |            |             |           |
| 外部キー |     | User     | User       |             |           |
| 備考   |     |          |            | 担当開始日       | 担当中かどうか   |
# Subject（科目マスター）
|      | id  | subject_name | display_order | is_active | created_at |
| ---- | --- | ------------ | ------------- | --------- | ---------- |
| 制約   | 必須  | 必須           |               | 必須        |            |
| データ型 | INT | VARCHAR(50)  | INT           | BOOL      | DATETIME   |
| 主キー  | ○   |              |               |           |            |
| 外部キー |     |              |               |           |            |
| 備考   |     | 例：数学、国語、英語   | 表示順序          | 使用可能かどうか  |            |

# Problem_Category（問題カテゴリマスター）
|      | id  | subject_id | title       | grade | display_order | is_active |
| ---- | --- | ---------- | ----------- | ----- | ------------- | --------- |
| 制約   | 必須  | 必須         | 必須          | 必須    |               | 必須        |
| データ型 | INT | INT        | VARCHAR(50) | INT   | INT           | BOOL      |
| 主キー  | ○   |            |             |       |               |           |
| 外部キー |     | Subject    |             |       |               |           |
| 備考   |     |            | 例：分数の計算     |       | 表示順序          | 使用可能かどうか  |

# Problem
|      | id  | category_id | problem      | answer       | difficulty | display_order | is_active | created_at |
| ---- | --- | ----------- | ------------ | ------------ | ---------- | ------------- | --------- | ---------- |
| 制約   | 必須  | 必須          | 必須           | 必須           |            |               | 必須        |            |
| データ型 | INT | INT         | VARCHAR(500) | VARCHAR(200) | INT        | INT           | BOOL      | DATETIME   |
| 主キー  | ○   |             |              |              |            |               |           |            |
| 外部キー |     | Problem_Category |              |              |            |               |           |            |
| 備考   |     |             | 問題文          | 正解           | 難易度1-5     | 表示順序          | 使用可能かどうか  |            |

# Schedule
|      | id  | student_id | problem_id | status_id | scheduled_date | created_at | updated_at | memo         |
| ---- | --- | ---------- | ---------- | --------- | -------------- | ---------- | ---------- | ------------ |
| 制約   | 必須  | 必須         | 必須         | 必須        | 必須             |            |            |              |
| データ型 | INT | INT        | INT        | INT       | DATE           | DATETIME   | DATETIME   | VARCHAR(200) |
| 主キー  | ○   |            |            |           |                |            |            |              |
| 外部キー |     | User       | Problem    | Status    |                |            |            |              |
| 備考   |     |            |            |           | この日に解く予定       |            |            | メモ欄          |
# Status（ステータスマスター）
|      | id  | status      | display_order |
| ---- | --- | ----------- | ------------- |
| 制約   | 必須  | 必須          |               |
| データ型 | INT | VARCHAR(30) | INT           |
| 主キー  | ○   |             |               |
| 外部キー |     |             |               |
| 備考   |     | 未着手・進行中・完了  | 表示順序          |
# History
|      | id  | problem_id | student_id | level | started_at | finished_at | duration_seconds | is_correct | created_at |
| ---- | --- | ---------- | ---------- | ----- | ---------- | ----------- | ---------------- | ---------- | ---------- |
| 制約   | 必須  | 必須         | 必須         | 必須    | 必須         |             |                  |            |            |
| データ型 | INT | INT        | INT        | INT   | DATETIME   | DATETIME    | INT              | BOOL       | DATETIME   |
| 主キー  | ○   |            |            |       |            |             |                  |            |            |
| 外部キー |     | Problem    | User       |       |            |             |                  |            |            |
| 備考   |     |            |            | 理解度1-5 | 解答開始時刻     | 解答終了時刻      | 所要時間（秒）        | 正解したかどうか   | 戻るを押した場合はNULL |
# Information（お知らせ）
|      | id  | title        | detail        | important | target_type         | created_by | published_at | is_published | created_at | updated_at |
| ---- | --- | ------------ | ------------- | --------- | ------------------- | ---------- | ------------ | ------------ | ---------- | ---------- |
| 制約   | 必須  | 必須           | 必須            |           |                     |            |              | 必須           |            |            |
| データ型 | INT | VARCHAR(100) | VARCHAR(1000) | BOOL      | VARCHAR(20)         | INT        | DATETIME     | BOOL         | DATETIME   | DATETIME   |
| 主キー  | ○   |              |               |           |                     |            |              |              |            |            |
| 外部キー |     |              |               |           |                     | User       |              |              |            |            |
| 備考   |     |              |               | 重要フラグ     | all/grade/user_type | 作成者        | 公開日時         | 公開中かどうか      |            |            |
# Question（アンケート質問マスター）
|      | id  | question_text | question_type | display_order | is_active | created_at |
| ---- | --- | ------------- | ------------- | ------------- | --------- | ---------- |
| 制約   | 必須  | 必須            |               |               | 必須        |            |
| データ型 | INT | VARCHAR(200)  | VARCHAR(20)   | INT           | BOOL      | DATETIME   |
| 主キー  | ○   |               |               |               |           |            |
| 外部キー |     |               |               |               |           |            |
| 備考   |     | 質問文           | likert等       | 表示順序          | 使用可能かどうか  |            |
# Questionnaire（アンケート回答）
|      | id  | student_id | question_id | answer   | answered_at |
| ---- | --- | ---------- | ----------- | -------- | ----------- |
| 制約   | 必須  | 必須         | 必須          | 必須       | 必須          |
| データ型 | INT | INT        | INT         | INT      | DATETIME    |
| 主キー  | ○   |            |             |          |             |
| 外部キー |     | User       | Question    |          |             |
| 備考   |     |            |             | リッカート1-5 | 回答日時        |