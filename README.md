# coding-interview

## 概要

`Category` の CRUD API を Django / Django REST Framework で実装しています。

`Category` は `Company` に紐づくため、動作確認用の `Company` fixture を同梱しています。

## 必要要件

- Python 3.11
- pipenv
- PostgreSQL

## 動作確認環境

DB 接続設定は `config/settings.py` の以下の環境変数を参照します。

| 環境変数 | デフォルト値 |
| --- | --- |
| `POSTGRES_DB` | `coding-test` |
| `POSTGRES_USER` | `root` |
| `POSTGRES_PASSWORD` | `password` |
| `DB_HOST_NAME` | `localhost` |
| `DB_PORT` | `5432` |

必要に応じて、事前に環境変数を設定してください。

```bash
export POSTGRES_DB=coding-test
export POSTGRES_USER=root
export POSTGRES_PASSWORD=password
export DB_HOST_NAME=localhost
export DB_PORT=5432
```

## セットアップ

依存関係の解決:

```bash
pipenv install
```

マイグレーションの適用:

```bash
pipenv run python manage.py makemigrations api
pipenv run python manage.py migrate
```

fixture の登録:

```bash
pipenv run python manage.py loaddata api/fixtures/companies.json
```

fixture ファイル:

- `api/fixtures/companies.json`
- 動作確認用 Company ID: `11111111-1111-1111-1111-111111111111`

## テスト実行

`manage.py test` はテスト用データベースを作成するため、`POSTGRES_USER` に `CREATEDB` 権限が必要です。

権限がない場合は、PostgreSQL の管理者ユーザーで以下を実行してください。

```sql
ALTER USER root CREATEDB;
```

全テストを実行する場合:

```bash
pipenv run python manage.py test
```

Category API のテストのみ実行する場合:

```bash
pipenv run python manage.py test api.tests.test_views
```

## サーバー起動

```bash
pipenv run python manage.py runserver
```

起動後は `http://127.0.0.1:8000/` でアクセスできます。

## API仕様

### エンドポイント一覧

| メソッド | パス | 説明 |
| --- | --- | --- |
| `GET` | `/api/categories/` | Category 一覧取得 |
| `POST` | `/api/categories/` | Category 作成 |
| `GET` | `/api/categories/<category_id>/` | Category 詳細取得 |
| `PATCH` | `/api/categories/<category_id>/` | Category 更新 |
| `DELETE` | `/api/categories/<category_id>/` | Category 削除 |

### リクエスト項目

`POST /api/categories/` および `PATCH /api/categories/<category_id>/` では、以下の項目を扱います。

| 項目 | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `company` | UUID | `POST` では必須、`PATCH` では変更不可 | 紐づく Company ID |
| `name` | string | 必須 | カテゴリ名 |
| `parent_category` | UUID または `null` | 任意 | 親カテゴリ ID。ルートカテゴリの場合は `null` |

### レスポンス項目

一覧取得・詳細取得・作成・更新では、以下の形式でレスポンスを返します。

| 項目 | 型 | 説明 |
| --- | --- | --- |
| `id` | UUID | Category ID |
| `company` | UUID | 紐づく Company ID |
| `name` | string | カテゴリ名 |
| `parent_category` | UUID または `null` | 親カテゴリ ID |
| `created_at` | datetime string | 作成日時 |
| `updated_at` | datetime string | 更新日時 |

レスポンス例:

```json
{
  "id": "8aa90e84-089b-4478-979b-fc4aa43da9a9",
  "company": "11111111-1111-1111-1111-111111111111",
  "name": "Books",
  "parent_category": null,
  "created_at": "2026-04-21T07:01:48.879395Z",
  "updated_at": "2026-04-21T07:01:48.879412Z"
}
```

### 現時点でのバリデーション・制約

- `name` は必須です
- `name` は 255 文字以下です
- 空文字および空白のみの `name` は受け付けません
- 同一 `company` 内で同名の `Category` は作成できません
- `parent_category` を指定する場合、同一 `company` の `Category` である必要があります
- 自分自身を `parent_category` に指定することはできません
- 循環参照となる親子関係は作成できません
- `PATCH` での `company` 更新は受け付けません
- 親カテゴリ削除時、子カテゴリの `parent_category` は `null` になります

## API 動作確認

### Category 一覧取得

```bash
curl http://127.0.0.1:8000/api/categories/
```

### Category 作成

```bash
curl -X POST http://127.0.0.1:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -d '{
    "company": "11111111-1111-1111-1111-111111111111",
    "name": "Books",
    "parent_category": null
  }'
```

### Category 詳細取得

作成済みの Category ID を指定して確認します。

```bash
curl http://127.0.0.1:8000/api/categories/<category_id>/
```

### Category 更新

```bash
curl -X PATCH http://127.0.0.1:8000/api/categories/<category_id>/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Books"
  }'
```

### Category 削除

```bash
curl -X DELETE http://127.0.0.1:8000/api/categories/<category_id>/
```

## 今後確認したい事項

現時点では、課題で明示されている CRUD の実装と基本的な整合性担保を優先しています。
一方で、実運用を考えると以下のような業務要件・利用ユースケースの確認余地があります。

### 1. 子カテゴリが存在する場合の削除仕様

現在は `parent_category` に `on_delete=models.SET_NULL` を設定しているため、親カテゴリ削除時に子カテゴリは残り、`parent_category` が `null` になります。
削除時の期待挙動は業務仕様に強く依存するため、課題段階ではモデル定義に沿った最小実装に留めています。

考えられる選択肢:

- 現在の実装のまま、子カテゴリをルートカテゴリとして残す
- 子カテゴリが存在する場合は削除を禁止する
- 子カテゴリも含めて再帰的に削除する

### 2. 一覧 API のページネーション

現在の一覧 API はページネーション未導入で、取得対象をそのまま返します。
ページネーションは件数想定やクライアント利用方法に依存するため、要件未確定の段階では導入していません。

考えられる選択肢:

- 件数が少ない前提で、ページネーションなしのまま運用する
- `PageNumberPagination` を導入する
- `LimitOffsetPagination` を導入する

### 3. 一覧 API の絞り込み・ソート条件

現在の一覧 API は全件取得で、`created_at` 昇順のみを行っています。`company` や親子関係、名前検索などによる絞り込みは未導入です。
一覧の利用ユースケースが未確定なため、勝手な解釈でフィルタやソート条件を追加せず、まずは最小構成に留めています。

考えられる選択肢:

- 現在の実装のまま、全件取得のみとする
- `company` 単位で絞り込めるようにする
- ルートカテゴリのみ取得するフィルタを追加する
- `name` による部分一致検索を追加する
- ソート条件を API パラメータで切り替えられるようにする

### 4. Company 更新の扱い

現在はカテゴリ木構造の整合性を保つため、`PATCH` による `company` 更新を禁止しています。
ここを安易に許可するとカテゴリ階層や関連リソース全体の整合性に影響しうるため、仕様確定までは安全側に倒しています。

また、将来的にカテゴリへ商品など他リソースが紐づく場合、`company` 更新はカテゴリ木構造だけでなく関連リソース全体の整合性にも影響するため、安易に許可しない方が安全だと考えています。

考えられる選択肢:

- 現在の実装のまま、`company` 更新を禁止する
- `company` 更新を許可し、親子関係・子孫関係を含めた整合性チェックを追加する
- `company` 更新時に、配下カテゴリも含めて一括更新する

### 5. カテゴリ名の扱い

現在はモデル定義と DRF 標準 validation により、空文字・空白のみ・255 文字超過・同一 company 内の重複を防いでいます。
一方で、trim の厳密な扱いや大文字小文字の同一視は業務ルール依存のため、明示要件がない範囲では追加実装していません。

考えられる選択肢:

- 現在の実装のまま運用する
- 前後空白の trim を明示的な仕様として定める
- 大文字小文字を区別しない重複判定にする

### 6. 認証・認可

現在は認証・認可要件が未確定のため、API へのアクセス制限は実装していません。
認証方式によって一覧・詳細・更新・削除の可視範囲や権限制御の実装が大きく変わるため、ここも仕様確定前に決め打ちしない方針としています。

特に、`Company` 単位でデータアクセスを制限するのか、API Token 等で認証したうえで別途認可したリソースにアクセスさせるのかで、実装方針は大きく変わると考えています。

考えられる選択肢:

- 認証なしの内部利用 API として運用する
- `Company` 単位の認証・認可を導入し、所属 Company のカテゴリのみ操作可能にする
- API Token ベースの認証を導入し、トークンに紐づく権限でアクセス可能リソースを制御する
