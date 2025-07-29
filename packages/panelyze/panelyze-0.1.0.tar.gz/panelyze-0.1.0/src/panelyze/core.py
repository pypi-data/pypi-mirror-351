import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from itables import show, init_notebook_mode

# Enable interactive tables and set custom CSS for black text in lengthMenu
init_notebook_mode(all_interactive=True)
display(HTML("""
<style>
.dataTables_length select {
    color: black !important;
}
</style>
"""))

def panelyze(df: pd.DataFrame, max_filter_values=100):
    """
    Interactive Excel-like DataFrame viewer with column selection, filtering,
    and global NaN visibility support.
    """
    df = df.copy()
    output = widgets.Output()

    all_columns = df.columns.tolist()

    # Checkbox for displaying only NaN-containing rows
    global_nan_checkbox = widgets.Checkbox(
        value=False,
        description="",
        layout=widgets.Layout(margin="0 0 0 10px")
    )

    # "Select all" toggle
    select_all_checkbox = widgets.Checkbox(
        value=True,
        description="All columns"
    )

    column_selector = widgets.SelectMultiple(
        options=all_columns,
        value=tuple(all_columns),
        layout=widgets.Layout(width='250px', height='160px')
    )

    def toggle_all_columns(change):
        if select_all_checkbox.value:
            column_selector.value = tuple(all_columns)
        else:
            column_selector.value = ()

    select_all_checkbox.observe(toggle_all_columns, names='value')

    # Filters area
    filters_box = widgets.VBox()
    filter_widgets = {}

    def create_filters(change=None):
        filters_box.children = []
        filter_widgets.clear()

        selected_cols = list(column_selector.value)
        new_filters = []

        for col in selected_cols:
            unique_vals = df[col].dropna().unique()

            if len(unique_vals) > max_filter_values:
                filter_input = widgets.Text(
                    placeholder='Contains...',
                    layout=widgets.Layout(width='200px')
                )
            else:
                filter_input = widgets.Dropdown(
                    options=['All'] + sorted(unique_vals.tolist()),
                    value='All',
                    layout=widgets.Layout(width='200px')
                )

            filter_widgets[col] = filter_input

            new_filters.append(
                widgets.HBox([
                    widgets.Label(f"{col}:", layout=widgets.Layout(width='100px')),
                    filter_input
                ])
            )

        filters_box.children = new_filters

    def apply_filters(b=None):
        selected_cols = list(column_selector.value)

        if global_nan_checkbox.value:
            filtered_df = df[selected_cols]
            nan_mask = filtered_df.isna().any(axis=1)
            filtered_df = filtered_df[nan_mask]
            if filtered_df.empty:
                filtered_df = pd.DataFrame(columns=selected_cols)
        else:
            filtered_df = df[selected_cols].copy()
            for col in selected_cols:
                widget = filter_widgets.get(col)
                if isinstance(widget, widgets.Dropdown) and widget.value != 'All':
                    mask = filtered_df[col] == widget.value
                    filtered_df = filtered_df[mask]
                elif isinstance(widget, widgets.Text) and widget.value:
                    mask = filtered_df[col].astype(str).str.contains(widget.value, na=False, case=False)
                    filtered_df = filtered_df[mask]

        with output:
            clear_output()
            show(filtered_df, scrollY="500px", lengthMenu=[10, 25, 50, 100, 1000, 1000000])

    def reset_filters(b=None):
        for widget in filter_widgets.values():
            if isinstance(widget, widgets.Dropdown):
                widget.value = 'All'
            elif isinstance(widget, widgets.Text):
                widget.value = ''
        global_nan_checkbox.value = False
        apply_filters()

    column_selector.observe(create_filters, names='value')
    apply_button = widgets.Button(description="Apply Filters", button_style='success')
    reset_button = widgets.Button(description="Reset Filters", button_style='warning')
    apply_button.on_click(apply_filters)
    reset_button.on_click(reset_filters)

    create_filters()
    apply_filters()

    display(widgets.VBox([
        widgets.HBox([
            widgets.VBox([
                widgets.HTML("<b>Specify Columns to Filter Data:</b>"),
                select_all_checkbox,
                column_selector
            ]),
            widgets.VBox([
                widgets.HTML("<b>Filter by Column:</b>"),
                filters_box
            ], layout=widgets.Layout(margin='0 0 0 20px'))
        ]),

        widgets.HBox([
            widgets.HTML("<b>Display Missing Values Only (NaN):</b>"),
            global_nan_checkbox
        ], layout=widgets.Layout(margin='10px 0')),

        widgets.HBox([apply_button, reset_button]),
        output
    ]))