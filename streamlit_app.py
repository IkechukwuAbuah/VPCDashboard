import streamlit as st
import pandas as pd
import openpyxl
import plotly.express as px
import plotly.graph_objects as go

# Streamlit app to deploy route cost management system
def main():
    st.title("VPC Route Cost Dashboard")
    st.write("This dashboard allows users to search routes by origin, destination, fleet, and month.")

    # File upload
    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

    if uploaded_file:
        # Load the uploaded Excel file
        try:
            data = pd.read_excel(uploaded_file, sheet_name='Sheet1')
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            return

        # Remove unnecessary columns
        data = data.drop(columns=['COMMISSION', 'COST/LITRE'])

        # Filter options
        origin_options = ['All'] + list(data['ORIGIN'].unique())
        destination_options = ['All'] + list(data['DESTINATION'].unique())
        fleet_options = ['All'] + list(data['Fleet'].unique())
        month_options = ['All'] + list(data['Month'].unique())

        # Display all filters on one line
        st.sidebar.header("Filters")
        selected_origin = st.sidebar.selectbox("Select Origin", options=origin_options)
        selected_destination = st.sidebar.selectbox("Select Destination", options=destination_options)
        selected_fleet = st.sidebar.selectbox("Select Fleet", options=fleet_options)
        selected_month = st.sidebar.selectbox("Select Month", options=month_options)

        # Filter data based on user selections
        filtered_data = data.copy()
        if selected_origin != 'All':
            filtered_data = filtered_data[filtered_data['ORIGIN'] == selected_origin]
        if selected_destination != 'All':
            filtered_data = filtered_data[filtered_data['DESTINATION'] == selected_destination]
        if selected_fleet != 'All':
            filtered_data = filtered_data[filtered_data['Fleet'] == selected_fleet]
        if selected_month != 'All':
            filtered_data = filtered_data[filtered_data['Month'] == selected_month]

        # Sidebar summary section for filtered data
        if not filtered_data.empty:
            total_trips = filtered_data['ORIGIN'].count()
            total_revenue = filtered_data['TRIP RATE'].sum()
            average_profit = filtered_data['PROFIT'].mean()
            average_cost = filtered_data[['TRIP RATE', 'DISPATCH']].sum(axis=1).mean() - average_profit

            st.sidebar.markdown("### Summary of Filtered Data")
            st.sidebar.write(f"**Total Trips:** {total_trips}")
            st.sidebar.write(f"**Total Revenue (₦):** {total_revenue:,.0f}")
            st.sidebar.write(f"**Average Profit (₦):** {average_profit:,.0f}")
            st.sidebar.write(f"**Average Cost (₦):** {average_cost:,.0f}")

        # Display filtered results in a collapsible section (closed by default)
        with st.expander("Filtered Route Data", expanded=False):
            st.dataframe(filtered_data)

        # Summary section for filtered data
        if not filtered_data.empty:
            filtered_data['TOTAL_COST'] = (filtered_data['TRIP RATE'] + filtered_data['DISPATCH']) - filtered_data['PROFIT']

            # Group by month and fleet and calculate summary metrics
            summary_by_month_and_fleet = filtered_data.groupby(['Month', 'Fleet']).agg(
                number_of_trips=('ORIGIN', 'count'),
                total_revenue=('TRIP RATE', 'sum'),
                average_profit=('PROFIT', 'mean'),
                average_cost=('TOTAL_COST', 'mean')
            ).reset_index()

            # Sort months in chronological order
            month_order = ['JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER']
            summary_by_month_and_fleet['Month'] = pd.Categorical(summary_by_month_and_fleet['Month'], categories=month_order, ordered=True)
            summary_by_month_and_fleet = summary_by_month_and_fleet.sort_values(['Month', 'Fleet'])

            # Display combined summary in a collapsible section (open by default)
            with st.expander("Summary of Filtered Routes by Month and Fleet", expanded=True):
                st.dataframe(summary_by_month_and_fleet)

            # Visualization for summary statistics using Plotly in collapsible sections
            with st.expander("Summary Statistics Visualization - Number of Trips by Month", expanded=True):
                trips_fig = px.bar(summary_by_month_and_fleet, x='Month', y='number_of_trips', color='Fleet', title='Number of Trips by Month and Fleet',
                                   labels={'number_of_trips': 'Number of Trips', 'Month': 'Month'}, barmode='group',
                                   color_discrete_sequence=px.colors.qualitative.Set1)
                trips_fig.update_layout(barmode='stack', bargap=0.1)
                st.plotly_chart(trips_fig)

            with st.expander("Summary Statistics Visualization - Average Profit by Month", expanded=False):
                profit_fig = px.bar(summary_by_month_and_fleet, x='Month', y='average_profit', color='Fleet', title='Average Profit by Month and Fleet',
                                    labels={'average_profit': 'Average Profit (₦)', 'Month': 'Month'}, barmode='group',
                                    color_discrete_sequence=px.colors.qualitative.Set2)
                profit_fig.update_layout(barmode='stack', bargap=0.1)
                st.plotly_chart(profit_fig)

            with st.expander("Summary Statistics Visualization - Average Cost by Month", expanded=False):
                cost_fig = px.bar(summary_by_month_and_fleet, x='Month', y='average_cost', color='Fleet', title='Average Cost by Month and Fleet',
                                  labels={'average_cost': 'Average Cost (₦)', 'Month': 'Month'}, barmode='group',
                                  color_discrete_sequence=px.colors.qualitative.Pastel)
                cost_fig.update_layout(barmode='stack', bargap=0.1)
                st.plotly_chart(cost_fig)

            with st.expander("Summary Statistics Visualization - Total Revenue by Month", expanded=False):
                revenue_fig = px.bar(summary_by_month_and_fleet, x='Month', y='total_revenue', color='Fleet', title='Total Revenue by Month and Fleet',
                                     labels={'total_revenue': 'Total Revenue (₦)', 'Month': 'Month'}, barmode='group',
                                     color_discrete_sequence=px.colors.qualitative.Set3)
                revenue_fig.update_layout(barmode='stack', bargap=0.1)
                st.plotly_chart(revenue_fig)

if __name__ == "__main__":
    main()