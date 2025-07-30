from enum import Enum

# Enum classes for display magic input options
class ViewType(Enum):
    TABLE = "table"
    SCHEMA = "schema"
    COLUMN = "column"
    PLOT = "plot"
    ALL = "all"

class PlotLibraries(Enum):
    DEFAULT = "default"
    PYGWALKER = "pygwalker"
    YDATA = "ydata-profiling"
    DATAPREP = "dataprep"

# Section and Header Text
TABLE_SECTION_NAME = "Table"
SUMMARY_SECTION_NAME = "Summary"
COLUMN_SECTION_NAME = "Column"
PLOTTING_SECTION_NAME = "Plotting"
COLUMN_HOME_SECTION_NAME = "Home"

SUMMARY_HEADER = "DataFrame Data Visualization"
COLUMN_HEADER = "Column Data Visualization"
PLOT_HEADER = "Plot Data Visualization"
TABLE_HEADER = "Table Data Visualization"

COLUMN_NAME_HEADER = "Column Name"
DATA_TYPE_HEADER = "Data Type"
COUNT_HEADER = "Count"
DISTINCT_HEADER = "Distinct"
NULL_HEADER = "Null"
DATA_QUALITY_HEADER = "Data Quality"
VALUE_DISTRIBUTION_HEADER = "Value Distribution"
FREQUENT_RESULTS_HEADER = "Frequent Results"
BOX_PLOT_HEADER = "Box Plot"

COLUMN_SELECTOR_NAME = "Column Selector"
CHART_TYPE_SELECTOR_NAME = "Chart Type"
X_AXIS_SELECTOR_NAME = "X-Axis"
Y_AXIS_SELECTOR_NAME = "Y-Axis"
X_AXIS_TYPE_SELECTOR_NAME = "X-Axis Type"
Y_AXIS_TYPE_SELECTOR_NAME = "Y-Axis Type"
AGGREGATION_FUNCTION_SELECTOR_NAME = "Aggregation Function"
SAMPLING_METHOD_SELECTOR_NAME = "Sampling Method"
SAMPLE_SIZE_SELECTOR_NAME = "Sample Size"
PLOTTING_LIBRARY_SELECTOR_NAME = "Plotting Library"
ROWS_PER_PAGE_SELECTOR_NAME = "Rows per Page"

# Selector Options
CHART_TYPE_OPTIONS = ["Line", "Pie", "Scatter", "Bar"]
AXIS_TYPE_OPTIONS = ["Category", "Value", "Log"]
AGGREGATION_FUNCTION_OPTIONS = ["Mean", "Count", "Sum", "Min", "Max", "None"]
SAMPLING_METHOD_OPTIONS = ["Head", "Tail", "Random", "All"]
ROWS_PER_PAGE_OPTIONS = [5, 10, 25]

#STYLING CONSTANTS
ROW_STYLE = {
    "text-align": "center",
    "vertical-align": "middle",
    "width": "100%"
}

TEXT_STYLE = {
    "text-align": "center",
    "vertical-align": "middle",
}

GRAPH_STYLE = {
    "width": "96%",
    "height": "96%",
    "vertical-align": "middle",
}

PAGE_STYLE = {
    "height":"100%",
    "max_height":"100%",
    "width":"98%",
    "max_width":"98%",
    "margin-bottom":"1rem",
    "background-color":"transparent",
    "scrollbar-color":"grey transparent",
    "overflow-x":"scroll"
}

TEXT_STYLESHEET = """
    :host {
        --design-primary-text-color: var(--jp-content-font-color1);
        --design-secondary-text-color: var(--jp-content-font-color1);
        --design-background-text-color: var(--jp-content-font-color1);
        --design-surface-text-color: var(--jp-content-font-color1);
        --background-text-color: var(--jp-content-font-color1);
        font-family: var(--jp-ui-font-family);
        font-size: var(--jp-code-font-size);
    }
"""

BUTTON_STYLESHEET = """
    :host(.outline) .bk-btn-light {
        border-color: var(--jp-inverse-layout-color0);
    }

    :host(.outline) .bk-btn-light:hover {
        background-color: var(--jp-inverse-layout-color0);
        color: var(--jp-ui-inverse-font-color0);
    }
"""

SELECT_STYLESHEET = """
    select:not([multiple]).bk-input, select:not([size]).bk-input {
        background-image: url('data:image/svg+xml;utf8,<svg version="1.1" viewBox="0 0 25 20" xmlns="http://www.w3.org/2000/svg"><path d="M 0,0 25,0 12.5,20 Z" fill="white" stroke="black" stroke-width="3"/></svg>')
    }

    option {
        background-color: var(--jp-cell-editor-active-background);
    }
"""

ACCORDION_STYLESHEET = """
    :host(.accordion) button {
        padding: 0px 2px;
    }

    :host(.accordion) {
        padding: 2px 0px;
    }
"""

ACCORDION_TEXT_STYLESHEET = """
    <style>
    :host(.card-title) h3 {
        --design-primary-text-color: var(--jp-ui-font-color1);
        --design-secondary-text-color: var(--jp-ui-font-color1);
        --design-background-text-color: var(--jp-ui-font-color1);
        --design-surface-text-color: var(--jp-ui-font-color1);
        font-family: var(--jp-ui-font-family);
        font-size: var(--jp-code-font-size);
        margin-block-end: 0em;
        margin-block-start: 0em;
        background-color: transparent
    }
    </style>
"""

TABULATOR_STYLESHEET = """
    :host .tabulator .tabulator-header .tabulator-col.tabulator-sortable.tabulator-col-sorter-element:hover {
        background-color: var(--jp-rendermime-table-row-hover-background)
    }

    :host .pnx-tabulator.tabulator .tabulator-header .tabulator-col.tabulator-sortable:hover {
        background-color: var(--jp-rendermime-table-row-hover-background)
    }

    :host .tabulator {
        --design-primary-text-color: var(--jp-content-font-color1);
        --design-secondary-text-color: var(--jp-content-font-color1);
        --design-background-text-color: var(--jp-content-font-color1);
        --design-surface-text-color: var(--jp-content-font-color1);
        font-family: var(--jp-ui-font-family);
        font-size: var(--jp-code-font-size);
    }
"""

GENERAL_HEIGHT = 1050
COLUMN_HOME_HEIGHT = 450
SUMMARY_TEXT_HEIGHT = 35
PLOT_HEIGHT = 225
PLOT_WIDTH = 300
HALF_SELECT_WIDTH = 150

PLOT_COLOR = "#0072b5"
TEXT_COLOR = "#ffffff"
AXIS_COLOR = "#999"

MAIN_ACCORDION_HEADER_BACKGROUND = "var(--jp-layout-color1)"
COLUMN_ACCORDION_HEADER_BACKGROUND = "var(--jp-layout-color2)"

ECHART_TEMPLATE = "default"

