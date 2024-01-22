import streamlit as st
from streamlit.errors import StreamlitAPIException
import pandas as pd


class DynamicFilters:
    """
    A class to create dynamic multi-select filters in Streamlit.

    ...

    Attributes
    ----------
    df : DataFrame
        The dataframe on which filters are applied.
    filters : dict
        Dictionary with filter names as keys and their selected values as values.

    Methods
    -------
    check_state():
        Initializes the session state with filters if not already set.
    filter_df(except_filter=None):
        Returns the dataframe filtered based on session state excluding the specified filter.
    display():
        Renders the dynamic filters and the filtered dataframe in Streamlit.
    """

    def __init__(self, df, filters, filters_name='filters'):
        """
        Constructs all the necessary attributes for the DynamicFilters object.

        Parameters
        ----------
            df : DataFrame
                The dataframe on which filters are applied.
            filters : list of filters
                List of columns names in df for which filters are to be created.
            filters_name: str, optional
                Name of the filters object in session state.
        """
        self.df = df
        self.filters_name = filters_name
        self.filters = {filter_name: [] for filter_name in filters}
        self.check_state()

    def check_state(self):
        """Initializes the session state with filters if not already set."""
        # if 'filters' not in st.session_state:
        #     st.session_state.filters = self.filters
        if self.filters_name not in st.session_state:
            st.session_state[self.filters_name] = self.filters

    def filter_df(self, except_filter=None):
        """
        Filters the dataframe based on session state values except for the specified filter.

        Parameters
        ----------
            except_filter : str, optional
                The filter name that should be excluded from the current filtering operation.

        Returns
        -------
            DataFrame
                Filtered dataframe.
        """
        filtered_df = self.df.copy()
        for key, values in st.session_state[self.filters_name].items():
            if key != except_filter and values:
                filtered_df = filtered_df[filtered_df[key].isin(values)]
        return filtered_df

    
    def display_filters(self, location=None, num_columns=0, gap="small"):
        # ... (rest of the method remains the same)

        filters_changed = False

        # initiate counter and max_value for columns
        if location == 'columns' and num_columns > 0:
            counter = 1
            max_value = num_columns
            col_list = st.columns(num_columns, gap=gap)

        for filter_name in st.session_state[self.filters_name].keys():
            filtered_df = self.filter_df(filter_name)
            options = filtered_df[filter_name].unique().tolist()

            # Remove selected values that are not in options anymore
            valid_selections = [v for v in st.session_state[self.filters_name][filter_name] if v in options]
            if valid_selections != st.session_state[self.filters_name][filter_name]:
                st.session_state[self.filters_name][filter_name] = valid_selections
                filters_changed = True

            if location == 'sidebar':
                selected = st.selectbox(f"Select {filter_name}", options,
                                        index=options.index(st.session_state[self.filters_name][filter_name][0])
                                        if st.session_state[self.filters_name][filter_name] else 0)
            elif location == 'columns' and num_columns > 0:
                with col_list[counter - 1]:
                    selected = st.selectbox(f"Select {filter_name}", options,
                                            index=options.index(st.session_state[self.filters_name][filter_name][0])
                                            if st.session_state[self.filters_name][filter_name] else 0)

                # increase counter and reset to 1 if max_value is reached
                counter += 1
                counter = counter % (max_value + 1)
                if counter == 0:
                    counter = 1
            else:
                selected = st.selectbox(f"Select {filter_name}", options,
                                        index=options.index(st.session_state[self.filters_name][filter_name][0])
                                        if st.session_state[self.filters_name][filter_name] else 0)

            if selected != st.session_state[self.filters_name][filter_name]:
                st.session_state[self.filters_name][filter_name] = [selected]
                filters_changed = True

        if filters_changed:
            st.experimental_rerun()  # Use st.experimental_rerun() instead of st.rerun()
    def display_df(self, **kwargs):
        """Renders the filtered dataframe in the main area."""
        # Display filtered DataFrame
        st.dataframe(self.filter_df(), **kwargs)