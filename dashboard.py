import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='white')

orders_number_df = pd.read_csv("numbers_of_orders.csv", delimiter=",")
sum_order_items_df = pd.read_csv("sum_order_items.csv", delimiter=",")
most_reviewed_df = pd.read_csv("most_reviewed_df.csv", delimiter=",")
customer_df = pd.read_csv("customers_dataset.csv", delimiter=",") 
sellers_df = pd.read_csv("sellers_dataset.csv", delimiter=",")
rfm_df = pd.read_csv("rfm_df.csv", delimiter=",")


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_delivered_customer_date').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english").quantity_x.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_delivered_customer_date": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "total_price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_delivered_customer_date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df



datetime_columns = ["order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_approved_at", "order_purchase_timestamp"]
orders_number_df.sort_values(by="order_delivered_customer_date", inplace=True)
orders_number_df.reset_index(inplace=True)
 
for column in datetime_columns:
    orders_number_df[column] = pd.to_datetime(orders_number_df[column])

monthly_orders_df = orders_number_df.resample(rule='M', on='order_delivered_customer_date').agg({
    "order_id": "nunique",
    "price": "sum"
})

monthly_orders_df.index = monthly_orders_df.index.strftime('%Y-%m')

# Reset indeks
monthly_orders_df = monthly_orders_df.reset_index()

# Ganti nama kolom
monthly_orders_df.rename(columns={
    "order_id": "order_count",
    "price": "revenue"
}, inplace=True)


min_date = orders_number_df["order_delivered_customer_date"].min()
max_date = orders_number_df["order_delivered_customer_date"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    # st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
st.header('E-Commerce Collection Dashboard :sparkles:')

orders_chart_df = orders_number_df[(orders_number_df["order_delivered_customer_date"] >= str(start_date)) & (orders_number_df["order_delivered_customer_date"] <= str(end_date))]


daily_orders_df = create_daily_orders_df(orders_chart_df)



st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_delivered_customer_date"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)


tab1, tab2 = st.tabs(["Profit", "Review Score"])
 


fig_profit, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="price", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product by Profit", loc="center", fontsize=20)
ax[0].tick_params(axis ='y', labelsize=20)
ax[0].tick_params(axis ='x', labelsize=25) 

sns.barplot(x="price", y="product_category_name_english", data=sum_order_items_df.sort_values(by="price", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product (By Profit)", loc="center", fontsize=20)
ax[1].tick_params(axis='y', labelsize=20)
ax[1].tick_params(axis ='x', labelsize=25)
 
plt.show()


with tab1:
    st.subheader("Best & Worst Performing Product by Profit")
    st.pyplot(fig_profit)
 



most_reviewed_df = most_reviewed_df[most_reviewed_df['review_score'] == 5].groupby(by=["product_category_name_english"]).agg({
    "review_score" : "sum"
}).sort_values(by="review_score", ascending=False)

fig_rev, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["green", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="review_score", y="product_category_name_english", data=most_reviewed_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Reviewed Product", loc="center", fontsize=20)
ax[0].tick_params(axis ='y', labelsize=20)
ax[0].tick_params(axis ='x', labelsize=25) 

sns.barplot(x="review_score", y="product_category_name_english", data=most_reviewed_df.sort_values(by="review_score", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Reviewed Product", loc="center", fontsize=20)
ax[1].tick_params(axis ='y', labelsize=20)
ax[1].tick_params(axis ='x', labelsize=25) 

plt.show()





with tab2:
    st.subheader("Best & Worst Performing Product by Review per 5 Stars")
    st.pyplot(fig_rev)
 

tab3, tab4 = st.tabs(["Customers", "Sellers"])
 
customer_state_df = customer_df.groupby(by="customer_state").customer_id.nunique().sort_values(ascending=False)
customer_city_df = customer_df.groupby(by="customer_city").customer_id.nunique().sort_values(ascending=False)

fig_customer, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))  

customer_state_df[:10].plot(kind='bar', ax=axes[0], color='skyblue')
axes[0].set_title("Customer Count by State (Top 10)")
axes[0].set_ylabel('Number of Customers')
axes[0].set_xlabel('State')
axes[0].tick_params(axis ='y', labelsize=12)
axes[0].invert_xaxis()
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=360, ha="right")  # Memutar label sumbu x

customer_city_df[:10].plot(kind='bar', ax=axes[1], color='orange')  # Hanya mengambil 10 kota teratas untuk kejelasan
axes[1].set_title('Customer Count by City (Top 10)')
axes[1].set_ylabel('Number of Customers')
axes[1].set_xlabel('City')
axes[1].yaxis.set_label_position("right")
axes[1].yaxis.tick_right()
axes[1].tick_params(axis='y', labelsize=12)
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45, ha="right", fontsize=10)  # Memutar label sumbu x

plt.tight_layout()  

plt.show()

with tab3:
    st.subheader("Customers Demography")
    st.pyplot(fig_customer)


sellers_state_df = sellers_df.groupby(by="seller_state").seller_id.nunique().sort_values(ascending=False)
sellers_city_df = sellers_df.groupby(by="seller_city").seller_id.nunique().sort_values(ascending=False)


fig_sellers, axes = plt.subplots(nrows=1, ncols=2, figsize=(15, 5))  # Dua subplot sejajar

# Plot untuk customer_state_df
sellers_state_df[:10].plot(kind='bar', ax=axes[0], color='skyblue')
axes[0].set_title("Sellers Count by State (Top 10)")
axes[0].set_ylabel('Number of Sellers')
axes[0].set_xlabel('State')
axes[0].tick_params(axis ='y', labelsize=12)
axes[0].invert_xaxis()
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=360, ha="right")  # Memutar label sumbu x

# Plot untuk customer_city_df
sellers_city_df[:10].plot(kind='bar', ax=axes[1], color='orange')  # Hanya mengambil 10 kota teratas untuk kejelasan
axes[1].set_title('Sellers Count by City (Top 10)')
axes[1].set_ylabel('Number of Sellers')
axes[1].set_xlabel('City')
axes[1].yaxis.set_label_position("right")
axes[1].yaxis.tick_right()
axes[1].tick_params(axis='y', labelsize=12)
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45, ha="right", fontsize=10)  # Memutar label sumbu x

plt.tight_layout()  

plt.show()

with tab4:
    st.subheader("Sellers Demography")
    st.pyplot(fig_sellers)


rfm_df['customer_id'] = rfm_df['customer_id'].str[:8]

st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 

fig_rfm, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15, rotation=55)
ax[1].tick_params(axis='x', labelsize=15, rotation=55)
ax[2].tick_params(axis='x', labelsize=15, rotation=55)

# Menambahkan judul keseluruhan
plt.suptitle("Best Customer Based on RFM Parameters (customer_id)", fontsize=20)

# Menampilkan plot
plt.show()

st.pyplot(fig_rfm)