import streamlit as st
import json
import _snowflake
from snowflake.snowpark.context import get_active_session
from abc import ABC, abstractmethod
from scipy.optimize import linprog  # 線形計画法用
import pandas as pd
import uuid
import numpy as np
from pathlib import Path

# Streamlit in Snowflake ではアプリのルートディレクトリが変わるため、
# スクリプト自身の場所を基準にパスを解決する
_APP_DIR = Path(__file__).parent

session = get_active_session()

API_ENDPOINT = "/api/v2/cortex/agent:run"
API_TIMEOUT = 50000  # ミリ秒

CORTEX_SEARCH_SERVICES = "SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES.SUPPLY_CHAIN_INFO"
SEMANTIC_MODEL_SUPPLY_CHAIN = "@SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES.SEMANTIC_MODELS_STAGE/SUPPLY_CHAIN_ASSISTANT_MODEL.yaml"
SEMANTIC_MODEL_WEATHER = "@SUPPLY_CHAIN_ASSISTANT_DB.ENTITIES.SEMANTIC_MODELS_STAGE/WEATHER_FORECAST.yaml"

# 後方互換性のため
SEMANTIC_MODELS = SEMANTIC_MODEL_SUPPLY_CHAIN

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

/* サジェスチョンボタン */
.suggestion-btn {
    display: inline-block;
    padding: 8px 16px;
    margin: 4px;
    border-radius: 20px;
    border: 1px solid #CBD5E0;
    background-color: #F7FAFC;
    color: #2D3748;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
}

.suggestion-btn:hover {
    background-color: #EBF8FF;
    border-color: #29B5E8;
    color: #2C5282;
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
        if st.button(label="定点観測ダッシュボード 📊"):
            set_page('Dashboard')
            st.rerun()
        if st.button(label="最適化実行 🚀"):
            set_page('Optimization')
            st.rerun()
        st.markdown("")
        # 会話リセットボタン
        if st.button(label="会話をリセット 🔄"):
            st.session_state.messages = []
            st.session_state.api_messages = []
            st.rerun()
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
        return None


def _build_api_messages(api_messages):
    """会話履歴から Cortex Agents API 用のメッセージ配列を構築する。"""
    messages = []
    for msg in api_messages:
        role = msg["role"]
        text = msg["content"]
        messages.append({
            "role": role,
            "content": [{"type": "text", "text": text}]
        })
    return messages


def snowflake_api_call(api_messages, limit=10):
    """マルチターン会話対応の Cortex Agents API 呼び出し。
    
    api_messages: [{"role": "user"/"assistant", "content": "..."}] の配列
    """
    
    messages = _build_api_messages(api_messages)
    
    payload = {
        "model": "claude-3-5-sonnet",
        "messages": messages,
        "tools": [
            {
                "tool_spec": {
                    "type": "cortex_analyst_text_to_sql",
                    "name": "analyst_supply_chain"
                }
            },
            {
                "tool_spec": {
                    "type": "cortex_analyst_text_to_sql",
                    "name": "analyst_weather"
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
            "analyst_supply_chain": {"semantic_model_file": SEMANTIC_MODEL_SUPPLY_CHAIN},
            "analyst_weather": {"semantic_model_file": SEMANTIC_MODEL_WEATHER},
            "search1": {
                "name": CORTEX_SEARCH_SERVICES,
                "max_results": limit
            }
        },
        "response-instruction": "常にフレンドリーなトーンを維持し、簡潔に回答してください。「提供された情報によると」のような表現は避けてください。SQL クエリの結果に基づく回答の場合は、データの要約や分析も含めてください。"
    }
    
    try:
        resp = _snowflake.send_snow_api_request(
            "POST",
            API_ENDPOINT,
            {},
            {},
            payload,
            None,
            API_TIMEOUT,
        )
        try:
            response_content = json.loads(resp["content"])
        except json.JSONDecodeError:
            st.error("API レスポンスの解析に失敗しました。")
            if resp["status"] != 200:
                st.error(f"エラー:{resp} ")
            return None
            
        return response_content
            
    except Exception as e:
        st.error(f"リクエストエラー: {str(e)}")
        return None

def process_sse_response(response):
    """SSE レスポンスの処理。テキスト、SQL、解釈、引用を返す。"""
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
                                        citation += f"\n- {search_result.get('text', '')}"
                                    sql = result.get('json', {}).get('sql', '')
                    if content_type == 'text':
                        text += content_item.get('text', '')
                            
    except json.JSONDecodeError as e:
        st.error(f"イベント処理エラー: {str(e)}")
                
    except Exception as e:
        st.error(f"イベント処理エラー: {str(e)}")
        
    return text, sql, interpretation, citation


def render_message(msg):
    """メッセージをチャットバブル内に描画する。
    
    msg は以下の構造:
    {
        "role": "user" | "assistant",
        "content": "テキスト",
        "sql": "SELECT ...",            # optional
        "dataframe": [[...], ...],       # optional (pandas to_dict('records') 形式)
        "columns": ["col1", ...],        # optional
        "citation": "引用テキスト",        # optional
    }
    """
    with st.chat_message(msg["role"]):
        if msg.get("content"):
            st.markdown(msg["content"].replace("•", "\n\n-"))
        
        if msg.get("citation"):
            with st.expander("引用", expanded=False):
                st.markdown(msg["citation"])
        
        if msg.get("sql"):
            with st.expander("生成された SQL", expanded=False):
                st.code(msg["sql"], language="sql")
        
        if msg.get("dataframe") is not None and msg.get("columns"):
            df = pd.DataFrame(msg["dataframe"], columns=msg["columns"])
            st.dataframe(df, use_container_width=True)


# サジェスチョン質問の定義
SUGGESTION_QUESTIONS = {
    "サプライチェーン": [
        "稼働中の製造工場は何拠点ありますか？",
        "注文金額が大きい上位5社の顧客は？",
        "製造工場で在庫が不足している原材料はどれですか？",
    ],
    "天気予報": [
        "東京の今週の天気予報を教えてください",
        "明日の降水確率が50%以上の都市はどこですか？",
    ],
    "ドキュメント検索": [
        "当社のビジネスラインは何ですか？",
        "当社のサプライチェーンネットワークはどのように運営されていますか？",
    ],
}


low_excess_query = """
    WITH low_inventory AS (
        SELECT
            l.mfg_plant_id AS low_plant_id,
            mp.mfg_plant_name AS low_plant_name,
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
            mp.mfg_plant_name AS excess_plant_name,
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
    WHERE e.available_to_transfer > 0  AND l.units_needed > 0
    ORDER BY
        l.low_plant_name,
        l.material_name;
    """

low_excess_df = run_snowflake_query(low_excess_query)


def optimize_transfers():
    """
    在庫が少ない工場と余剰のある工場間の材料移送を最適化します。
    """

    low_excess_df_pd = low_excess_df.to_pandas()

    if low_excess_df_pd.empty:
        return "移送の機会が見つかりませんでした。"

    low_plants = [int(x) for x in low_excess_df_pd['LOW_PLANT_ID'].unique().tolist()]
    excess_plants = [int(x) for x in low_excess_df_pd['EXCESS_PLANT_ID'].unique().tolist()]
    materials = low_excess_df_pd['MATERIAL_ID'].unique().tolist()

    supplier_id = 999
    excess_plants.append(supplier_id)

    num_low_plants = len(low_plants)
    num_excess_plants = len(excess_plants)
    num_materials = len(materials)
    num_vars = num_low_plants * num_excess_plants * num_materials

    c = np.zeros(num_vars)
    A_ub = []
    b_ub = []
    A_eq = []
    b_eq = []
    bounds = [(0, float('inf'))] * num_vars

    for i, low_plant_id in enumerate(low_plants):
        for j, material_id in enumerate(materials):
            for k, excess_plant_id in enumerate(excess_plants):
                idx = i * num_excess_plants * num_materials + j * num_excess_plants + k

                if excess_plant_id == supplier_id:
                    material_cost = low_excess_df_pd[low_excess_df_pd['MATERIAL_ID'] == material_id]['MATERIAL_COST'].iloc[0]
                    c[idx] = material_cost
                else:
                    match = low_excess_df_pd[
                        (low_excess_df_pd['LOW_PLANT_ID'] == low_plant_id) &
                        (low_excess_df_pd['EXCESS_PLANT_ID'] == excess_plant_id) &
                        (low_excess_df_pd['MATERIAL_ID'] == material_id)
                        ]
                    if not match.empty:
                        row = match.iloc[0]
                        c[idx] = row['TRANSFER_COST_PER_UNIT']
                    else:
                        c[idx] = 1e9

    for j, material_id in enumerate(materials):
        for k, excess_plant_id in enumerate(excess_plants):
            row = [0] * num_vars
            for i in range(num_low_plants):
                idx = i * num_excess_plants * num_materials + j * num_excess_plants + k
                row[idx] = 1

            if excess_plant_id == supplier_id:
                available = 1e9
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

    for i, low_plant_id in enumerate(low_plants):
        for j, material_id in enumerate(materials):
            row = [0] * num_vars
            for k in range(num_excess_plants):
                idx = i * num_excess_plants * num_materials + j * num_excess_plants + k
                row[idx] = 1

            match = low_excess_df_pd[
                (low_excess_df_pd['LOW_PLANT_ID'] == low_plant_id) &
                (low_excess_df_pd['MATERIAL_ID'] == material_id)
                ]

            if not match.empty:
                needed = match['UNITS_NEEDED'].iloc[0]
            else:
                needed = 0

            A_eq.append(row)
            b_eq.append(needed)

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

    transfer_actions_df = session.create_dataframe(pd.DataFrame(transfer_actions))
    transfer_actions_df.write.mode("overwrite").save_as_table("supply_chain_assistant_db.entities.transfer_actions")

    return f"{len(transfer_actions)} 件の移送アクションが正常に作成されました。"
    

class WelcomePage(Page):
    def __init__(self):
        self.name = "Welcome"

    def print_page(self):
        col1, col2 = st.columns((6, 1))
        col1.title("サプライチェーンネットワークアシスタント 🚚")

        st.subheader("インテリジェントサプライチェーンアシスタントへようこそ ❄️")

        st.write('''このアシスタントは Streamlit で構築されており、サプライチェーンデータの
        セマンティック詳細を理解してText-to-SQLを実行する Cortex Analyst サービス、
        サプライチェーンに関する非構造化 PDF に対する Cortex Search サービス、
        そして質問を適切なサービスにルーティングして回答をフォーマットする
        Cortex Agents API を活用しています。''')

        st.write('')
        st.write('')
        st.write('')

        
        img_path = _APP_DIR / "cortex_image.png"
        if img_path.exists():
            st.image(img_path.read_bytes(), use_container_width=True)

    def print_sidebar(self):
        set_default_sidebar()


class AssistantPage(Page):
    def __init__(self):
        self.name = "Assistant"

    def _handle_query(self, query):
        """ユーザーの質問を処理し、API を呼び出して結果をメッセージに追加する。"""
        # ユーザーメッセージを UI 表示用リストに追加
        st.session_state.messages.append({"role": "user", "content": query})
        # API 用の会話履歴にも追加
        st.session_state.api_messages.append({"role": "user", "content": query})
        
        with st.chat_message("user"):
            st.markdown(query)
        
        with st.chat_message("assistant"):
            with st.spinner("リクエストを処理中..."):
                response = snowflake_api_call(st.session_state.api_messages, 5)
                text, sql, interpretation, citation = process_sse_response(response)

                # アシスタントのメッセージを構築
                assistant_msg = {"role": "assistant", "content": ""}
                
                # API 用の会話履歴に追加するテキストを構築
                api_response_text = ""

                if text:
                    assistant_msg["content"] = text
                    api_response_text += text
                    st.markdown(text.replace("•", "\n\n-"))

                if interpretation:
                    if assistant_msg["content"]:
                        assistant_msg["content"] += "\n\n" + interpretation
                    else:
                        assistant_msg["content"] = interpretation
                    api_response_text += "\n" + interpretation
                    st.markdown(interpretation.replace("•", "\n\n-"))

                if citation:
                    assistant_msg["citation"] = citation
                    with st.expander("引用", expanded=False):
                        st.markdown(citation)

                if sql:
                    assistant_msg["sql"] = sql
                    with st.expander("生成された SQL", expanded=False):
                        st.code(sql, language="sql")
                    
                    scn_results = run_snowflake_query(sql)
                    if scn_results is not None:
                        try:
                            df_pandas = scn_results.to_pandas()
                            st.dataframe(df_pandas, use_container_width=True)
                            assistant_msg["dataframe"] = df_pandas.values.tolist()
                            assistant_msg["columns"] = df_pandas.columns.tolist()
                            
                            # クエリ結果の要約を API 用履歴に追加（ドリルダウン用）
                            row_count = len(df_pandas)
                            col_names = ", ".join(df_pandas.columns.tolist()[:10])
                            preview = df_pandas.head(5).to_string(index=False)
                            api_response_text += f"\n\n[クエリ結果: {row_count}行, カラム: {col_names}]\n{preview}"
                        except Exception:
                            st.dataframe(scn_results)

                if not assistant_msg["content"] and not sql:
                    assistant_msg["content"] = "申し訳ありません。回答を生成できませんでした。別の質問をお試しください。"
                    api_response_text = assistant_msg["content"]
                    st.markdown(assistant_msg["content"])

                # メッセージ履歴に保存
                st.session_state.messages.append(assistant_msg)
                
                # API 用履歴にアシスタント応答を追加
                if api_response_text:
                    st.session_state.api_messages.append({
                        "role": "assistant",
                        "content": api_response_text.strip()
                    })

    def print_page(self):
        st.title("インテリジェントサプライチェーンネットワークアシスタント")
        
        # セッション状態の初期化
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'api_messages' not in st.session_state:
            st.session_state.api_messages = []
        if 'pending_suggestion' not in st.session_state:
            st.session_state.pending_suggestion = None
    
        # 既存のメッセージ履歴を表示
        for msg in st.session_state.messages:
            render_message(msg)

        # まだ会話がない場合、サジェスチョン質問を表示
        if not st.session_state.messages:
            st.markdown("#### 質問してみましょう")
            st.markdown("以下のサンプル質問をクリックするか、下のチャット欄に自由に入力してください。")
            st.markdown("")
            
            for category, questions in SUGGESTION_QUESTIONS.items():
                st.markdown(f"**{category}**")
                cols = st.columns(len(questions))
                for i, q in enumerate(questions):
                    with cols[i]:
                        if st.button(q, key=f"suggestion_{category}_{i}", use_container_width=True):
                            st.session_state.pending_suggestion = q
                            st.rerun()
                st.markdown("")
        
        # サジェスチョンから送信された質問を処理
        if st.session_state.pending_suggestion:
            query = st.session_state.pending_suggestion
            st.session_state.pending_suggestion = None
            self._handle_query(query)

        # チャット入力
        if query := st.chat_input("何について知りたいですか？（ドリルダウンも可能です）"):
            self._handle_query(query)

    def print_sidebar(self):
        set_default_sidebar()


class DashboardPage(Page):
    def __init__(self):
        self.name = "Dashboard"

    def _query_to_pandas(self, sql):
        """SQLを実行してpandas DataFrameを返す。失敗時はNone。"""
        try:
            return session.sql(sql).to_pandas()
        except Exception as e:
            st.error(f"クエリエラー: {str(e)}")
            return None

    def print_page(self):
        st.title("定点観測ダッシュボード 📊")

        # --- 事業ラインフィルタ ---
        all_lines = ["AUTOMOTIVE", "ELECTRONICS", "CONSTRUCTION", "ENERGY", "TEXTILE"]
        selected_lines = st.multiselect(
            "事業ラインでフィルタ", all_lines, default=all_lines, key="dashboard_filter"
        )
        if not selected_lines:
            st.warning("事業ラインを1つ以上選択してください。")
            return

        lines_sql = ", ".join(f"'{bl}'" for bl in selected_lines)

        # ========== KPI メトリクス ==========
        kpi_sql = f"""
        SELECT
            (SELECT COUNT(*) FROM supply_chain_assistant_db.entities.mfg_plant
             WHERE is_active = TRUE AND business_line IN ({lines_sql})) AS active_plants,
            (SELECT COUNT(*) FROM supply_chain_assistant_db.entities.orders o
             JOIN supply_chain_assistant_db.entities.product p ON o.product_id = p.product_id
             WHERE p.business_line IN ({lines_sql})) AS total_orders,
            (SELECT COALESCE(SUM(total_price), 0) FROM supply_chain_assistant_db.entities.orders o
             JOIN supply_chain_assistant_db.entities.product p ON o.product_id = p.product_id
             WHERE p.business_line IN ({lines_sql})) AS total_order_value,
            (SELECT COUNT(*) FROM supply_chain_assistant_db.entities.mfg_inventory i
             JOIN supply_chain_assistant_db.entities.mfg_plant mp ON i.mfg_plant_id = mp.mfg_plant_id
             WHERE i.quantity_on_hand < i.safety_stock_level
               AND i.material_id IS NOT NULL
               AND mp.business_line IN ({lines_sql})) AS inventory_alerts
        """
        kpi_df = self._query_to_pandas(kpi_sql)

        if kpi_df is not None and not kpi_df.empty:
            row = kpi_df.iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("稼働中の工場数", f"{int(row['ACTIVE_PLANTS']):,}")
            c2.metric("総注文件数", f"{int(row['TOTAL_ORDERS']):,}")
            c3.metric("総注文金額", f"¥{row['TOTAL_ORDER_VALUE']:,.0f}")
            c4.metric("在庫アラート数", f"{int(row['INVENTORY_ALERTS']):,}")

        st.markdown("---")

        # ========== 中段: 事業ライン別注文金額 & 注文ステータス ==========
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("事業ライン別 注文金額")
            orders_by_bl_sql = f"""
            SELECT p.business_line AS "事業ライン",
                   SUM(o.total_price) AS "注文金額"
            FROM supply_chain_assistant_db.entities.orders o
            JOIN supply_chain_assistant_db.entities.product p ON o.product_id = p.product_id
            WHERE p.business_line IN ({lines_sql})
            GROUP BY p.business_line
            ORDER BY "注文金額" DESC
            """
            orders_bl_df = self._query_to_pandas(orders_by_bl_sql)
            if orders_bl_df is not None and not orders_bl_df.empty:
                st.bar_chart(orders_bl_df.set_index("事業ライン"))

        with col_right:
            st.subheader("注文ステータス別 件数")
            orders_status_sql = f"""
            SELECT o.order_status AS "ステータス",
                   COUNT(*) AS "件数"
            FROM supply_chain_assistant_db.entities.orders o
            JOIN supply_chain_assistant_db.entities.product p ON o.product_id = p.product_id
            WHERE p.business_line IN ({lines_sql})
            GROUP BY o.order_status
            ORDER BY "件数" DESC
            """
            orders_status_df = self._query_to_pandas(orders_status_sql)
            if orders_status_df is not None and not orders_status_df.empty:
                st.bar_chart(orders_status_df.set_index("ステータス"))

        st.markdown("---")

        # ========== 下段: 在庫アラート一覧 & 工場概要 ==========
        col_left2, col_right2 = st.columns(2)

        with col_left2:
            st.subheader("在庫アラート一覧")
            st.caption("安全在庫を下回っている原材料")
            alert_sql = f"""
            SELECT mp.mfg_plant_name AS "工場名",
                   rm.material_name AS "材料名",
                   i.quantity_on_hand AS "手持在庫",
                   i.safety_stock_level AS "安全在庫",
                   i.days_forward_coverage AS "前方カバー日数"
            FROM supply_chain_assistant_db.entities.mfg_inventory i
            JOIN supply_chain_assistant_db.entities.mfg_plant mp ON i.mfg_plant_id = mp.mfg_plant_id
            JOIN supply_chain_assistant_db.entities.raw_material rm ON i.material_id = rm.material_id
            WHERE i.quantity_on_hand < i.safety_stock_level
              AND mp.business_line IN ({lines_sql})
            ORDER BY i.days_forward_coverage ASC
            """
            alert_df = self._query_to_pandas(alert_sql)
            if alert_df is not None and not alert_df.empty:
                st.dataframe(alert_df, use_container_width=True, hide_index=True)
            else:
                st.info("在庫アラートはありません。")

        with col_right2:
            st.subheader("事業ライン別 工場・従業員数")
            plant_summary_sql = f"""
            SELECT business_line AS "事業ライン",
                   COUNT(*) AS "工場数",
                   SUM(number_of_employees) AS "従業員数"
            FROM supply_chain_assistant_db.entities.mfg_plant
            WHERE is_active = TRUE
              AND business_line IN ({lines_sql})
            GROUP BY business_line
            ORDER BY "従業員数" DESC
            """
            plant_df = self._query_to_pandas(plant_summary_sql)
            if plant_df is not None and not plant_df.empty:
                st.bar_chart(plant_df.set_index("事業ライン")["従業員数"])
                st.dataframe(plant_df, use_container_width=True, hide_index=True)

    def print_sidebar(self):
        set_default_sidebar()


class OptimizationPage(Page):
    def __init__(self):
        self.name = "Optimization"

    def print_page(self):
        col1, col2 = st.columns((6, 1))
        col1.title("最適化実行 🚀")

        st.subheader("課題")

        img_path = _APP_DIR / "demo_problem.png"
        if img_path.exists():
            st.image(img_path.read_bytes(), caption="最適な材料移送を見つける必要があります", use_container_width=True)

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
                
                df_pandas = transfer_actions.to_pandas()
                transfers_count = len(df_pandas[df_pandas['action_type'] == 'TRANSFER'])
                purchases_count = len(df_pandas[df_pandas['action_type'] == 'PURCHASE'])
                total_spend = df_pandas['transfer_cost'].sum()
                total_savings = df_pandas['savings'].sum()
                
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


pages = [WelcomePage(), AssistantPage(), DashboardPage(), OptimizationPage()]


def main():
    for page in pages:
        if page.name == st.session_state.page:
            page.print_page()
            page.print_sidebar()


# main()

if __name__ == "__main__":
    main()
