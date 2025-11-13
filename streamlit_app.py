import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="성적 데이터 시각화", layout="wide")

st.title("📊 성적 데이터 시각화 앱")
st.write("CSV 파일을 업로드하고 다양한 그래프로 성적 데이터를 분석하세요!")

# ========== 파일 업로드 ==========
st.header("1️⃣ CSV 파일 업로드")
uploaded_file = st.file_uploader("CSV 파일을 선택하세요", type=["csv"])

if uploaded_file is not None:
    # 데이터 로드
    df = pd.read_csv(uploaded_file)
    
    st.success("파일이 성공적으로 업로드되었습니다!")
    st.subheader("📋 데이터 미리보기")
    st.dataframe(df.head(10))
    
    # 데이터 정보 표시
    st.subheader("📈 데이터 정보")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("행 수", len(df))
    with col2:
        st.metric("열 수", len(df.columns))
    with col3:
        st.metric("숫자형 열", len(df.select_dtypes(include=[np.number]).columns))
    
    # 숫자형 열만 추출
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) == 0:
        st.error("숫자형 데이터가 없습니다. CSV 파일을 확인해주세요.")
    else:
        st.divider()
        
        # ========== 그래프 옵션 선택 ==========
        st.header("2️⃣ 시각화 옵션 선택")
        
        chart_options = ["📊 히스토그램", "📈 막대그래프", "🔵 산점도", "📦 상자그림"]
        selected_chart = st.radio("그래프 유형을 선택하세요", chart_options, horizontal=True)
        
        st.divider()
        
        # ========== 히스토그램 ==========
        if selected_chart == "📊 히스토그램":
            st.subheader("📊 히스토그램")
            st.write("**설명**: 한 변수의 분포를 확인할 수 있습니다.")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                hist_col = st.selectbox("변수 선택", numeric_cols, key="hist_col")
            
            if hist_col:
                bins = st.slider("구간 수", min_value=5, max_value=50, value=20, key="hist_bins")
                
                fig = px.histogram(
                    df,
                    x=hist_col,
                    nbins=bins,
                    title=f"{hist_col} 분포",
                    labels={hist_col: hist_col},
                    color_discrete_sequence=["#636EFA"]
                )
                fig.update_layout(
                    xaxis_title=hist_col,
                    yaxis_title="빈도",
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 통계 정보
                st.subheader("📊 통계 정보")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("평균", f"{df[hist_col].mean():.2f}")
                with col2:
                    st.metric("중앙값", f"{df[hist_col].median():.2f}")
                with col3:
                    st.metric("표준편차", f"{df[hist_col].std():.2f}")
                with col4:
                    st.metric("최솟값", f"{df[hist_col].min():.2f}")
                with col5:
                    st.metric("최댓값", f"{df[hist_col].max():.2f}")
        
        # ========== 막대그래프 ==========
        elif selected_chart == "📈 막대그래프":
            st.subheader("📈 막대그래프")
            st.write("**설명**: 범주형 데이터와 숫자형 데이터의 관계를 보여줍니다.")
            
            # 범주형 열 추출
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            if len(categorical_cols) > 0:
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    bar_cat = st.selectbox("범주 선택", categorical_cols, key="bar_cat")
                with col2:
                    bar_val = st.selectbox("값 선택", numeric_cols, key="bar_val")
                with col3:
                    agg_func = st.selectbox("집계 함수", ["평균", "합계", "개수"], key="bar_agg")
                
                if bar_cat and bar_val:
                    # 데이터 집계
                    agg_dict = {"평균": "mean", "합계": "sum", "개수": "count"}
                    bar_data = df.groupby(bar_cat)[bar_val].agg(agg_dict[agg_func]).reset_index()
                    
                    fig = px.bar(
                        bar_data,
                        x=bar_cat,
                        y=bar_val,
                        title=f"{bar_cat}별 {bar_val} ({agg_func})",
                        labels={bar_cat: bar_cat, bar_val: bar_val},
                        color_discrete_sequence=["#EF553B"]
                    )
                    fig.update_layout(hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("범주형 데이터가 없습니다. 숫자형 데이터만으로는 막대그래프를 그릴 수 없습니다.")
        
        # ========== 산점도 ==========
        elif selected_chart == "🔵 산점도":
            st.subheader("🔵 산점도")
            st.write("**설명**: 두 변수 간의 관계를 확인할 수 있습니다.")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                scatter_x = st.selectbox("X축 변수 선택", numeric_cols, key="scatter_x")
            with col2:
                scatter_y = st.selectbox("Y축 변수 선택", numeric_cols, index=1 if len(numeric_cols) > 1 else 0, key="scatter_y")
            
            # 색상 옵션 (선택사항)
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            color_opt = [None] + categorical_cols
            with col3:
                scatter_color = st.selectbox("색상 그룹화 (선택사항)", color_opt, key="scatter_color", format_func=lambda x: "없음" if x is None else x)
            
            if scatter_x and scatter_y:
                fig = px.scatter(
                    df,
                    x=scatter_x,
                    y=scatter_y,
                    color=scatter_color,
                    title=f"{scatter_x} vs {scatter_y}",
                    labels={scatter_x: scatter_x, scatter_y: scatter_y},
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig.update_layout(hovermode="closest")
                st.plotly_chart(fig, use_container_width=True)
        
        # ========== 상자그림 ==========
        elif selected_chart == "📦 상자그림":
            st.subheader("📦 상자그림")
            st.write("**설명**: 데이터의 분포와 이상치를 시각적으로 확인할 수 있습니다.")
            
            # 범주형 열 추출
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            if len(categorical_cols) > 0:
                col1, col2 = st.columns([1, 2])
                with col1:
                    box_cat = st.selectbox("범주 선택", categorical_cols, key="box_cat")
                with col2:
                    box_val = st.selectbox("값 선택", numeric_cols, key="box_val")
                
                if box_cat and box_val:
                    fig = px.box(
                        df,
                        x=box_cat,
                        y=box_val,
                        title=f"{box_cat}별 {box_val} 분포",
                        labels={box_cat: box_cat, box_val: box_val},
                        color_discrete_sequence=["#00CC96"]
                    )
                    fig.update_layout(hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("범주형 데이터가 없습니다. 상자그림을 그리려면 범주형 데이터가 필요합니다.")
else:
    st.info("📁 위에서 CSV 파일을 업로드하여 시작하세요!")
