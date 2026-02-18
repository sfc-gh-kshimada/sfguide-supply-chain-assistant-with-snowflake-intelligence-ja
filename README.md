# Snowflake Intelligence を活用したサプライチェーンアシスタント

## ソリューション概要

現代のサプライチェーン運用は、複数の製造拠点にわたる原材料在庫の効率的な管理という重大な課題に直面しています。自動車（AUTOMOTIVE）、電子機器（ELECTRONICS）、建設（CONSTRUCTION）、エネルギー（ENERGY）、繊維・複合材料（TEXTILE）の5つの事業ラインを持つ当社では、運用管理者は常に在庫レベルのバランスを取り、余剰と不足のある工場間で材料を移送するか、サプライヤーから新たに購入するかを判断しなければなりません。これらの意思決定を手動で行うことは、時間がかかり、エラーが発生しやすく、コスト面で最適でない結果をもたらすことが多いです。

このクイックスタートでは、Snowflake Intelligence と Cortex AI の機能を使用して、インテリジェントなサプライチェーンアシスタントを構築する方法を紹介します。自然言語クエリと構造化・非構造化データのセマンティック検索を組み合わせることで、運用管理者が在庫管理に関するデータ駆動型の意思決定を行うための完全なソリューションを作成します。

このクイックスタートで学べる内容の概要は以下の通りです：

* **環境のセットアップ**：製造工場、在庫、サプライヤー、顧客、注文、出荷、天候データのテーブルを含む包括的なサプライチェーンデータベースの作成
* **Cortex Analyst**：自然言語によるText-to-SQLクエリを可能にする、サプライチェーン運用および天気予報のセマンティックモデルの構築
* **Cortex Search**：RAG（Retrieval Augmented Generation：検索拡張生成）を使用した、非構造化サプライチェーンドキュメントのインデックス作成とインテリジェント検索
* **カスタムツール**：Web検索、Webスクレイピング、HTML生成、メール機能をAIエージェントに統合
* **Snowflake Intelligence**：ユーザーの質問をインテリジェントにルーティングし、複数のデータソースを組み合わせる7つのツールを備えた包括的なAIエージェントの作成
* **高度な分析**：サプライチェーン最適化、天候影響分析、外部調査を含む複合的なマルチドメイン分析の実行

## 課題

![Alt text](/images/problem.png "課題")

サプライチェーンの運用管理者は、製造拠点全体にわたる原材料在庫の管理で日常的に以下の課題に直面しています：

* **在庫の不均衡**：一部の工場では原材料が余剰となり、他の工場では不足が発生し、非効率を生み出す
* **複雑な意思決定**：工場間で材料を移送するか、サプライヤーから購入するかを判断するには、材料コスト、輸送コスト、リードタイム、安全在庫レベルなど複数の要素を分析する必要がある
* **手動分析**：従来のアプローチでは、複数のレポート実行、スプレッドシート分析、手動でのコスト比較が必要
* **時間の制約**：在庫に関する意思決定は、生産遅延や過剰な在庫保有コストを避けるために迅速に行う必要がある

## ソリューション

![Alt text](/images/solution.png "ソリューション")

このソリューションは、Snowflake Intelligence と Cortex AI の機能を活用して、以下を実現するインテリジェントアシスタントを作成します：

1. **アドホックな質問への回答**：運用管理者が在庫レベル、注文、出荷、サプライヤー情報について自然言語で質問でき、エージェントが自動的に質問をSQLに変換して実行する
2. **コンテキスト情報の提供**：セマンティック検索を使用して、サプライチェーンドキュメントから関連情報を検索・取得する
3. **インテリジェントルーティング**：質問の性質に基づいて、構造化データ（Cortex Analyst経由）を照会するか、ドキュメント（Cortex Search経由）を検索するかを自動的に判断する
4. **複雑な分析**：同じ材料の在庫が不足している工場と余剰のある工場を特定し、サプライヤーからの購入コストと工場間移送コストを比較するなど、複数テーブルにまたがる高度なクエリを処理する
5. **ノーコードエージェント作成**：Snowflake Intelligence のビジュアルインターフェースを使用して、アプリケーションコードを書かずにソリューション全体を構築・デプロイする

## Snowflake Cortex とは？

Snowflake Cortex は、Snowflake 環境とガバナンスの境界内で安全に実行される、フルマネージドの生成AI機能を提供します。主な機能は以下の通りです：

**Cortex Analyst** - ビジネスユーザーが構造化データについて自然言語で質問できるようにします。セマンティックモデルを使用してデータを理解し、正確なSQLクエリを自動生成します。

**Cortex Search** - 非構造化データに対する使いやすいセマンティック検索を提供します。ドキュメントのチャンキング、エンベディング生成、検索を処理し、RAG（検索拡張生成）パターンの実装を簡素化します。

**Cortex Agents** - Analyst と Search などの複数のAI機能をオーケストレーションし、ユーザーのクエリを適切なサービスにインテリジェントにルーティングして応答を合成します。

[Snowflake Cortex](https://www.snowflake.com/en/product/features/cortex/) の詳細はこちら。

## Snowflake Intelligence とは？

Snowflake Intelligence は、Snowflake 内でAIエージェントを構築・デプロイするための統合エクスペリエンスです。以下を提供します：

* **ノーコードエージェントビルダー**：コードを書かずに、複数のツール（Cortex Analyst、Cortex Search、カスタムツール）を組み合わせたエージェントを作成
* **統合ツール**：セマンティックモデルと検索サービスをエージェント機能として簡単に接続
* **会話型インターフェース**：Snowsight 内のチャットインターフェースを通じてエージェントと対話
* **エンタープライズ対応**：Snowflake のセキュリティとガバナンス基盤の上に構築

[Snowflake Intelligence](https://docs.snowflake.com/en/user-guide/snowflake-cortex/snowflake-intelligence) の詳細はこちら。

## 学べること

* Snowflake での適切なリレーションシップを持つ多層サプライチェーンのモデリング方法
* ディメンション、メジャー、検証済みクエリを含む Cortex Analyst 用セマンティックモデルの作成方法
* 非構造化ドキュメントに対する Cortex Search サービスのセットアップ方法
* Snowflake Intelligence を使用した包括的なAIエージェントの構築方法
* 単一エージェントでのクロスドメイン分析のための複数セマンティックモデルの組み合わせ方法
* カスタムツール（関数とストアドプロシージャ）のエージェントへの統合方法
* AIアシスタント内でのWeb検索とスクレイピング機能の有効化方法
* AIの正確な応答のための効果的なツール説明とセマンティックモデルの記述方法
* 複数のデータソースにまたがる複雑な分析クエリの処理方法

## 構築するもの

* 11テーブルとリアルなサンプルデータを含む包括的なサプライチェーンデータベース
* 2つのセマンティックモデル：サプライチェーンデータ用と天気予報用
* サプライチェーンドキュメントにインデックスされた Cortex Search サービス
* 7つのツールを備えた Snowflake Intelligence エージェント：
  * 2つの Cortex Analyst ツール（サプライチェーンと天候データ）
  * 1つの Cortex Search ツール（ドキュメント）
  * 4つのカスタムツール（Web検索、Webスクレイピング、HTMLニュースレター生成、メール送信）
* 在庫分析、コスト比較、リバランス機会のための複雑な検証済みクエリ
* 構造化データ、非構造化データ、外部Webソースを組み合わせた本番対応のAIアシスタント

## 前提条件

* Cortex 機能が有効化された Snowflake アカウント。Snowflake アカウントをお持ちでない場合は、[無料トライアルに登録](https://signup.snowflake.com/)できます。
* ACCOUNTADMIN ロール、またはデータベース、スキーマ、テーブル、ステージ、Cortex Search サービスを作成できるロールを持つ Snowflake アカウントログイン。
* Cortex Analyst、Cortex Search、Snowflake Intelligence が Snowflake リージョンで利用可能であること。
* Snowflake SQL と Snowsight インターフェースの基本的な知識。

> **注意：** Web検索とWebスクレイピング用のカスタムツールは外部統合アクセスが必要であり、トライアルアカウントでは利用できません。これらのツールのセットアップステップをスキップしても、クイックスタートの他の部分は完了できます。

---

## ステップ 1 - データベースのセットアップとデータのロード

このステップでは、必要なすべてのテーブル、ステージ、サンプルデータを含むサプライチェーンデータベースインフラストラクチャを作成します。

データベースは、サプライヤー、製造工場、顧客を含む多層サプライチェーンネットワークをモデル化します。デモでは在庫レベル、需要、安全在庫、リードタイムのばらつき、コストなどの主要な運用要素を考慮します。

1. Snowsight で **Projects > Workspaces** に移動し、新しいプライベートワークスペースを作成
2. ワークスペースに新しい SQL ファイルを追加
3. リポジトリの **scripts/setup.sql** ファイルをインポート
4. **Run All** をクリックしてスクリプト全体を実行

このスクリプトにより以下が作成されます：

* データベース：`SUPPLY_CHAIN_ASSISTANT_DB`（スキーマ `ENTITIES` と `WEATHER`）
* ウェアハウス：`SUPPLY_CHAIN_ASSISTANT_WH`
* すべてのサプライチェーンテーブル（サプライヤー、工場、在庫、注文など）
* PDF とセマンティックモデル用の内部ステージ
* INSERT 文によるサンプルデータのロード
* カスタム関数とプロシージャ（Web検索、Webスクレイピング、メール、HTMLニュースレター生成機能）

## ステップ 2 - ドキュメントとセマンティックモデルのアップロード

最初のステップで、すべてのオブジェクトが `SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES` データベース/スキーマに作成されています。2つの内部ステージを作成したので、ここでファイルをアップロードします。

### PDF ドキュメントのアップロード

1. 左側メニューの **Catalog** から **データベースエクスプローラー** に移動
2. `SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES` データベース/スキーマに移動
3. **Stages** をクリックして利用可能なステージを表示
4. **SUPPLY_CHAIN_ASSISTANT_PDF_STAGE** ステージを選択
5. 右上の **+ Files** ボタンをクリック
6. **pdfs/Supply Chain Network Overview.pdf**（または日本語版 **pdfs/Supply Chain Network Overview.md**）ファイルをアップロード

### セマンティックモデルファイルのアップロード

1. 同じ Stages ビューで **SEMANTIC_MODELS_STAGE** ステージを選択
2. **+ Files** ボタンをクリック
3. 両方のセマンティックモデルファイルをアップロード：
   * **scripts/semantic_models/SUPPLY_CHAIN_ASSISTANT_MODEL.yaml**
   * **scripts/semantic_models/WEATHER_FORECAST.yaml**

これらのセマンティックモデルは、Cortex Analyst がサプライチェーンデータと天候データに関する自然言語の質問に回答するために使用する構造、リレーションシップ、検証済みクエリを定義しています。

## ステップ 3 - Cortex Search サービスの作成

Cortex Search サービスの作成には2つの方法があります：

### オプション A：SQL スクリプトを使用

1. ワークスペースに新しい SQL ファイルを追加
2. **scripts/configure_search_services.sql** ファイルをインポート
3. **Run All** をクリックしてスクリプト全体を実行

このスクリプトは以下を行います：

* Cortex PARSE_DOCUMENT 関数を使用して PDF を解析
* 再帰的文字分割によりコンテンツを検索可能なセグメントにチャンク分割
* 事前署名付き URL を持つ `PARSED_PDFS` テーブルを作成
* `SUPPLY_CHAIN_INFO` Cortex Search サービスを作成
* 事前署名付き URL を毎日更新するタスクをセットアップ（7日で期限切れのため）

### オプション B：Snowsight UI から手動作成

検索サービスを手動で作成する場合：

#### ステップ 3.1：データの準備（SQL が必要）

UI アプローチでも、ドキュメントの解析と準備のために一部の SQL を実行する必要があります。新しいワークシートを開いて以下を実行してください：

```sql
USE SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES;
USE WAREHOUSE SUPPLY_CHAIN_ASSISTANT_WH;

-- PDF 解析のためにウェアハウスをスケールアップ
ALTER WAREHOUSE SUPPLY_CHAIN_ASSISTANT_WH SET WAREHOUSE_SIZE = 'X-LARGE';

-- PDF の解析
CREATE OR REPLACE TABLE PARSE_PDFS AS 
SELECT RELATIVE_PATH, 
       SNOWFLAKE.CORTEX.PARSE_DOCUMENT(@SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES.SUPPLY_CHAIN_ASSISTANT_PDF_STAGE, 
                                        RELATIVE_PATH, 
                                        {'mode':'LAYOUT'}) AS DATA
FROM DIRECTORY(@SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES.SUPPLY_CHAIN_ASSISTANT_PDF_STAGE);

-- コンテンツのチャンク分割と準備
CREATE OR REPLACE TABLE PARSED_PDFS AS (
    WITH TMP_PARSED AS (
        SELECT RELATIVE_PATH,
               SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER(TO_VARIANT(DATA):content, 'MARKDOWN', 1800, 300) AS CHUNKS
        FROM PARSE_PDFS 
        WHERE TO_VARIANT(DATA):content IS NOT NULL
    )
    SELECT TO_VARCHAR(C.value) AS PAGE_CONTENT,
           REGEXP_REPLACE(RELATIVE_PATH, '\\.pdf$', '') AS TITLE,
           RELATIVE_PATH,
           GET_PRESIGNED_URL(@SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES.SUPPLY_CHAIN_ASSISTANT_PDF_STAGE, RELATIVE_PATH, 604800) AS PAGE_URL
    FROM TMP_PARSED P, LATERAL FLATTEN(INPUT => P.CHUNKS) C
);

-- ウェアハウスをスケールダウン
ALTER WAREHOUSE SUPPLY_CHAIN_ASSISTANT_WH SET WAREHOUSE_SIZE = 'SMALL';
```

#### ステップ 3.2：UI から検索サービスを作成

1. Snowsight で、左側ナビゲーションの **AI & ML** > **Cortex Search** に移動
2. **Create** ボタンをクリック
3. 検索サービスを設定：
   * **Database:** `SUPPLY_CHAIN_ASSISTANT_DB`
   * **Schema:** `ENTITIES`
   * **Name:** `SUPPLY_CHAIN_INFO`
   * **Source Table to be Indexed:** `PARSED_PDFS`
   * **Search Column:** `PAGE_CONTENT` を選択
   * **Attributes:** **Next** をクリック
   * **Select Columns:** `TITLE` を選択
   * **Target Lag:** `1 hour`
   * **Warehouse:** `SUPPLY_CHAIN_ASSISTANT_WH`
4. **Create Search Service** をクリック

検索サービスが解析済みPDFコンテンツのインデックス作成を開始します。インデックス作成が完了すると、セマンティック検索クエリに利用可能になります。

## ステップ 4 - Snowflake Intelligence エージェントの作成

セマンティックモデルと検索サービスが作成されたので、Snowflake Intelligence を使用してインテリジェントエージェントに統合できます。エージェントはユーザーの質問の性質に基づいて、適切なツールにインテリジェントにルーティングします。

### エージェントの作成

> Snowsight で **SUPPLY_CHAIN_ASSISTANT_ROLE** ロールを使用していることを確認してください。

1. Snowsight の左側ナビゲーションバーの **AI & ML** セクション内の **Agents** をクリック
2. **Create Agent** ボタンをクリック
3. 以下を設定：
   * **Database:** `SNOWFLAKE_INTELLIGENCE`
   * **Schema:** `AGENTS`
   * **Agent object name:** `Supply_Chain_Agent`
   * **Display name:** Supply Chain Agent
4. 作成後、**Tools** タブに移動

### 最初の Cortex Analyst ツールの追加 - サプライチェーンデータ

1. **Cortex Analyst** の横にある **+ Add** をクリック
2. ツールを設定：
   * **Semantic model file** ラジオボタンを選択
   * **Database:** `SUPPLY_CHAIN_ASSISTANT_DB`
   * **Schema:** `ENTITIES`
   * **Stage:** `SEMANTIC_MODELS_STAGE`
   * `SUPPLY_CHAIN_ASSISTANT_MODEL.yaml` を選択
   * **Name:** `SUPPLY_CHAIN_ASSISTANT_MODEL`
   * **Description:** *"Tool for analyzing supply chain data."*
   * **Warehouse:** **Custom** ラジオボタンを選択し、`SUPPLY_CHAIN_ASSISTANT_WH` を選択
3. **Save** をクリック

### 2番目の Cortex Analyst ツールの追加 - 天候データ

1. **Cortex Analyst** の横にある **+ Add** をクリック
2. ツールを設定：
   * **Semantic model file** ラジオボタンを選択
   * **Database:** `SUPPLY_CHAIN_ASSISTANT_DB`
   * **Schema:** `ENTITIES`
   * **Stage:** `SEMANTIC_MODELS_STAGE`
   * `WEATHER_FORECAST.yaml` を選択
   * **Name:** `WEATHER_FORECAST`
   * **Description:** *"Tool for analyzing weather data."*
   * **Warehouse:** **Custom** ラジオボタンを選択し、`SUPPLY_CHAIN_ASSISTANT_WH` を選択
3. **Save** をクリック

### Cortex Search ツールの追加

1. **Cortex Search Services** の横にある **+ Add** をクリック
2. ツールを設定：
   * **Database:** `SUPPLY_CHAIN_ASSISTANT_DB`
   * **Schema:** `ENTITIES`
   * **Search Service:** `SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES.SUPPLY_CHAIN_INFO` を選択
   * **Name:** `SUPPLY_CHAIN_INFO`
   * **Description:** *"Tool for searching supply chain unstructured data."*
   * **ID Column:** `PAGE_URL`
   * **Title Column:** `TITLE`
3. **Save** をクリック

### カスタムツールの追加

> **注意：** WEB_SEARCH と WEB_SCRAPE カスタムツールは外部統合アクセスが必要であり、トライアルアカウントでは利用できません。トライアルアカウントを使用している場合は、これら2つのツールの追加をスキップしても他のエージェント機能は使用できます。

以下の各カスタムツールについて、**Custom Tool** の横にある **+ Add** をクリックしてから設定します：

#### 1. CREATE_HTML_NEWSLETTER

* **Type:** procedure
* **Schema:** `SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES`
* **Custom tool identifier:** `CREATE_HTML_NEWSLETTER_SP`
* **Name:** `CREATE_HTML_NEWSLETTER_SP`
* **Warehouse:** `SUPPLY_CHAIN_ASSISTANT_WH`
* **Description:** *"Create HTML newsletter from responses."*

#### 2. WEB_SEARCH

* **Type:** function
* **Schema:** `SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES`
* **Custom tool identifier:** `WEB_SEARCH`
* **Name:** `WEB_SEARCH`
* **Warehouse:** `SUPPLY_CHAIN_ASSISTANT_WH`
* **Description:** *"Search the web using DuckDuckGo."*

#### 3. WEB_SCRAPE

* **Type:** function
* **Schema:** `SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES`
* **Custom tool identifier:** `WEB_SCRAPE`
* **Name:** `WEB_SCRAPE`
* **Warehouse:** `SUPPLY_CHAIN_ASSISTANT_WH`
* **Description:** *"Web scraping and content extraction."*

#### 4. SEND_MAIL（オプション - 認証済みメールアドレスが必要）

* **Type:** procedure
* **Schema:** `SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES`
* **Custom tool identifier:** `SEND_MAIL`
* **Name:** `SEND_MAIL`
* **Warehouse:** `SUPPLY_CHAIN_ASSISTANT_WH`
* **Description:** *"Send emails to recipients with HTML formatted content."*

### エージェントの保存とテスト

1. **Save** をクリックしてエージェント設定を保存
2. 右側のペインで直接エージェントのテストを開始できます

### Snowflake Intelligence への公開

エージェントを Snowflake Intelligence で利用可能にするには、以下の手順が必要です：

1. 作成したエージェントのページで **Overview** タブに移動
2. **Snowflake Intelligence** セクションにある **Add to Snowflake Intelligence** ボタンをクリック
3. 左側ナビゲーションの **AI & ML** メニューで **Snowflake Intelligence** に移動
4. ドロップダウンからエージェントを選択
5. 質問を始めましょう！

## ステップ 5 - サンプル質問を試す

シンプルな質問から始めて、徐々に複雑な分析に進みましょう。エージェントが質問に基づいて自動的にどのツールを使用するかを決定する様子に注目してください！

**サプライチェーンデータの質問（Cortex Analyst - サプライチェーンモデル）：**

* "稼働中の製造工場は何拠点ありますか？"
* "AUTOMOTIVE事業ラインの注文は何件ありますか？"
* "注文金額が大きい上位5社の顧客は？"
* "製造工場にある完成品の総在庫数量は？"
* "製造工場で在庫が不足している原材料はどれですか？"
* "TEXTILE事業の製造工場一覧を教えてください"
* "在庫不足の工場に対して、余剰在庫のある工場から資材を移送する場合のコストと新規購入コストの比較は？"

**天候データの質問（Cortex Analyst - 天候モデル）：**

* "東京の天気予報はどうですか？"
* "降水確率が最も高い都市はどこですか？"
* "大阪の気温予報を見せてください"
* "名古屋の風の状況はどうですか？"

**ドキュメントの質問（Cortex Search）：**

* "当社のビジネスにおける出荷追跡の仕組みを説明してください"
* "当社のビジネスラインは何ですか？"
* "当社のサプライチェーンネットワークはどのように運営されていますか？"

**Web リサーチの質問（カスタムツール - Web 検索 & Web スクレイプ）：**

* "最近のサプライチェーンの混乱について Web 検索してください"
* "サプライチェーン管理の最新トレンドは何ですか？"

**メールとニュースレターの作成（カスタムツール）：**

* "今月のトップ顧客をまとめた HTML ニュースレターを作成してください"
* "現在の在庫状況に関するメールを下書きしてください"（注：送信にはメール統合が必要）

**クロスツールの複合質問：**

* "当社の製造工場がある都市の天気予報はどうですか？"
* "厳しい天候条件が予想される工場の在庫レベルを比較してください"

![Alt text](/images/Agent.gif "Snowflake Intelligence")

## 次のステップ

おめでとうございます！以下を組み合わせた、Snowflake Intelligence を活用した包括的なサプライチェーンアシスタントの構築が完了しました：

* **デュアル分析**：サプライチェーン運用と天候データの両方をクエリ
* **セマンティック検索**：非構造化サプライチェーンドキュメントへのアクセス
* **Web 統合**：外部情報の検索とスクレイピング
* **コミュニケーション**：HTML ニュースレターの生成とメール送信（適切な統合が必要）

このソリューションをさらに拡張するには：

* 他のビジネスドメイン用のセマンティックモデルを追加
* 追加のデータソースを統合
* 特定のビジネスプロセス用のカスタムツールを作成
* エージェントと連携する Streamlit アプリケーションを構築
