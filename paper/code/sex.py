import pandas as pd
import pymongo
from bokeh import charts
from bokeh.io import push_notebook, show, output_notebook
output_notebook()

client = pymongo.MongoClient()
db = client['hfut']
student_df = pd.DataFrame(list(db['student'].find()), columns=['学号', '姓名', '性别'])
student_df['入学年份'] = student_df['学号'] // 1000000
p = charts.Bar(student_df,label='入学年份', values='性别', agg='count', stack='性别')
show(p)
