import streamlit as st
import json
import _snowflake
from snowflake.snowpark.context import get_active_session
from abc import ABC, abstractmethod
from scipy.optimize import linprog  # 線形計画法用
import pandas as pd
import uuid
import numpy as np

session = get_active_session()

API_ENDPOINT = "/api/v2/cortex/agent:run"
API_TIMEOUT = 50000  # ミリ秒

CORTEX_SEARCH_SERVICES = "SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES.SUPPLY_CHAIN_INFO"
SEMANTIC_MODELS = "@SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES.SEMANTIC_MODELS_STAGE/SUPPLY_CHAIN_ASSISTANT_MODEL.yaml"

# ページ設定
st.set_page_config(
    page_title="サプライチェーンアシスタント",
    page_icon="❄️️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "このアプリは、Cortex Search と Cortex Analyst サービスを含む3層サプライチェーン用のチャットアシスタントです。サプライチェーン最適化ソルバーも含まれています。"
    }
)

# 開始ページの設定
if "page" not in st.session_state:
    st.session_state.page = "Welcome"


# ページ名に基づいてページを設定
def set_page(page: str):
    st.session_state.page = page

# カスタム CSS スタイリング
st.markdown("""
<style>
/* 統一カラーパレット */
:root {
    --background-color: #FFFFFF;
    --text-color: #222222;
    --title-color: #1A1A1A;
    --button-color: #1a56db;
    --button-text: #FFFFFF;
    --border-color: #CBD5E0;
    --accent-color: #2C5282;
}

/* 全体のアプリスタイリング */
.stApp {
    background-color: var(--background-color);
    color: var(--text-color);
}

/* タイトルスタイリング */
h1, .stTitle {
    color: var(--title-color) !important;
    font-size: 36px !important;
    font-weight: 600 !important;
    padding: 1.5rem 0;
}

/* 入力フィールド */
textarea {
    background-color: white !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 4px !important;
    padding: 16px !important;
    font-size: 16px !important;
    color: var(--text-color) !important;
}

textarea:focus {
    border-color: var(--accent-color) !important;
    box-shadow: 0 0 0 1px var(--accent-color) !important;
}

textarea::placeholder {
    color: #666666 !important;
}

/* 成功・エラーメッセージ */
.stException {
    background-color: #FEE2E2 !important;
    border: 1px solid #EF4444 !important;
    padding: 16px !important;
    border-radius: 4px !important;
    margin: 16px 0 !important;
    color: #991B1B !important;
}

div[data-testid="stAlert"], div[data-testid="stException"] {
    background-color: #f8d7da !important;
    color: #721c24 !important;
    border: 1px solid #f5c6cb !important;
    padding: 12px !important;
    border-radius: 6px !important;
    font-weight: bold !important;
}

div[data-testid="stAlertContentError"] {
    color: #721c24 !important;
}

.stFormSubmitButton {
    background-color: white !important;
    padding: 10px;
    border-radius: 8px;
}

button[data-testid="stBaseButton-secondaryFormSubmit"] {
    background-color: #29B5E8 !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 5px !important;
    padding: 8px 16px !important;
    border: none !important;
}

/* サイドバーボタン */
.stSidebar button {
    background-color: #29B5E8 !important;
    color: white !important;
    font-weight: 600 !important;
    border: none !important;
}

/* ツールチップ */
.tooltip {
    visibility: hidden;
    opacity: 0;
    background-color: white;
    color: var(--text-color);
    padding: 10px;
    border-radius: 10px;
    font-size: 14px;
    line-height: 1.5;
    width: max-content;
    max-width: 300px;
    position: absolute;
    z-index: 1000;
    bottom: calc(100% + 5px);
    left: 50%;
    transform: translateX(-50%);
    transition: opacity 0.3s ease, transform 0.3s ease;
}

.citation:hover + .tooltip {
    visibility: visible;
    opacity: 1;
    transform: translateX(-50%) translateY(0);
}

/* Streamlit ブランディングの非表示 */
#MainMenu, header, footer {
    visibility: hidden;
}

[data-testid="stDownloadButton"] button {
    background-color: #2196F3 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border: none !important;
    padding: 0.5rem 1rem !important;
    border-radius: 0.375rem !important;
    box-shadow: none !important;
}

.metric-container {
        border: 1px solid #ccc;
        padding: 15px;
        border-radius: 5px;
        text-align: center;
}

.metric-label {
    font-size: 1em;
    color: #555;
}

.metric-value {
    font-size: 1.5em;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


class Page(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def print_page(self):
        pass

    @abstractmethod
    def print_sidebar(self):
        pass

def set_default_sidebar():
    # ページナビゲーション用サイドバー
    with st.sidebar:
        st.title("サプライチェーンネットワークアシスタント 🚚")
        st.markdown("")
        st.markdown("このアプリケーションは、Cortex Search と Cortex Analyst サービスを含むサプライチェーンネットワーク用のチャットアシスタントです。サプライチェーン最適化ソルバーも含まれています。")
        st.markdown("")
        if st.button(label="サプライチェーンアシスタント 💬"):
            set_page('Assistant')
            st.rerun()
        if st.button(label="最適化実行 🚀"):
            set_page('Optimization')
            st.rerun()
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        if st.button(label="ホームに戻る"):
            set_page('Welcome')
            st.rerun()

def run_snowflake_query(query):
    try:
        df = session.sql(query.replace(';',''))
        
        return df

    except Exception as e:
        st.error(f"SQL 実行エラー: {str(e)}")
        return None, None

def snowflake_api_call(query: str, limit: int = 10):
    
    payload = {
        "model": "claude-3-5-sonnet",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            }
        ],
        "tools": [
            {
                "tool_spec": {
                    "type": "cortex_analyst_text_to_sql",
                    "name": "analyst1"
                }
            },
            {
                "tool_spec": {
                    "type": "cortex_search",
                    "name": "search1"
                }
            }
        ],
        "tool_resources": {
            "analyst1": {"semantic_model_file": SEMANTIC_MODELS},
            "search1": {
                "name": CORTEX_SEARCH_SERVICES,
                "max_results": limit
            }
        },
        "response-instruction": "常にフレンドリーなトーンを維持し、簡潔に回答してください。「提供された情報によると」のような表現は避けてください。"
    }
    
    try:
        resp = _snowflake.send_snow_api_request(
            "POST",  # メソッド
            API_ENDPOINT,  # パス
            {},  # ヘッダー
            {},  # パラメータ
            payload,  # ボディ
            None,  # request_guid
            API_TIMEOUT,  # タイムアウト（ミリ秒）
        )
        try:
            response_content = json.loads(resp["content"])
        except json.JSONDecodeError:
            st.error("❌ API レスポンスの解析に失敗しました。サーバーが無効な JSON 形式を返した可能性があります。")

            if resp["status"] != 200:
                st.error(f"エラー:{resp} ")
            return None
            
        return response_content
            
    except Exception as e:
        st.error(f"リクエストエラー: {str(e)}")
        return None

def process_sse_response(response):
    """SSE レスポンスの処理"""
    text = ""
    sql = ""
    interpretation = ""
    citation = ""
    
    if not response:
        return text, sql, interpretation, citation
        
    try:
        for event in response:
            if event.get('event') == "message.delta":
                data = event.get('data', {})
                delta = data.get('delta', {})
                
                for content_item in delta.get('content', []):
                    content_type = content_item.get('type')
                    if content_type == "tool_results":
                        tool_results = content_item.get('tool_results', {})
                        if 'content' in tool_results:
                            for result in tool_results['content']:
                                if result.get('type') == 'json':
                                    interpretation += result.get('json', {}).get('text', '')
                                    search_results = result.get('json', {}).get('searchResults', [])
                                    for search_result in search_results:
                                        citation += f"\n• {search_result.get('text', '')}"
                                    sql = result.get('json', {}).get('sql', '')
                    if content_type == 'text':
                        text += content_item.get('text', '')
                            
    except json.JSONDecodeError as e:
        st.error(f"イベント処理エラー: {str(e)}")
                
    except Exception as e:
        st.error(f"イベント処理エラー: {str(e)}")
        
    return text, sql, interpretation, citation

low_excess_query = """
    WITH low_inventory AS (
        SELECT
            l.mfg_plant_id AS low_plant_id,
            mp.mfg_plant_name AS low_plant_name,  -- レポート用に名前を保持
            l.material_id,
            rm.material_name,
            l.quantity_on_hand AS low_qty,
            l.safety_stock_level,
            rm.material_cost,
            l.safety_stock_level * 2 AS low_replenishment_point,
            (low_replenishment_point - l.quantity_on_hand) AS units_needed
        FROM
            supply_chain_assistant_db.entities.mfg_inventory AS l
        JOIN supply_chain_assistant_db.entities.mfg_plant AS mp ON l.mfg_plant_id = mp.mfg_plant_id
        JOIN supply_chain_assistant_db.entities.raw_material AS rm ON l.material_id = rm.material_id
        WHERE l.quantity_on_hand < l.safety_stock_level
        AND l.days_forward_coverage <= l.material_lead_time + l.lead_time_variability
    ), excess_inventory AS (
        SELECT
            e.mfg_plant_id AS excess_plant_id,
            mp.mfg_plant_name AS excess_plant_name,  -- レポート用に名前を保持
            e.material_id,
            e.quantity_on_hand AS excess_qty,
            e.safety_stock_level,
            e.safety_stock_level * 2 AS excess_replenishment_point,
            (e.quantity_on_hand - excess_replenishment_point) AS available_to_transfer
        FROM
            supply_chain_assistant_db.entities.mfg_inventory AS e
        JOIN supply_chain_assistant_db.entities.mfg_plant AS mp ON e.mfg_plant_id = mp.mfg_plant_id
        WHERE e.quantity_on_hand > 3 * e.safety_stock_level
        AND e.days_forward_coverage > 2 * e.material_lead_time
    )
    SELECT
        l.low_plant_id,
        l.low_plant_name,
        l.material_id,
        l.material_name,
        l.units_needed,
        l.material_cost,
        e.excess_plant_id,
        e.excess_plant_name,
        e.available_to_transfer,
        (l.material_cost * 0.3 * COALESCE(tcs.transport_cost_surcharge, 1.5)) AS transfer_cost_per_unit
    FROM
        low_inventory AS l
    LEFT JOIN excess_inventory AS e ON l.material_id = e.material_id
    LEFT JOIN supply_chain_assistant_db.entities.transport_cost_surcharge AS tcs
        ON e.excess_plant_id = tcs.source_facility_id AND l.low_plant_id = tcs.destination_facility_id
    WHERE e.available_to_transfer > 0  AND l.units_needed > 0 -- 正の移送量のみを確保
    ORDER BY
        l.low_plant_name,
        l.material_name;
    """

low_excess_df = run_snowflake_query(low_excess_query)


def optimize_transfers():
    """
    在庫が少ない工場と余剰のある工場間の材料移送を最適化します。

    この関数は：
    1. 提供された SQL クエリの修正版を実行して、
       在庫不足/余剰データ（輸送コスト乗数を含む）を取得します。
    2. 線形計画問題を定式化・解決して、
       総移送コストを最小化します。
    3. 最適な移送アクションを 'transfer_actions' テーブルに挿入します。

    Args:
        session: Snowflake Snowpark セッション。

    Returns:
        成功と作成された移送アクション数を示す文字列。
    """

    # --- 1. Snowflake からデータを取得（修正クエリ） ---

    low_excess_df_pd = low_excess_df.to_pandas()

    # --- 2. 線形計画法の定式化 ---

    if low_excess_df_pd.empty:
        return "移送の機会が見つかりませんでした。"

    low_plants = [int(x) for x in low_excess_df_pd['LOW_PLANT_ID'].unique().tolist()]
    excess_plants = [int(x) for x in low_excess_df_pd['EXCESS_PLANT_ID'].unique().tolist()]
    materials = low_excess_df_pd['MATERIAL_ID'].unique().tolist()

    # --- サプライヤーを「余剰工場」として追加 ---
    supplier_id = 999  # サプライヤー ID として 999 を使用
    excess_plants.append(supplier_id)

    # --- 線形計画法の定式化 ---
    num_low_plants = len(low_plants)
    num_excess_plants = len(excess_plants)
    num_materials = len(materials)
    num_vars = num_low_plants * num_excess_plants * num_materials

    c = np.zeros(num_vars)  # コスト係数
    A_ub = []  # 不等式制約行列 (Ax <= b)
    b_ub = []  # 不等式制約ベクトル
    A_eq = []  # 等式制約行列 (Ax = b)
    b_eq = []  # 等式制約ベクトル
    bounds = [(0, float('inf'))] * num_vars

    # コスト行列 (c) の構築
    for i, low_plant_id in enumerate(low_plants):
        for j, material_id in enumerate(materials):
            for k, excess_plant_id in enumerate(excess_plants):
                idx = i * num_excess_plants * num_materials + j * num_excess_plants + k

                if excess_plant_id == supplier_id:
                    # サプライヤーからのコストは材料コストのみ
                    material_cost = low_excess_df_pd[low_excess_df_pd['MATERIAL_ID'] == material_id]['MATERIAL_COST'].iloc[0]
                    c[idx] = material_cost
                else:
                    # 他の工場からのコストは材料コスト × 輸送乗数
                    match = low_excess_df_pd[
                        (low_excess_df_pd['LOW_PLANT_ID'] == low_plant_id) &
                        (low_excess_df_pd['EXCESS_PLANT_ID'] == excess_plant_id) &
                        (low_excess_df_pd['MATERIAL_ID'] == material_id)
                        ]
                    if not match.empty:
                        row = match.iloc[0]
                        c[idx] = row['TRANSFER_COST_PER_UNIT']
                    else:
                        c[idx] = 1e9  # 不可能な移送に対する非常に高いコスト

    # 供給制約 (<= available_to_transfer、サプライヤーを含む)
    for j, material_id in enumerate(materials):
        for k, excess_plant_id in enumerate(excess_plants):
            row = [0] * num_vars
            for i in range(num_low_plants):
                idx = i * num_excess_plants * num_materials + j * num_excess_plants + k
                row[idx] = 1

            if excess_plant_id == supplier_id:
                available = 1e9 # サプライヤーの大きな数値
            else:
                match = low_excess_df_pd[
                    (low_excess_df_pd['EXCESS_PLANT_ID'] == excess_plant_id) &
                    (low_excess_df_pd['MATERIAL_ID'] == material_id)
                    ]
                if not match.empty:
                    available = match['AVAILABLE_TO_TRANSFER'].iloc[0]
                else:
                    available = 0
            A_ub.append(row)
            b_ub.append(available)

    # 需要制約 (= units_needed) -- 修正されたロジック
    for i, low_plant_id in enumerate(low_plants):
        for j, material_id in enumerate(materials):
            row = [0] * num_vars
            for k in range(num_excess_plants):
                idx = i * num_excess_plants * num_materials + j * num_excess_plants + k
                row[idx] = 1 # すべての入庫移送を合計

            match = low_excess_df_pd[
                (low_excess_df_pd['LOW_PLANT_ID'] == low_plant_id) &
                (low_excess_df_pd['MATERIAL_ID'] == material_id)
                ]

            if not match.empty:
                needed = match['UNITS_NEEDED'].iloc[0]
            else:
                needed = 0

            A_eq.append(row) # 等式制約
            b_eq.append(needed)


    # --- 線形計画問題の求解 ---
    # 等式制約には A_eq と b_eq を使用
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")


    if result.status != 0:
        return f"線形計画法が失敗しました: {result.message}"

    transfer_actions = []
    idx = 0
    for i, low_plant_id in enumerate(low_plants):
        for j, material_id in enumerate(materials):
            for k, excess_plant_id in enumerate(excess_plants):
                transfer_quantity = round(result.x[idx], 2)
                idx += 1
                if transfer_quantity > 0:
                    if excess_plant_id == supplier_id:
                        # 購入アクション
                        material_cost = low_excess_df_pd[low_excess_df_pd['MATERIAL_ID'] == material_id]['MATERIAL_COST'].iloc[0]
                        transfer_actions.append({
                            'action_type': 'PURCHASE',
                            'source_plant_id': excess_plant_id,
                            'destination_plant_id': low_plant_id,
                            'material_id': material_id,
                            'transfer_quantity': transfer_quantity,
                            'transfer_cost': transfer_quantity * material_cost,
                            'savings': 0.00,
                            'transfer_id': str(uuid.uuid4()),
                            'transfer_date': pd.to_datetime('today').normalize()                            
                        })
                    else:
                        # 移送アクション
                        match = low_excess_df_pd[
                            (low_excess_df_pd['LOW_PLANT_ID'] == low_plant_id) &
                            (low_excess_df_pd['EXCESS_PLANT_ID'] == excess_plant_id) &
                            (low_excess_df_pd['MATERIAL_ID'] == material_id)
                        ]
                        if not match.empty:
                            cost_per_unit = match.iloc[0]['TRANSFER_COST_PER_UNIT']
                            material_cost = low_excess_df_pd[low_excess_df_pd['MATERIAL_ID'] == material_id]['MATERIAL_COST'].iloc[0]
                            transfer_actions.append({
                                'action_type': 'TRANSFER',
                                'source_plant_id': excess_plant_id,
                                'destination_plant_id': low_plant_id,
                                'material_id': material_id,
                                'transfer_quantity': transfer_quantity,
                                'transfer_cost': transfer_quantity * cost_per_unit,
                                'savings': transfer_quantity * (material_cost - cost_per_unit),
                                'transfer_id': str(uuid.uuid4()),
                                'transfer_date': pd.to_datetime('today').normalize()
                            })

    if not transfer_actions:
        return "最適な移送が見つかりませんでした。"

    # Snowpark DataFrame を作成して Snowflake に書き込み
    transfer_actions_df = session.create_dataframe(pd.DataFrame(transfer_actions))
    transfer_actions_df.write.mode("overwrite").save_as_table("supply_chain_assistant_db.entities.transfer_actions")

    return f"{len(transfer_actions)} 件の移送アクションが正常に作成されました。"
    

class WelcomePage(Page):
    def __init__(self):
        self.name = "Welcome"

    def print_page(self):
        # メインページのセットアップ
        col1, col2 = st.columns((6, 1))
        col1.title("サプライチェーンネットワークアシスタント 🚚")

        # ウェルカムページ
        st.subheader("インテリジェントサプライチェーンアシスタントへようこそ ❄️")

        st.write('''このアシスタントは Streamlit で構築されており、サプライチェーンデータの
        セマンティック詳細を理解してText-to-SQLを実行する Cortex Analyst サービス、
        サプライチェーンに関する非構造化 PDF に対する Cortex Search サービス、
        そして質問を適切なサービスにルーティングして回答をフォーマットする
        Cortex Agents API を活用しています。''')

        st.write('')
        st.write('')
        st.write('')

        
        st.image("cortex_image.png", use_container_width=True)

    def print_sidebar(self):
        set_default_sidebar()


class AssistantPage(Page):
    def __init__(self):
        self.name = "Assistant"

    def print_page(self):
        # セッション状態の初期化
        st.title("インテリジェントサプライチェーンネットワークアシスタント")
        
        if 'messages' not in st.session_state:
            st.session_state.messages = []
    
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                st.markdown(message['content'].replace("•", "\n\n-"))
    
        if query := st.chat_input("何について知りたいですか？"):
            # ユーザーメッセージをチャットに追加
            with st.chat_message("user"):
                st.markdown(query)
            st.session_state.messages.append({"role": "user", "content": query})
            
            # API からレスポンスを取得
            with st.spinner("リクエストを処理中..."):
                response = snowflake_api_call(query, 1)
                text, sql, interpretation, citation = process_sse_response(response)

                if citation:
                    st.session_state.messages.append({"role": "assistant", "content": citation})
                    with st.expander("引用", expanded=True):
                        st.markdown(citation.replace("•", "\n\n-"))
                
                # アシスタントの応答をチャットに追加
                if text:
                    st.session_state.messages.append({"role": "assistant", "content": text})
                    with st.chat_message("assistant"):
                        st.markdown(text.replace("•", "\n\n-"))

                # アシスタントの応答をチャットに追加
                if interpretation:
                    st.session_state.messages.append({"role": "assistant", "content": interpretation})
                    with st.chat_message("assistant"):
                        st.markdown(interpretation.replace("•", "\n\n-"))
    
                # SQL がある場合は表示
                if sql:
                    st.markdown("### 生成された SQL")
                    st.code(sql, language="sql")
                    scn_results = run_snowflake_query(sql)
                    if scn_results:
                        st.write("### サプライチェーンクエリ結果")
                        st.dataframe(scn_results)

    def print_sidebar(self):
        set_default_sidebar()


class OptimizationPage(Page):
    def __init__(self):
        self.name = "Optimization"

    def print_page(self):
        # メインページのセットアップ
        col1, col2 = st.columns((6, 1))
        col1.title("最適化実行 🚀")

        # 問題説明ページ
        st.subheader("課題")

        st.image("demo_problem.png", caption="最適な材料移送を見つける必要があります", use_container_width=True)

        st.write('')
        st.write('''ここまでで、原材料の在庫が少ない製造工場と余剰のある工場を特定しました。
        インテリジェントアシスタントは、このようなアドホックな質問に答えるのに優れています。''')

        st.write('')
        st.dataframe(low_excess_df)
        
        st.write('''しかし、これは定期的に対処すべき課題のようです。[線形計画法](
        https://ja.wikipedia.org/wiki/%E7%B7%9A%E5%BD%A2%E8%A8%88%E7%94%BB%E6%B3%95)（線形最適化や制約計画法とも呼ばれる）を使用して、
        移送または新規購入のいずれかで各工場を補充する最もコスト効率の高い方法を特定しましょう。''')

        st.write('''線形計画法は、不等式のシステムを使用して実行可能な数学的空間を定義し、
        複数の決定変数を調整しながらその空間を探索する「ソルバー」が、
        制約条件を満たしながら、記述された目的関数に対して最も最適な決定の組み合わせを効率的に見つけます。''')

        st.write('''整数ベースの決定変数を導入することも可能で、
        その場合、問題は線形計画法から混合整数計画法に変わりますが、
        基本的な仕組みは同じです。''')

        st.write("目的関数は、利益やコストなどの値を最大化または最小化するという目標を定義します。")
        st.write("決定変数は一連の決定であり、ソルバーが目的値に影響を与えるために変更できる値です。")
        st.write(
            "制約条件は、記載された能力までしか出荷できないなど、ビジネスの現実を定義します。")

        st.write("[SciPy ライブラリ](https://scipy.org/) の linprog メソッドを使用しています。"
                 "これは Snowpark でネイティブに利用可能で、線形計画法を定義し、事実上あらゆるソルバーを使用できます。"
                 "今回は [HiGHS ソルバー](https://highs.dev/) をモデルに使用しています。")

        submitted = st.button("コスト最適化 📊")

        if submitted:
            with st.spinner("モデルを求解中..."):
                optimize_transfers()
                st.write('')
                transfer_actions = session.table("supply_chain_assistant_db.ENTITIES.TRANSFER_ACTIONS")
                st.dataframe(transfer_actions)
                st.write('')
                
                # 統計の計算
                df_pandas = transfer_actions.to_pandas()
                transfers_count = len(df_pandas[df_pandas['action_type'] == 'TRANSFER'])
                purchases_count = len(df_pandas[df_pandas['action_type'] == 'PURCHASE'])
                total_spend = df_pandas['transfer_cost'].sum()
                total_savings = df_pandas['savings'].sum()
                
                # Streamlit のカラムを使用してボックスを横に並べて表示
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(
                        f"""
                        <div class="metric-container">
                            <div class="metric-label">移送数</div>
                            <div class="metric-value">{transfers_count}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                
                with col2:
                    st.markdown(
                        f"""
                        <div class="metric-container">
                            <div class="metric-label">購入数</div>
                            <div class="metric-value">{purchases_count}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                
                with col3:
                    st.markdown(
                        f"""
                        <div class="metric-container">
                            <div class="metric-label">総支出</div>
                            <div class="metric-value">${total_spend:,.2f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                
                with col4:
                    st.markdown(
                        f"""
                        <div class="metric-container">
                            <div class="metric-label">削減額</div>
                            <div class="metric-value">${total_savings:,.2f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                
                
        
        

    def print_sidebar(self):
        set_default_sidebar()


pages = [WelcomePage(), AssistantPage(), OptimizationPage()]


def main():
    for page in pages:
        if page.name == st.session_state.page:
            page.print_page()
            page.print_sidebar()


# main()

if __name__ == "__main__":
    main()
