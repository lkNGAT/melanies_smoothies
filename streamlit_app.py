# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd


# Write directly to the app
st.title("Customize your smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)
name_on_order = st.text_input('Name on smoothie:')
st.write('The name on you smoothie will be: ',name_on_order)


cnx = st.connection('snowflake')
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()


ingredients_list = st.multiselect('Choose up to 5 ingredients:', my_dataframe, max_selections=5)
if ingredients_list:
    ingredients_string = ''
    for x in ingredients_list:
        seach_on = pd_df.loc[pd_df['FRUIT_NAME' == x],'SEARCH_ON'].iloc[0]
        st.write('The search value for ', x,' is ', search_on,'.')
        st.subheader(x + ' Nutrition Information:')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + x)
        fv_df = st.dataframe(data =fruityvice_response.json(), use_container_width=True )
        ingredients_string += x + ' '
    #st.write(ingredients_string)
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    #st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, '+ name_on_order +"!", icon="✅")
