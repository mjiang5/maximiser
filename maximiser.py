import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import datetime as dt
plt.style.use('classic')

st.title('MaxiMiser')
st.write('')
st.write('Simple bonus optimization strategy of opening new checking or saving accounts')

scraped_df = pd.read_csv('data/real_time_bonuses.csv')
scraped_df = scraped_df.iloc[:, 1:]
scraped_df = scraped_df.drop(columns=['post_link'])

scraped_df.rename(columns={'expiration_date': 'open_date'}, inplace=True)

scraped_df['month'] = scraped_df['open_date'].apply(lambda x: pd.to_datetime(x).month)
scraped_df['keep_time'] = scraped_df['keep_time'].astype('int')
scraped_df['ini_month'] = scraped_df['month']+1
scraped_df['end_month'] = scraped_df['ini_month'] + scraped_df['keep_time']-1

bonus_df = scraped_df

st.sidebar.subheader('Your requirements:')
budget = st.sidebar.number_input('Maximum monthly direct deposit:', min_value=100.0, step=500.0)
num_account = st.sidebar.number_input('Maximum number of accounts:', min_value=1.0, step=1.0)


######## build the optimal strategy ###########
from pulp import *

problem = LpProblem("Bonus Portfolio", LpMaximize)

bonus_title = list(bonus_df['title'])
months = list(range(2, 14))

bonus_amount = dict(zip(bonus_title, bonus_df['bonus']))
monthly_dd_amount = dict(zip(bonus_title, bonus_df['monthly_dd']))
account_keeping_time = dict(zip(bonus_title, bonus_df['keep_time']))
ini_month = dict(zip(bonus_title, bonus_df['ini_month']))
end_month = dict(zip(bonus_title, bonus_df['end_month']))
open_date = dict(zip(bonus_title, bonus_df['open_date']))

# vector of variables
holdings = LpVariable.dicts("offer", bonus_title, cat='Binary')

for m in months:
    problem += lpSum([monthly_dd_amount[i]*holdings[i] for i in bonus_title if (m<=end_month[i] and m>=ini_month[i])]) <= budget
    
problem += lpSum([holdings[i] for i in bonus_title]) <= num_account

# objective function
problem += lpSum([bonus_amount[i]*holdings[i] for i in bonus_title])

problem.solve()

status = LpStatus[problem.status]
        
total_return = value(problem.objective)


optimal_holding = pd.DataFrame(columns=['Offer', 'Monthly Direct Deposit', 'Bonus', 'Open Date', 'Keeping Time (Month)'])

i = 0
for v in holdings:
    if holdings[v].varValue == 1:
        optimal_holding.loc[i, 'Offer'] = v
        optimal_holding.loc[i, 'Monthly Direct Deposit'] = monthly_dd_amount[v]
        optimal_holding.loc[i, 'Bonus'] = bonus_amount[v]
        optimal_holding.loc[i, 'Open Date'] = open_date[v]
        optimal_holding.loc[i, 'Keeping Time (Month)'] = account_keeping_time[v] #int()?
        i += 1



base_day = dt.datetime(2020, 1, 1)

optimal_holding['Close Date'] = optimal_holding['Keeping Time (Month)'].apply(lambda x: dt.timedelta(31*x))
optimal_holding['Close Date'] += optimal_holding['Open Date'].apply(pd.to_datetime)
optimal_holding['Close Date'] = optimal_holding['Close Date'].dt.strftime('%m-%d-%Y')

optimal_holding['Open Date'] = pd.to_datetime(optimal_holding['Open Date'])
optimal_holding['Close Date'] = pd.to_datetime(optimal_holding['Close Date'])

optimal_holding['open'] = optimal_holding['Open Date']-base_day
optimal_holding['close'] = optimal_holding['Close Date']-base_day

optimal_holding['Open Date'] = optimal_holding['Open Date'].dt.strftime('%m-%d-%Y')
optimal_holding['Close Date'] = optimal_holding['Close Date'].dt.strftime('%m-%d-%Y')



open_date = [optimal_holding.loc[i, 'open'].days for i in optimal_holding.index]
close_date = [optimal_holding.loc[i, 'close'].days for i in optimal_holding.index]



offers = ['Bonus {}'.format(i) for i in optimal_holding.index]

from matplotlib.ticker import MultipleLocator
                               
fig1 = plt.figure(figsize=(18, 5))
ax = fig1.add_subplot(111)

for i in range(len(open_date)):
    plt.plot([open_date[i], close_date[i]], [i+0.5, i+0.5], lw=55, c='blue')  #########


plt.xlim(0, 365*2)
plt.ylim(0, len(open_date))
ax.set_aspect(40)
plt.tick_params(axis='x', which='both', bottom=False, top=False)
plt.tick_params(axis='y', which='both', left=False, right=False)
xlist = [0, 90, 181, 273, 365, 455, 546, 638, 730]
xlabels=['2019-12', '2020-03', '2020-06', '2020-9', '2020-12', '2021-03', '2021-06', '2021-09', '2021-12']
plt.xticks(xlist, xlabels)
plt.yticks(np.arange(0.5, len(open_date)+0.5), offers)

ax.xaxis.grid(True, which='major', color='w', lw=1, linestyle='solid')
ax.yaxis.grid(True, which='minor', color='w', lw=1, linestyle='solid')
ax.xaxis.set_major_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(1))

# hide axis spines
for spine in ax.spines.values():
    spine.set_visible(False)
    
ax.set_facecolor('lavender')
fig1.patch.set_alpha(0.)
plt.tight_layout()

st.sidebar.subheader('')
st.sidebar.subheader('')


holding_cols = ['Offer', 'Open Date', 'Keeping Time (Month)', 'Close Date', 'Monthly Direct Deposit', 'Bonus']
st.subheader('Optimal Strategy:')
st.table(optimal_holding[holding_cols])
st.subheader('Optimal Return:')
st.write(total_return)
st.pyplot(fig1, dpi=200)
    
    

######## build the lazy strategy ###########
lazy_df = bonus_df
lazy_budget = budget
lazy_num_account = 1
lazy_holding = pd.DataFrame()

lazy_df = lazy_df[lazy_df['monthly_dd'] <= lazy_budget]
lazy_df = lazy_df.sort_values(by=['bonus'], ascending=False)
lazy = lazy_df.iloc[0]
lazy_holding = lazy_holding.append(lazy_df.iloc[0])

lazy_total_return = np.sum(lazy_holding['bonus'])

# print('Total return: '+ str(lazy_total_return))
# print()

lazy_holding.reset_index(drop=True, inplace=True)

cols = ['title', 'monthly_dd', 'bonus', 'open_date', 'keep_time']

lazy_holding = lazy_holding[cols].rename(columns={'title': 'Offer',
                                                  'monthly_dd': 'Monthly Direct Deposit',
                                                  'bonus': 'Bonus',
                                                  'open_date': 'Open Date',
                                                  'keep_time': 'Keeping Time (Month)'})
# lazy_holding

lazy_holding['Close Date'] = lazy_holding['Keeping Time (Month)'].apply(lambda x: dt.timedelta(31*x))
lazy_holding['Close Date'] += pd.to_datetime(lazy_holding['Open Date'])
lazy_holding['Close Date'] = lazy_holding['Close Date'].dt.strftime('%Y-%m-%d')

lazy_holding['Open Date'] = pd.to_datetime(lazy_holding['Open Date'])
lazy_holding['Close Date'] = pd.to_datetime(lazy_holding['Close Date'])

lazy_holding['open'] = lazy_holding['Open Date']-base_day
lazy_holding['close'] = lazy_holding['Close Date']-base_day

lazy_holding['Open Date'] = lazy_holding['Open Date'].dt.strftime('%m-%d-%Y')
lazy_holding['Close Date'] = lazy_holding['Close Date'].dt.strftime('%m-%d-%Y')


lazy_open_date = [lazy_holding.loc[i, 'open'].days for i in lazy_holding.index]
lazy_close_date = [lazy_holding.loc[i, 'close'].days for i in lazy_holding.index]

lazy_offers = ['Bonus {}'.format(i) for i in lazy_holding.index]

                               
fig2 = plt.figure(figsize=(18, 5))
ax = fig2.add_subplot(111)


for i in range(len(lazy_open_date)):
    plt.plot([lazy_open_date[i], lazy_close_date[i]], [i+0.5, i+0.5], lw=55, c='blue')
    
plt.xlim(0, 365*2)
plt.ylim(0, len(lazy_open_date))
ax.set_aspect(40)
# plt.grid(b=True, which='both', axis='both')
plt.tick_params(axis='x', which='both', bottom=False, top=False)
plt.tick_params(axis='y', which='both', left=False, right=False)
xlist = [0, 90, 181, 273, 365, 455, 546, 638, 730]
xlabels=['2019-12', '2020-03', '2020-06', '2020-9', '2020-12', '2021-03', '2021-06', '2021-09', '2021-12']
plt.xticks(xlist, xlabels)
# plt.xticks(np.arange(0.5, 12.5), calendar.month_name[1:13])
plt.yticks(np.arange(0.5, len(lazy_open_date)+0.5), lazy_offers)

ax.xaxis.grid(True, which='major', color='w', lw=1, linestyle='solid')
ax.yaxis.grid(True, which='minor', color='w', lw=1, linestyle='solid')
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(1))

# hide axis spines
for spine in ax.spines.values():
    spine.set_visible(False)
    
ax.set_facecolor('lavender')
fig2.patch.set_alpha(0.)
plt.tight_layout()

st.sidebar.subheader('Validation')
st.sidebar.markdown('Optimal Strategy Return: '+str(total_return))
st.sidebar.markdown('vs')
st.sidebar.markdown('Lazy Strategy Return: '+str(lazy_total_return))

st.sidebar.subheader('')
st.sidebar.subheader('')

st.subheader('Lazy Strategy:')
st.table(lazy_holding[holding_cols])
st.subheader('Lazy Strategy Return:')
st.write(lazy_total_return)
st.pyplot(fig2, dpi=200)







