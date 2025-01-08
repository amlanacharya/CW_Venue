import streamlit as st
import pandas as pd
from BSA import process_bank_statement
import tempfile
import os

st.title("Bank Statement Analyzer")

st.write("""
Upload your bank statement CSV file to get a detailed analysis of your income and expenses.
""")

uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_filepath = tmp_file.name
    
    try:
        income_df, expenses_df, full_df = process_bank_statement(tmp_filepath)
        
        if income_df is not None:
            st.success("Analysis completed successfully!")
            
            tab1, tab2, tab3 = st.tabs(["Summary", "Income Details", "Expense Details"])
            
            with tab1:
                st.header("Financial Summary")
                total_income = income_df['Amount'].sum()
                total_expenses = expenses_df['Amount'].sum()
                net_amount = total_income - total_expenses
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Income", f"₹{total_income:,.2f}")
                with col2:
                    st.metric("Total Expenses", f"₹{total_expenses:,.2f}")
                with col3:
                    st.metric("Net Profit/Loss", f"₹{net_amount:,.2f}")
                
                st.header("Monthly Breakdown")
                monthly_data = pd.DataFrame(full_df.groupby(full_df['Date'].dt.strftime('%B %Y')).agg({
                    'Amount': lambda x: (x * (full_df.loc[x.index, 'Dr / Cr'] == 'CR')).sum() - 
                                      (x * (full_df.loc[x.index, 'Dr / Cr'] == 'DR')).sum()
                }))
                st.bar_chart(monthly_data)
            
            with tab2:
                st.header("Income Transactions")
                st.dataframe(income_df)
                
                csv_income = income_df.to_csv(index=False)
                st.download_button(
                    label="Download Unclean Income Data",
                    data=csv_income,
                    file_name="uc_income.csv",
                    mime="text/csv"
                )
            
            with tab3:
                st.header("Expense Transactions")
                st.dataframe(expenses_df)
                
                csv_expenses = expenses_df.to_csv(index=False)
                st.download_button(
                    label="Download Unclean Expense Data",
                    data=csv_expenses,
                    file_name="uc_expenses.csv",
                    mime="text/csv"
                )
        
        else:
            st.error("Error processing the file. Please check the file format.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
    finally:
        os.unlink(tmp_filepath)

st.sidebar.markdown("""
### Instructions
1. Upload your bank statement CSV file
2. View the analysis in different tabs
3. Download income and expense data separately
""")