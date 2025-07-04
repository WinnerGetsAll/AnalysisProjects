# Encodeing by UTF8
try:
	import pandas as pd
	import numpy as np
	import matplotlib.pyplot as plt
	import seaborn as sns
	import streamlit as st
	import plotly.graph_objects as go
	from plotly.subplots import make_subplots
	import plotly.express as px
	import joypy
	from matplotlib import cm
	import datetime
	import pandas_datareader as pdr
	import os
	import sys
except ModuleNotFoundError as e:
	print(e)

try:
	base_dir1 = os.path.dirname(os.path.abspath(__file__))
except NameError:
	base_dir1 = os.getcwd()
file_path1 = os.path.join(base_dir1, 'query-hive-451961.xlsx')

sourcedata = pd.read_excel(file_path1)
table = pd.pivot_table(sourcedata, index=['model_id', 'dt'], values=['click_uv', 'expose_uv', 'click_pv', 'expose_pv'],
                       aggfunc='sum')
table['uvctr'] = table['click_uv'] / table['expose_uv']
table['pvctr'] = table['click_pv'] / table['expose_pv']

flow_group1 = table.loc['f03']
flow_group2 = table.loc['f04']

dt1 = table.index.levels[1].unique().sort_values()

dt = pd.to_datetime(dt1, format='%Y-%m-%d')

flow_group1_exposePV = flow_group1['expose_pv'] / 100000
flow_group2_exposePV = flow_group2['expose_pv'] / 100000
flow_group1_pvctr = flow_group1['pvctr'] * 100
flow_group2_pvctr = flow_group2['pvctr'] * 100

flow_group1_exposeUV = flow_group1['expose_uv'] / 100000
flow_group2_exposeUV = flow_group2['expose_uv'] / 100000
flow_group1_uvctr = flow_group1['uvctr'] * 100
flow_group2_uvctr = flow_group2['uvctr'] * 100

Rpvctr = (flow_group1_pvctr - flow_group2_pvctr) / flow_group2_pvctr * 100
Ruvctr = (flow_group1_uvctr - flow_group2_uvctr) / flow_group2_uvctr * 100
AveRpvctr = pd.Series(np.full(len(dt), np.average(Rpvctr)))
AveRuvctr = pd.Series(np.full(len(dt), np.average(Ruvctr)))

fig0 = go.Figure()
fig0.add_trace(
	go.Line(
		x=dt,
		y=Ruvctr,
		name='Uvctr相对提升'
	)
)
fig0.add_trace(
	go.Line(
		x=dt,
		y=Rpvctr,
		name='Pvctr相对提升'
	)
)
fig0.add_trace(
	go.Line(
		x=dt,
		y=AveRuvctr,
		name='平均Uvctr相对提升'
	)
)
fig0.add_trace(
	go.Line(
		x=dt,
		y=AveRpvctr,
		name='平均Pvctr相对提升'
	)
)

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(
	go.Bar(
		x=dt,
		y=flow_group1_exposePV,
		name='试验组曝光PV',
	)
)
fig.add_trace(
	go.Bar(
		x=dt,
		y=flow_group2_exposePV,
		name='对照组曝光Pv',
	)
)
fig.add_trace(
	go.Line(
		x=dt,
		y=flow_group1_pvctr,
		yaxis='y2',
		name='试验组Pvctr'
	)
)
fig.add_trace(
	go.Line(
		x=dt,
		y=flow_group2_pvctr,
		yaxis='y2',
		name='对照组Pvctr'
	)
)

fig1 = make_subplots(specs=[[{"secondary_y": True}]])
fig1.add_trace(
	go.Bar(
		x=dt,
		y=flow_group1_exposeUV,
		name='试验组曝光Uv', )
)

fig1.add_trace(
	go.Bar(
		x=dt,
		y=flow_group2_exposeUV,
		name='对照组曝光Uv'
	)
)

fig1.add_trace(
	go.Line(
		x=dt,
		y=flow_group1_uvctr,
		name='试验组Uvctr',
		yaxis='y2'
	)
)

fig1.add_trace(
	go.Line(
		x=dt,
		y=flow_group2_uvctr,
		name='对照组Uvctr',
		yaxis='y2',
	)
)

data = [[1, 25, 30, 50, 1], [20, 1, 60, 80, 30], [30, 60, 1, 5, 20]]
fig4 = px.imshow(data,
                 labels=dict(x="日期", y="时段", color="Productivity"),
                 x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                 y=['Morning', 'Afternoon', 'Evening']
                 )
fig4.update_xaxes(side="top")

start_date = datetime.datetime(2014, 1, 1)
end_date = datetime.datetime(2022, 12, 31)
ticker_list = ['SP500']
df = pdr.DataReader(ticker_list, 'fred', start_date, end_date)
df_ = df.dropna()
df_['daily_r'] = df_['SP500'].pct_change() * 100
df_['Year'] = pd.DatetimeIndex(df_.index).year

fig5, ax = plt.subplots(figsize=(6, 4))
joypy.joyplot(df_, by="Year", column="daily_r", ax=ax,
              range_style='own', grid="y",
              linewidth=1, legend=False,
              colormap=cm.autumn_r, fade=True)

base_dir2 = os.path.dirname(os.path.abspath(__file__))
file_path2 = os.path.join(base_dir2, 'query-hive-486841.xlsx')

datas = pd.read_excel(file_path2)
data = datas.loc[:,
       ['t1.algorithm_type', 't2.brand_name', 't3.launch_price', 't4.goods_label', 't4.similar_business_name',
        't4.price']]
data['launch_cut'] = pd.cut(data['t3.launch_price'], [1000, 3000, 5000, 8000, 10000])
data['click_price_cut'] = pd.cut(data['t4.price'], [1000, 3000, 5000, 8000, 10000])

fig2 = px.parallel_categories(data, dimensions=['t2.brand_name', 't4.goods_label', 't4.similar_business_name'],
                              labels={'t2.brand_name': '用户持有品牌', 't4.goods_label': '点击终端类型',
                                      't4.similar_business_name': '点击品牌'},
                              color='t4.price', color_continuous_scale=px.colors.sequential.Inferno)


df = px.data.gapminder().query("year == 2007").query("continent == 'Europe'")
df.loc[df['pop'] < 2.e6, 'country'] = 'Other countries'
fig3 = px.pie(df, values='pop', names='country', title='终端二级类别订单占比')
fig3.update_traces(hole=.68)

Rd = np.random.RandomState(42)
data = Rd.randint(1000, size=(10, 3))
Tindex = pd.bdate_range(start='2025-06-17', periods=10)
data = pd.DataFrame(data, index=Tindex, columns=['合约机', '裸机', '泛智能'])

st.title('全触点终端模型指标分析')
col4, col5 = st.columns(2)
col4.subheader('日用户活跃情况')
col4.plotly_chart(fig4)
col5.subheader('访问变化情况')
col5.pyplot(fig5)

st.subheader('点击率相对提升变化/点击率提升平均变化')
st.plotly_chart(fig0)

col1, col2 = st.columns(2)
col1.subheader('曝光Pv/Pvctr详情')
col1.plotly_chart(fig)

col2.subheader('曝光Uv/Uvctr详情')
col2.plotly_chart(fig1)

st.subheader('价格品牌偏好')
st.plotly_chart(fig2)

col3, col4 = st.columns(2)
col3.subheader('终端二级类别订单占比')
col3.plotly_chart(fig3)
col4.subheader('终端二级类别商品销售详情')
col4.write(data)

