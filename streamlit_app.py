import os

import pandas as pd
import plotly.express as px
import streamlit as st

SALES_HISTORY_PATH = "./data/sales_history.csv"
ITEM_CATEGORIES_PATH = "./data/item_categories.csv"
CATEGORY_NAMES_PATH = "./data/category_names.csv"
TEST_PATH = "./data/test.csv"

# ---- ---- ---- ----

DEV_TYPE = "開発モード"
NOMAL_TYPE = "通常モード"

# ---- ---- ---- ----

def app(dev_mode):
    if not dev_mode:
        data_expander = st.expander("データ登録", expanded=True)
        with data_expander:
            col00, col01 = st.columns(2)
            with col00:
                st.subheader("販売実績データ")
                sales_history_file = st.file_uploader(
                    "Competitionサイトで公開された販売実績データファイル(sales_history.csv)をアップロード",
                    type="csv",
                )

            with col01:
                st.subheader("評価用データ")
                test_file = st.file_uploader(
                    "Competitionサイトで公開された評価用データ(test.csv)をアップロード",
                    type="csv",
                )

            col10, col11 = st.columns(2)
            with col10:
                st.subheader("商品カテゴリーデータ")
                item_categories_file = st.file_uploader(
                    "Competitionサイトで公開された商品カテゴリーデータファイル(item_categories.csv)をアップロード",
                    type="csv",
                )

            with col11:
                st.subheader("カテゴリ名称データ")
                category_names_file = st.file_uploader(
                    "Competitionサイトで公開されたカテゴリ名称データファイル(category_names.csv)をアップロード",
                    type="csv",
                )

    if dev_mode:
        sales_history_df = pd.read_csv(SALES_HISTORY_PATH)
        item_categories_df = pd.read_csv(ITEM_CATEGORIES_PATH)
        category_names_df = pd.read_csv(CATEGORY_NAMES_PATH)
        test_df = pd.read_csv(TEST_PATH)

    else:
        if sales_history_file is not None:
            sales_history_df = pd.read_csv(sales_history_file)
        if item_categories_file is not None:
            item_categories_df = pd.read_csv(item_categories_file)
        if category_names_file is not None:
            category_names_df = pd.read_csv(category_names_file)
        if test_file is not None:
            test_df = pd.read_csv(test_file)

    calc_enable = False

    if not dev_mode:
        if (
            sales_history_file is not None
            and item_categories_file is not None
            and category_names_file is not None
            and test_file is not None
        ):
            calc_enable = True
    else:
        calc_enable = True

    if calc_enable:
        # ---- VVV 計算処理 VVV ----

        # test_dfに存在する商品IDと店舗IDの組み合わせを抽出
        test_item_store_combinations = test_df[['商品ID', '店舗ID']].drop_duplicates()

        # train_dfを、test_item_store_combinationsに存在する組み合わせのみに絞り込む
        # inner join を使用することで、両方のDataFrameに存在する組み合わせのみが残る
        sales_history_df_pickup = pd.merge(sales_history_df, test_item_store_combinations, on=['商品ID', '店舗ID'], how='inner')

        sales_by_shop_item = sales_history_df_pickup.groupby(['店舗ID', '商品ID'])['売上個数'].sum().reset_index()

        sales_by_shop_item['店舗ID'] = sales_by_shop_item['店舗ID'].astype(str)
        sales_by_shop_item['商品ID'] = sales_by_shop_item['商品ID'].astype(str)

        st.subheader("店舗ID毎の売上個数が多い商品ID (Treemap)")
        fig = px.treemap(
            sales_by_shop_item,
            path=['店舗ID', '商品ID'],
            values='売上個数',
            title='店舗ID毎の売上個数が多い商品ID',
            color='売上個数',
            color_continuous_scale='RdBu',
            color_continuous_midpoint=sales_by_shop_item['売上個数'].mean()
        )
        fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("店舗ID毎の売上個数が多い商品ID (DataFrame)")
        st.dataframe(sales_by_shop_item)

        st.divider()

        sales_history_df_pickup2 = pd.merge(sales_history_df_pickup, item_categories_df, on='商品ID', how='left')
        sales_history_df_pickup2 = pd.merge(sales_history_df_pickup2, category_names_df, on='商品カテゴリID', how='left')

        sales_history_df_pickup2['メインカテゴリ名'] = sales_history_df_pickup2['商品カテゴリ名'].apply(lambda x: x.split(' - ')[0] if pd.notnull(x) and ' - ' in x else x)
        sales_history_df_pickup2['サブカテゴリ名'] = sales_history_df_pickup2['商品カテゴリ名'].apply(lambda x: x.split(' - ')[1] if pd.notnull(x) and ' - ' in x else None)

        sales_by_categories = sales_history_df_pickup2.groupby(['メインカテゴリ名', 'サブカテゴリ名'])['売上個数'].sum().reset_index()

        st.subheader("カテゴリ毎の売上個数が多い商品ID (Treemap)")
        fig = px.treemap(
            sales_by_categories,
            path=['メインカテゴリ名', 'サブカテゴリ名'],
            values='売上個数',
            title='カテゴリ毎の売上個数が多い商品ID',
            color='売上個数',
            color_continuous_scale='RdBu',
            color_continuous_midpoint=sales_by_categories['売上個数'].mean()
        )
        fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("カテゴリ毎の売上個数が多い商品ID (DataFrame)")
        st.dataframe(sales_by_categories)

        # ---- AAA 計算処理 AAA ----


# ---- ---- ---- ----

if __name__ == "__main__":
    st.set_page_config(
        page_title="MDXQ2025 テーマ1 演習03 EDA 共有アプリ", layout="wide",
        page_icon=":computer:"
    )
    st.title("MDXQ2025 テーマ1 演習03 EDA 共有アプリ")

    dev_mode_enable = False
    if os.path.isfile(TEST_PATH):
        dev_mode_enable = True

    fix_dev_mode = False
    # fix_dev_mode = True

    dev_mode = False
    if dev_mode_enable:
        if not fix_dev_mode:
            select_dev_mode = st.radio(
                label="モード選択",
                options=[DEV_TYPE, NOMAL_TYPE],
                horizontal=True,
                label_visibility="hidden",
            )
            if select_dev_mode == DEV_TYPE:
                dev_mode = True
        else:
            dev_mode = True

    # dev_mode = False # 強制的に通常モードにする

    app(dev_mode)
