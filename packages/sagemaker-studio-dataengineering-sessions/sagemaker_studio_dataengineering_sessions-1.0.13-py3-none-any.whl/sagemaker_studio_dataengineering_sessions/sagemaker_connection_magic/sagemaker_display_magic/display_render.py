import os
import traceback
import html
import json
import logging
import warnings
from io import BytesIO
from jupyter_core.paths import jupyter_config_dir
from sagemaker_studio_dataengineering_sessions.sagemaker_connection_magic.sagemaker_display_magic.style_constants import (
    # Enum classes and Selector Options
    PlotLibraries, ViewType, CHART_TYPE_OPTIONS, AXIS_TYPE_OPTIONS, AGGREGATION_FUNCTION_OPTIONS, SAMPLING_METHOD_OPTIONS, ROWS_PER_PAGE_OPTIONS,
    # Styling constants
    ACCORDION_STYLESHEET, ACCORDION_TEXT_STYLESHEET, AXIS_COLOR, BUTTON_STYLESHEET, COLUMN_ACCORDION_HEADER_BACKGROUND, COLUMN_HOME_HEIGHT,
    ECHART_TEMPLATE, GENERAL_HEIGHT, GRAPH_STYLE, HALF_SELECT_WIDTH, MAIN_ACCORDION_HEADER_BACKGROUND, PAGE_STYLE, PLOT_COLOR, PLOT_HEIGHT,
    PLOT_WIDTH, SELECT_STYLESHEET, SUMMARY_TEXT_HEIGHT, TABULATOR_STYLESHEET, TEXT_COLOR, TEXT_STYLE, TEXT_STYLESHEET,
    # Section and Header Text
    TABLE_SECTION_NAME, SUMMARY_SECTION_NAME, COLUMN_SECTION_NAME, PLOTTING_SECTION_NAME, COLUMN_HOME_SECTION_NAME,
    SUMMARY_HEADER, COLUMN_HEADER, PLOT_HEADER, TABLE_HEADER, COLUMN_NAME_HEADER, DATA_TYPE_HEADER, COUNT_HEADER, DISTINCT_HEADER,
    NULL_HEADER, DATA_QUALITY_HEADER, VALUE_DISTRIBUTION_HEADER, FREQUENT_RESULTS_HEADER, BOX_PLOT_HEADER,
    COLUMN_SELECTOR_NAME, CHART_TYPE_SELECTOR_NAME, X_AXIS_SELECTOR_NAME, Y_AXIS_SELECTOR_NAME, X_AXIS_TYPE_SELECTOR_NAME,
    Y_AXIS_TYPE_SELECTOR_NAME, AGGREGATION_FUNCTION_SELECTOR_NAME, SAMPLING_METHOD_SELECTOR_NAME, SAMPLE_SIZE_SELECTOR_NAME,
    PLOTTING_LIBRARY_SELECTOR_NAME, ROWS_PER_PAGE_SELECTOR_NAME
)
from sagemaker_studio_dataengineering_sessions.sagemaker_connection_magic.sagemaker_display_magic.run_statement import run_statement
from sagemaker_studio_dataengineering_sessions.sagemaker_connection_magic.sagemaker_display_magic.utils import JSONWithCommentsDecoder


try:
    import panel as pn
    from IPython.display import display
    import pandas as pd
except ModuleNotFoundError as e: 
    raise ModuleNotFoundError(f"Missing required libraries on local instance. Error: {e}")

# Known issue with PyArrow. Does not affect runtime.
warnings.filterwarnings('ignore', message='\'PYARROW_IGNORE_TIMEZONE\'')


class DisplayMagicRender:
    def __init__(self, display_magic_compute, session_manager, view=ViewType.ALL.value, plot_lib=PlotLibraries.DEFAULT.value, columns=None):
        pn.extension("echarts", "tabulator", design='material', theme="dark", disconnect_notification='Connection lost, try re-running the cell!', inline=False)

        self.display_magic_compute = display_magic_compute # This is a string representation of the variable name of the DisplayMagicCompute on the remote compute
        self.session_manager = session_manager
        self.columns = columns
        self.logger = logging.getLogger(__name__)

        try:
            self.view = ViewType(view)
            self.plot_lib = PlotLibraries(plot_lib)
            # Bookkeeping to assist with UI interactivity
            self.table_tab_index = None
            self.summary_tab_index = None
            self.column_tab_index = None
            self.plot_tab_index = None
            self.column_tab_list = []

            # Load initial data from the remote compute 
            run_statement_data = run_statement(session_manager = self.session_manager, statement = f"{self.display_magic_compute}.get_metadata()", mode = "eval")
            self.metadata = json.loads(run_statement_data.encode('utf-8').decode('unicode_escape'))
            self.keys = self.metadata["keys"]
            self.sample_df = self.get_sampled_dataframe()
            self.table_rows_per_page = 10

            self.output = self.generate_loading_spinner()
            # GENERATE VIEW
            self.output = self.generate_view()
        except Exception as e:
            self.output = self.generate_exception_card(e)

    # Renders UI to Jupyter Output Cell
    def render(self):
        display(self.output)
        # Ensure that only the first section (Table) is expanded by default
        if self.output.active:
            self.output.active = [self.output.active[0]]

    def get_sampled_dataframe(self):
        sample_data = run_statement(session_manager=self.session_manager, statement=f"""{self.display_magic_compute}.sampled_dataframe.to_parquet()""", mode="eval")
        if isinstance(sample_data, str):
            # Parquet data starts and ends with "PAR1"
            # Slicing is used here to ensure that this is the case and that other characters (like b'' for bytes) are excluded
            parquet_byte_values = sample_data[sample_data.find("PAR1") : sample_data.rfind("PAR1") + 4]
            # This is required for removing the escaped characters and re-encoding the string to the original byte array
            sample_data = parquet_byte_values.encode().decode('unicode_escape').encode('latin-1')
        return pd.read_parquet(BytesIO(sample_data))

    # Generates view based upon passed view type, uses Panel Tab object as primary holder
    def generate_view(self):
        # If column parameter is not none, then displaying column should take precedence
        if self.columns:
            self.column_tab_index = 0
            output = pn.Accordion(
                (ACCORDION_TEXT_STYLESHEET + COLUMN_SECTION_NAME, pn.Accordion(
                    (ACCORDION_TEXT_STYLESHEET + COLUMN_HOME_SECTION_NAME, pn.Column(self.column_home())), active=[0], toggle=True,
                    sizing_mode="stretch_width", header_background=COLUMN_ACCORDION_HEADER_BACKGROUND,
                    active_header_background=COLUMN_ACCORDION_HEADER_BACKGROUND, stylesheets=[TEXT_STYLESHEET])
                ),
                active=[0], toggle=True, sizing_mode="stretch_width",
                header_background=MAIN_ACCORDION_HEADER_BACKGROUND,
                active_header_background=MAIN_ACCORDION_HEADER_BACKGROUND,
                stylesheets=[TEXT_STYLESHEET]
            )
            for col in self.columns:
                col_view = self.column_view(col)
                output[0].append((col, col_view))
        elif self.view is ViewType.PLOT:
            self.table_tab_index = 0
            self.plot_tab_index = 1
            output = pn.Accordion(
                (ACCORDION_TEXT_STYLESHEET + TABLE_SECTION_NAME, pn.Column(self.table_view())),
                (ACCORDION_TEXT_STYLESHEET + PLOTTING_SECTION_NAME, pn.Column(self.plot_view())),
                active=[1], toggle=True, sizing_mode="stretch_width",
                header_background=MAIN_ACCORDION_HEADER_BACKGROUND,
                active_header_background=MAIN_ACCORDION_HEADER_BACKGROUND,
                stylesheets=[TEXT_STYLESHEET]
            )
        elif self.view is ViewType.SCHEMA:
            self.table_tab_index = 0
            self.summary_tab_index = 1
            self.column_tab_index = 2
            output = pn.Accordion(
                (ACCORDION_TEXT_STYLESHEET + TABLE_SECTION_NAME, pn.Column(self.table_view())),
                (ACCORDION_TEXT_STYLESHEET + SUMMARY_SECTION_NAME, pn.Column(self.summary_view())),
                (ACCORDION_TEXT_STYLESHEET + COLUMN_SECTION_NAME, pn.Accordion(
                    (ACCORDION_TEXT_STYLESHEET + COLUMN_HOME_SECTION_NAME, pn.Column(self.column_home())), active=[0], toggle=True,
                    sizing_mode="stretch_width", header_background=COLUMN_ACCORDION_HEADER_BACKGROUND,
                    active_header_background=COLUMN_ACCORDION_HEADER_BACKGROUND, stylesheets=[TEXT_STYLESHEET, ACCORDION_STYLESHEET])
                ),
                active=[0, 1, 2], toggle=True, sizing_mode="stretch_width",
                header_background=MAIN_ACCORDION_HEADER_BACKGROUND,
                active_header_background=MAIN_ACCORDION_HEADER_BACKGROUND,
                stylesheets=[TEXT_STYLESHEET, ACCORDION_STYLESHEET]
            )
        elif self.view is ViewType.TABLE:
            self.table_tab_index = 0
            output = pn.Accordion(
                (ACCORDION_TEXT_STYLESHEET + TABLE_SECTION_NAME, pn.Column(self.table_view())),
                active=[0], toggle=True, sizing_mode="stretch_width",
                header_background=MAIN_ACCORDION_HEADER_BACKGROUND,
                active_header_background=MAIN_ACCORDION_HEADER_BACKGROUND,
                stylesheets=[TEXT_STYLESHEET]
            )
        elif self.view is ViewType.ALL:
            self.table_tab_index = 0
            self.summary_tab_index = 1
            self.column_tab_index = 2
            self.plot_tab_index = 3
            output = pn.Accordion(
                (ACCORDION_TEXT_STYLESHEET + TABLE_SECTION_NAME, pn.Column(self.table_view())),
                (ACCORDION_TEXT_STYLESHEET + SUMMARY_SECTION_NAME, pn.Column(self.summary_view())),
                (ACCORDION_TEXT_STYLESHEET + COLUMN_SECTION_NAME, pn.Accordion(
                    (ACCORDION_TEXT_STYLESHEET + COLUMN_HOME_SECTION_NAME, pn.Column(self.column_home())), active=[0], toggle=True,
                    sizing_mode="stretch_width", header_background=COLUMN_ACCORDION_HEADER_BACKGROUND,
                    active_header_background=COLUMN_ACCORDION_HEADER_BACKGROUND, stylesheets=[TEXT_STYLESHEET])
                ),
                (ACCORDION_TEXT_STYLESHEET + PLOTTING_SECTION_NAME, pn.Column(self.plot_view())),
                active=[0, 1, 2, 3], toggle=True, sizing_mode="stretch_width",
                header_background=MAIN_ACCORDION_HEADER_BACKGROUND,
                active_header_background=MAIN_ACCORDION_HEADER_BACKGROUND,
                stylesheets=[TEXT_STYLESHEET],
                styles=PAGE_STYLE
            )
        else:
            raise ValueError(f"Not a valid view: {self.view.value}")
        return output

    # VIEW LOGIC
    # Creates summary view
    def summary_view(self):
        return pn.Column(
            self.summary_header(),
            self.summary_data(),
            scroll = "x-auto", 
        )

    def summary_header(self):
        heading = pn.pane.Markdown(f"<h3>{SUMMARY_HEADER}</h3>", stylesheets=[TEXT_STYLESHEET], align=("center", "center"), sizing_mode="fixed")
        interactive_selects = self.generate_interactive_selects(context=ViewType.SCHEMA)
        return pn.Row(heading, interactive_selects, sizing_mode="stretch_width")

    def summary_data(self):
        # Calculate Data
        try:
            run_statement_data = run_statement(session_manager = self.session_manager, statement = f"{self.display_magic_compute}.generate_summary_schema()", mode = "eval")
            data = json.loads(run_statement_data.encode('utf-8').decode('unicode_escape'))

            cols = [
                pn.Column(
                    pn.pane.Markdown(f"**{COLUMN_NAME_HEADER}**", styles = TEXT_STYLE, height = SUMMARY_TEXT_HEIGHT, width = PLOT_WIDTH, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET]),
                    pn.pane.Markdown(f"**{DATA_TYPE_HEADER}**", styles = TEXT_STYLE, height = SUMMARY_TEXT_HEIGHT, width = PLOT_WIDTH, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET]),
                    pn.pane.Markdown(f"**{COUNT_HEADER}**", styles = TEXT_STYLE, height = SUMMARY_TEXT_HEIGHT, width = PLOT_WIDTH, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET]),
                    pn.pane.Markdown(f"**{DISTINCT_HEADER}**", styles = TEXT_STYLE, height = SUMMARY_TEXT_HEIGHT, width = PLOT_WIDTH, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET]),
                    pn.pane.Markdown(f"**{NULL_HEADER}**", styles = TEXT_STYLE, height = SUMMARY_TEXT_HEIGHT, width = PLOT_WIDTH, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET]),
                    pn.pane.Markdown(f"**{DATA_QUALITY_HEADER}**", styles = TEXT_STYLE, height = SUMMARY_TEXT_HEIGHT, width = PLOT_WIDTH, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET]),
                    pn.Column(
                        pn.Row(
                            pn.pane.Markdown(f"**{VALUE_DISTRIBUTION_HEADER}**", styles = TEXT_STYLE, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET]),
                            height = PLOT_HEIGHT, align = ("center", "center")
                        ),
                        width = PLOT_WIDTH
                    ),
                    pn.Column(
                        pn.Row(
                            pn.pane.Markdown(f"**{FREQUENT_RESULTS_HEADER}**", styles = TEXT_STYLE, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET]),
                            height = PLOT_HEIGHT, align = ("center", "center")
                        ),
                        width = PLOT_WIDTH
                    ),
                    pn.Column(
                        pn.Row(
                            pn.pane.Markdown(f"**{BOX_PLOT_HEADER}**", styles = TEXT_STYLE, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET]),
                            height = PLOT_HEIGHT, align = ("center", "center")
                        ),
                        width = PLOT_WIDTH
                    ),
                    width = PLOT_WIDTH
                )
            ]

            for col in self.keys:
                column_name = pn.widgets.Button(name = f"{col}", button_style = "outline", button_type = "light", description = f"Open column view for {col}", height = SUMMARY_TEXT_HEIGHT, width = PLOT_WIDTH, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET, BUTTON_STYLESHEET])
                column_name.on_click(self.update_column_view_from_summary)

                data_type = pn.pane.Markdown(f"""{data[col]["dtype"]}""", styles = TEXT_STYLE, height = SUMMARY_TEXT_HEIGHT, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET])
                count = pn.pane.Markdown(f"""{int(data[col]["count"])}""", styles = TEXT_STYLE, height = SUMMARY_TEXT_HEIGHT, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET])
                distinct = pn.pane.Markdown(f"""{data[col]["distinct"]}""", styles = TEXT_STYLE, height = SUMMARY_TEXT_HEIGHT, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET])
                null = pn.pane.Markdown(f"""{data[col]["null"]}""", styles = TEXT_STYLE, height = SUMMARY_TEXT_HEIGHT, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET])
                data_quality = pn.pane.Markdown("{:.2%} Data Present".format(data[col]["count"] / (data[col]["null"] + data[col]["count"])), styles=TEXT_STYLE, height = SUMMARY_TEXT_HEIGHT, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET])

                if "histogram" in data[col]:
                    value_distribution = pn.pane.ECharts({
                        "xAxis": {
                            "type": "category",
                            "show": False,
                            "data": data[col]["histogram"]["bins"],
                            "axisLine": {"lineStyle": {"color": AXIS_COLOR}}
                            
                        },
                        "yAxis": {
                            "type": "value",
                            "axisLine": {"lineStyle": {"color": AXIS_COLOR}}
                        },
                        'tooltip': {},
                        "series": [
                        {
                            "data": data[col]["histogram"]["counts"],
                            "type": "bar",
                            "barWidth": "100%",
                            "itemStyle": {
                                "color": PLOT_COLOR
                            },
                        }
                        ],
                        "grid": {
                            "containLabel": True,
                            "left": "0",
                            "top": "10%",
                            "right": "10%",
                            "bottom": "0",
                        },
                        "aria": {
                            "enabled": True,
                            "decal": {
                                "show": True,
                            }
                        }}, theme = ECHART_TEMPLATE, styles=GRAPH_STYLE, width = PLOT_WIDTH, height = PLOT_HEIGHT, margin =(0,0,0,0))

                else:
                    value_distribution = pn.Column(pn.Row(pn.pane.Markdown("N/A", styles = TEXT_STYLE, align = ("center", "center"), margin =(0,0,0,0), stylesheets=[TEXT_STYLESHEET]), height = PLOT_HEIGHT, align = ("center", "center"), margin =(0,0,0,0)), width = PLOT_WIDTH, margin =(0,0,0,0))

                frequent_results = pn.pane.ECharts({
                        "yAxis": {
                            "type": "category",
                            "data": data[col]["frequent"]["keys"],
                            "inverse": True,
                            "axisLine": {"lineStyle": {"color": AXIS_COLOR}},
                            "axisLabel": {"width": 45, "overflow": "truncate"}
                        },
                        "xAxis": {
                            "type": "value",
                            "axisLine": {"lineStyle": {"color": AXIS_COLOR}},
                        },
                        'tooltip': {},
                        "series": [
                        {
                            "data": data[col]["frequent"]["values"],
                            "type": "bar",
                            "itemStyle": {
                                "color": PLOT_COLOR
                            },
                        }
                        ],
                        "grid": {
                            "left": "55",
                            "top": "10%",
                            "right": "10%",
                            "bottom": "30",
                        },
                        "aria": {
                            "enabled": True,
                            "decal": {
                                "show": True
                            }
                        }}, theme = ECHART_TEMPLATE, styles=GRAPH_STYLE, width = PLOT_WIDTH, height = PLOT_HEIGHT, margin =(0,0,0,0)
                )

                if "median" in data[col]:
                    box_plot = pn.pane.ECharts({
                        "yAxis": {
                            "show": False,
                            "data": [col], 
                            "type": "category",
                            "axisLine": {"lineStyle": {"color": AXIS_COLOR}}
                        },
                        "xAxis": {
                            "type": "value",
                            "scale": True,
                            "axisLine": {"lineStyle": {"color": AXIS_COLOR}}
                        },
                        'tooltip': {},
                        "series": [
                        {
                            "data": [[data[col]["min"], data[col]["Q1"], data[col]["median"], data[col]["Q3"], data[col]["max"]]],
                            "type": "boxplot",
                            "itemStyle": {
                                "color": PLOT_COLOR
                            },
                        }
                        ],
                        "grid": {
                            "show": True,
                            "left": "6%",
                            "top": "10%",
                            "right": "6%%",
                            "bottom": "20",
                        },
                        "aria": {
                            "enabled": True,
                            "decal": {
                                "show": True
                            }
                        }}, theme = ECHART_TEMPLATE, width = PLOT_WIDTH, height = PLOT_HEIGHT, margin =(0,0,0,0)
                    )
                else:
                    box_plot = pn.Column(pn.Row(pn.pane.Markdown("N/A", styles = TEXT_STYLE, align = ("center", "center")), height = PLOT_HEIGHT, align = ("center", "center"), stylesheets=[TEXT_STYLESHEET]), width = PLOT_WIDTH)

                cols.append(
                    pn.Column(
                        column_name,
                        data_type,
                        count,
                        distinct,
                        null,
                        data_quality,
                        value_distribution,
                        frequent_results,
                        box_plot,
                    )
                )

            return pn.Row(*cols, styles = PAGE_STYLE, height = GENERAL_HEIGHT)
        except Exception as e:
            return self.generate_exception_card(e)

    # Creates home page to select individual columns to view
    def column_home(self):
        heading = pn.pane.Markdown(f"<h3>{COLUMN_HEADER}</h3>", stylesheets=[TEXT_STYLESHEET], align=("center", "center"), sizing_mode="fixed")
        interactive_selects = self.generate_interactive_selects(context=ViewType.COLUMN)
        column_select = pn.widgets.MultiChoice(
            name=COLUMN_SELECTOR_NAME,
            options=self.keys,
            value=self.column_tab_list,
            delete_button=False,
            solid=True,
            stylesheets=[TEXT_STYLESHEET, BUTTON_STYLESHEET],
            sizing_mode="stretch_width",
            min_width=HALF_SELECT_WIDTH,
        )
        column_select.link(heading, callbacks={'value': self.update_column_view_from_column_search})
        return pn.Column(
            pn.Row(heading, interactive_selects, sizing_mode="stretch_width"),
            column_select,
            styles = PAGE_STYLE,
            scroll = "x-auto",
            height = COLUMN_HOME_HEIGHT,
        )

    # Template for individual column view
    def column_view(self, col):
        try:
            heading = pn.pane.Markdown(f"<h3>{col} Data Visualization</h3>", stylesheets=[TEXT_STYLESHEET], align=("center", "center"), sizing_mode="fixed")
            metric = pn.pane.Markdown(
                f"""Total Rows in DataFrame: {self.metadata["original_df_size"]}\nTotal Rows Sampled: {self.metadata["rows_sampled"]}\nMethod Used: {self.metadata["sampling_method"]}""",
                margin = (0,0,0,0),
                align="end",
                styles={"text-align": "right"},
                stylesheets=[TEXT_STYLESHEET],
                sizing_mode="fixed",
                hard_line_break=True,
            )

            run_statement_data = run_statement(session_manager = self.session_manager, statement = f"""{self.display_magic_compute}.generate_column_schema(column = "{col}")""", mode = "eval")
            column_data = json.loads(run_statement_data.encode('utf-8').decode('unicode_escape'))[col]

            sum_data = pn.Row(
                pn.pane.Markdown(f"<h4>{COLUMN_NAME_HEADER}\n\n{col}</h4>", styles = TEXT_STYLE, sizing_mode = "stretch_width", stylesheets=[TEXT_STYLESHEET], hard_line_break=True),
                pn.pane.Markdown(f"""<h4>{DATA_TYPE_HEADER}\n\n{column_data["dtype"]}</h4>""", styles = TEXT_STYLE, sizing_mode = "stretch_width", stylesheets=[TEXT_STYLESHEET], hard_line_break=True),
                pn.pane.Markdown(f"""<h4>{COUNT_HEADER}\n\n{int(column_data["count"])}</h4>""", styles = TEXT_STYLE, sizing_mode = "stretch_width", stylesheets=[TEXT_STYLESHEET], hard_line_break=True),
                pn.pane.Markdown(f"""<h4>{DISTINCT_HEADER}\n\n{column_data["distinct"]}</h4>""", styles = TEXT_STYLE, sizing_mode = "stretch_width", stylesheets=[TEXT_STYLESHEET], hard_line_break=True),
                pn.pane.Markdown(f"""<h4>{NULL_HEADER}\n\n{column_data["null"]}</h4>""", styles = TEXT_STYLE, sizing_mode = "stretch_width", stylesheets=[TEXT_STYLESHEET], hard_line_break=True),
                sizing_mode = "stretch_width", align = ("center", "center")
            )

            if "histogram" in column_data:
                value_distribution = pn.pane.ECharts({
                    "xAxis": {
                        "type": "category",
                        "data": column_data["histogram"]["bins"],
                        "axisLine": {"lineStyle": {"color": AXIS_COLOR}}
                    },
                    "yAxis": {
                        "type": "value",
                        "axisLine": {"lineStyle": {"color": AXIS_COLOR}}
                    },
                    'tooltip': {},
                    "series": [
                    {
                        "data": column_data["histogram"]["counts"],
                        "type": "bar",
                        "barWidth": "100%",
                        "itemStyle": {
                            "color": PLOT_COLOR
                        },
                    }
                    ],
                    "grid": {
                        "containLabel": True,
                        "left": "0",
                        "top": "10%",
                        "right": "3%",
                        "bottom": "0",
                    },
                    "aria": {
                        "enabled": True,
                        "decal": {
                            "show": True
                        }
                    },
                    "title": {
                        "left": 'center',
                        "text": VALUE_DISTRIBUTION_HEADER,
                        "textStyle": {"color" : TEXT_COLOR}
                    }}, theme = ECHART_TEMPLATE, styles=GRAPH_STYLE, sizing_mode = "stretch_both")
                
            else:
                value_distribution = pn.pane.Markdown(
                    f"<h4>{VALUE_DISTRIBUTION_HEADER} not applicable for categorical data</h4>",
                    styles = TEXT_STYLE, align = ("center", "center"), sizing_mode = "stretch_both", stylesheets=[TEXT_STYLESHEET]
                )

            frequent_results = pn.pane.ECharts({
                "yAxis": {
                    "type": "category",
                    "data": column_data["frequent"]["keys"],
                    "inverse": True,
                    "axisLine": {"lineStyle": {"color": AXIS_COLOR}},
                    "axisLabel": {"width": 70, "overflow": "truncate"}
                },
                "xAxis": {
                    "type": "value",
                    "axisLine": {"lineStyle": {"color": AXIS_COLOR}},
                },
                'tooltip': {},
                "series": [
                {
                    "data": column_data["frequent"]["values"],
                    "type": "bar",
                    "itemStyle": {
                        "color": PLOT_COLOR
                    },
                }
                ],
                "grid": {
                    "left": "100",
                    "top": "5%",
                    "right": "5%",
                    "bottom": "30",
                },
                "aria": {
                    "enabled": True,
                    "decal": {
                        "show": True
                    }
                },
                "title": {
                    "left": 'center',
                    "text": FREQUENT_RESULTS_HEADER,
                    "textStyle": {"color" : TEXT_COLOR}
                }}, theme = ECHART_TEMPLATE, styles=GRAPH_STYLE, sizing_mode = "stretch_both", margin =(0,0,0,0)
            )
        
            if "median" in column_data:
                box_plot = pn.Row(
                    pn.Column(
                        pn.pane.Markdown(f"**Min:** {column_data['min']}", styles = TEXT_STYLE, stylesheets=[TEXT_STYLESHEET]),
                        pn.pane.Markdown(f"**Q1:** {column_data['Q1']}", styles = TEXT_STYLE, stylesheets=[TEXT_STYLESHEET]),
                        pn.pane.Markdown(f"**Median:** {column_data['median']}", styles = TEXT_STYLE, stylesheets=[TEXT_STYLESHEET]),
                        pn.pane.Markdown(f"**Q3:** {column_data['Q3']}", styles = TEXT_STYLE, stylesheets=[TEXT_STYLESHEET]),
                        pn.pane.Markdown(f"**Max:** {column_data['max']}", styles = TEXT_STYLE, stylesheets=[TEXT_STYLESHEET]),
                        align = "center", margin=(0,0,0,15)
                    ),
                    pn.pane.ECharts({
                        "yAxis": {
                            "type": "category",
                            "data": [col],
                            "show": False,
                            "axisLine": {"lineStyle": {"color": AXIS_COLOR}}
                        },
                        "xAxis": {
                            "type": "value",
                            "scale": True,
                            "axisLine": {"lineStyle": {"color": AXIS_COLOR}}
                        },
                        'tooltip': {},
                        "series": [
                        {
                            "data": [[column_data["min"], column_data["Q1"], column_data["median"], column_data["Q3"], column_data["max"]]],
                            "type": "boxplot",
                            "itemStyle": {
                                "color": PLOT_COLOR
                            },
                        }
                        ],
                        "grid": {
                            "left": "10",
                            "top": "10%",
                            "right": "5%",
                            "bottom": "20",
                        },
                        "aria": {
                            "enabled": True,
                            "decal": {
                                "show": True
                            }
                        },
                        "title": {
                            "left": 'center',
                            "text": BOX_PLOT_HEADER,
                            "textStyle": {"color" : TEXT_COLOR}
                        }}, theme = ECHART_TEMPLATE, sizing_mode = "stretch_both", margin =(0,0,0,0)
                    )
                )
            else:
                box_plot = pn.pane.Markdown(
                    f"<h4>{BOX_PLOT_HEADER} not applicable for categorical data</h4>",
                    styles = TEXT_STYLE, align = ("center", "center"), sizing_mode = "stretch_both", stylesheets=[TEXT_STYLESHEET]
                )
        

            graphs = pn.Row(
                pn.Column(
                    box_plot,
                    value_distribution,
                    styles = {"width": "75%"}
                ),
                pn.Column(frequent_results, styles = {"width": "25%"}),
                sizing_mode = "stretch_both", align = ("center", "center")
            )
        
            return pn.Column(
                pn.Row(
                    heading,
                    pn.Column(
                        metric,
                        align = "end", 
                        sizing_mode = "stretch_width"
                    ),
                    align = "center",
                    sizing_mode = "stretch_width"
                ),
                sum_data,
                graphs,
                styles = PAGE_STYLE,
                scroll = "x-auto",
                height = GENERAL_HEIGHT
            )
        except Exception as e:
            return self.generate_exception_card(e)
    
    def plot_view(self):
        return pn.Column(
            self.plot_header(),
            self.plot_data(),
            scroll = "x-auto",
        )
    
    def plot_header(self):
        heading = pn.pane.Markdown(f"<h3>{PLOT_HEADER}</h3>", stylesheets=[TEXT_STYLESHEET], align=("center", "center"), sizing_mode="fixed")
        interactive_selects = self.generate_interactive_selects(context=ViewType.PLOT)
        return pn.Row(
            heading,
            interactive_selects,
            sizing_mode="stretch_width"
        )

    # Generates view for the chart in the plotting view
    def plot_data(self):
        try:
            if self.plot_lib is PlotLibraries.DEFAULT:
                chart_type_select = pn.widgets.RadioButtonGroup(
                    name=CHART_TYPE_SELECTOR_NAME,
                    options=CHART_TYPE_OPTIONS,
                    value="Line",
                    button_type='light',
                    button_style="outline",
                    align=('center', 'center'),
                    stylesheets=[TEXT_STYLESHEET, BUTTON_STYLESHEET],
                    sizing_mode="fixed",
                )
                x_axis_select = pn.widgets.Select(
                    name=X_AXIS_SELECTOR_NAME,
                    options=self.keys,
                    value=self.keys[0],
                    align=('center', 'center'),
                    stylesheets=[TEXT_STYLESHEET, SELECT_STYLESHEET],
                    sizing_mode="stretch_width",
                    min_width=HALF_SELECT_WIDTH,
                )
                y_axis_select = pn.widgets.Select(
                    name=Y_AXIS_SELECTOR_NAME,
                    options=self.keys,
                    value=self.keys[0],
                    align=('center', 'center'),
                    stylesheets=[TEXT_STYLESHEET, SELECT_STYLESHEET],
                    sizing_mode="stretch_width",
                    min_width=HALF_SELECT_WIDTH,
                )
                x_axis_type_select = pn.widgets.Select(
                    name=X_AXIS_TYPE_SELECTOR_NAME,
                    options=AXIS_TYPE_OPTIONS,
                    value="Category",
                    align=('center', 'center'),
                    stylesheets=[TEXT_STYLESHEET, SELECT_STYLESHEET],
                    sizing_mode="stretch_width",
                    min_width=HALF_SELECT_WIDTH,
                )
                y_axis_type_select = pn.widgets.Select(
                    name=Y_AXIS_TYPE_SELECTOR_NAME,
                    options=AXIS_TYPE_OPTIONS,
                    value="Value",
                    align=('center', 'center'),
                    stylesheets=[TEXT_STYLESHEET, SELECT_STYLESHEET],
                    sizing_mode="stretch_width",
                    min_width=HALF_SELECT_WIDTH,
                )

                agg_select = pn.widgets.Select(
                    name=AGGREGATION_FUNCTION_SELECTOR_NAME,
                    options=AGGREGATION_FUNCTION_OPTIONS,
                    value="Mean",
                    align = ('center', 'center'),
                    stylesheets=[TEXT_STYLESHEET, SELECT_STYLESHEET],
                    sizing_mode="stretch_width",
                    min_width=HALF_SELECT_WIDTH,
                )

                chart_type_select.link([x_axis_select, y_axis_select, agg_select, x_axis_type_select, y_axis_type_select, chart_type_select], callbacks={'value': self.update_echart_view})
                x_axis_select.link([x_axis_select, y_axis_select, agg_select, x_axis_type_select, y_axis_type_select, chart_type_select], callbacks={'value': self.update_echart_view})
                y_axis_select.link([x_axis_select, y_axis_select, agg_select, x_axis_type_select, y_axis_type_select, chart_type_select], callbacks={'value': self.update_echart_view})
                agg_select.link([x_axis_select, y_axis_select, agg_select, x_axis_type_select, y_axis_type_select, chart_type_select], callbacks={'value': self.update_echart_view})
                x_axis_type_select.link([x_axis_select, y_axis_select, agg_select, x_axis_type_select, y_axis_type_select, chart_type_select], callbacks={'value': self.update_echart_view})
                y_axis_type_select.link([x_axis_select, y_axis_select, agg_select, x_axis_type_select, y_axis_type_select, chart_type_select], callbacks={'value': self.update_echart_view})


                echart_data = run_statement(session_manager = self.session_manager, statement = f"""{self.display_magic_compute}.generate_echart_data("{x_axis_select.value}", "{y_axis_select.value}", "{agg_select.value.lower()}")""", mode = "eval")
                echart_pane = self.generate_echart_pane(echart_data, chart_type_select.value.lower(), x_axis_select.value, y_axis_select.value, x_axis_type_select.value.lower(), y_axis_type_select.value.lower())

                return pn.Column(
                    pn.Row(chart_type_select),
                    pn.Row(
                        x_axis_select,
                        x_axis_type_select,
                    ),
                    pn.Row(y_axis_select, y_axis_type_select, agg_select),
                    echart_pane,
                    styles=PAGE_STYLE,
                    height=GENERAL_HEIGHT,
                )

            # Set up third-party plotting library visualizations
            else:
                plot_html = None
                iframe_height = "100%"
                if self.plot_lib is PlotLibraries.PYGWALKER:
                    dark_theme = False
                    try:
                        # Read jupyterlab theme settings file to determine current theme
                        # This is used to set pygwalker to dark mode (only pygwalker supports it for now)
                        config_dir = jupyter_config_dir()
                        lab_theme_user_settings_file = os.path.join(config_dir, 'lab', 'user-settings', '@jupyterlab', 'apputils-extension','themes.jupyterlab-settings')
                        with open(lab_theme_user_settings_file) as json_data:
                            theme = json.load(json_data, cls=JSONWithCommentsDecoder)
                            if "dark" in theme["theme"].lower():
                                dark_theme = True
                    except Exception:
                        # If the theme config file does not exist, the default theme (SageMaker Dark) has not changed
                        dark_theme = True
                    try:
                        import pygwalker as pyg
                    except ModuleNotFoundError as e:
                        raise ModuleNotFoundError(f"Missing pygwalker on Jupyterlab space. Error: {e}")
                    pyg.GlobalVarManager.set_privacy("offline")
                    appearance = "dark" if dark_theme else "light"
                    plot_html = html.escape(pyg.to_html(self.sample_df, appearance=appearance, theme_key="vega"))
                    # The pygwalker HTML needs extra processing to remove excess whitespace around the borders and bottom of the iframe
                    iframe_height = "968px"
                    plot_html = f"<html><body style=&quot;margin:1px;&quot;>{plot_html}</body></html>"
                elif self.plot_lib is PlotLibraries.YDATA:
                    try:
                        from ydata_profiling import ProfileReport
                    except ModuleNotFoundError as e:
                        raise ModuleNotFoundError(f"Missing ydata-profiling on Jupyterlab space. Error: {e}")
                    profile = ProfileReport(self.sample_df, sort=None)
                    profile.config.html.navbar_show = False
                    plot_html = html.escape(profile.to_html())
                elif self.plot_lib is PlotLibraries.DATAPREP:
                    try:
                        from dataprep.eda import create_report
                    except ModuleNotFoundError as e:
                        raise ModuleNotFoundError(f"Missing dataprep on Jupyterlab space. Error: {e}")
                    report = create_report(self.sample_df)
                    plot_html = html.escape(report)
                pane = pn.pane.HTML(f"""<iframe srcdoc="{plot_html}" frameBorder="0" width="100%" height="{iframe_height}" allowfullscreen></iframe>""", sizing_mode = "stretch_both")
                return pn.Column(pane, height=GENERAL_HEIGHT, styles=PAGE_STYLE)
        except Exception as e:
            return self.generate_exception_card(e)

    # Creates EChart Pane to display in the default plotting view
    def generate_echart_pane(self, echart_data, echart_type, x_axis, y_axis, x_axis_type, y_axis_type):
        # echart_data is a plotting error message
        if isinstance(echart_data, str):
            echart_config = {
                "xAxis": {
                    "type": x_axis_type,
                    "name": x_axis,
                    "min": "dataMin",
                    "nameLocation": "center",
                    "axisLine": {"lineStyle": {"color": AXIS_COLOR}},
                    "nameGap": 30
                },
                "yAxis": {
                    "type": y_axis_type,
                    "nameLocation": "center",
                    "name": y_axis,
                    "axisLabel": {"show": True, "width": 45, "overflow": "truncate"},
                    "axisLine": {"show": True, "lineStyle": {"color": AXIS_COLOR}},
                    "nameGap": 45,
                    "show": True,
                    "splitLine": {
                        "show": True
                    },
                },
                'tooltip': {},
                "series": [
                {
                    "type": "line",
                    "itemStyle": {
                            "color": PLOT_COLOR
                    },
                    "symbolSize": 8
                }
                ],
                "grid": {
                    "containLabel": True,
                    "left": "35",
                    "top": "5%",
                    "right": "5%",
                    "bottom": "30",
                },
                "title": {
                    "left": 'center',
                    "textStyle": {"color" : TEXT_COLOR}
                }, 
                "dataset" : {
                    "source" : {
                        x_axis: [0],
                        y_axis: [0]
                    }
                },
                "graphic": {
                    "type": "text",
                    "left": "center",
                    "top": "middle",
                    "style": { "text": echart_data, "fill" : AXIS_COLOR },
                },
            }
        # echart_data is valid data that needs to be plotted
        else:
            if echart_type == "pie":
                echart_config = {
                    "xAxis": {
                        "type": x_axis_type,
                        "name": x_axis,
                        "nameLocation": "center",
                        "axisLine": {"lineStyle": {"color": AXIS_COLOR}},
                        "data": echart_data[0],
                        "show": False
                    },
                    "yAxis": {
                        "type": y_axis_type,
                        "nameLocation": "center",
                        "name": y_axis,
                        "axisLine": {"lineStyle": {"color": AXIS_COLOR}},
                        "show": False
                    },
                    'tooltip': {},
                    "series": [
                    {
                        "type": echart_type,
                        "data": echart_data[1],
                        "radius": "60%"
                    }
                    ],
                    "grid": {
                        "left": "10%",
                        "top": "10%",
                        "right": "10%",
                        "bottom": "10%",
                    },
                    "title": {
                        "left": 'center',
                        "textStyle": {"color" : TEXT_COLOR}
                    }
                }
            else:
                echart_config = {
                    "xAxis": {
                        "type": x_axis_type,
                        "name": x_axis,
                        "min": "dataMin",
                        "nameLocation": "center",
                        "axisLine": {"lineStyle": {"color": AXIS_COLOR}},
                        "nameGap": 30
                    },
                    "yAxis": {
                        "type": y_axis_type,
                        "nameLocation": "center",
                        "name": y_axis,
                        "axisLabel": {"width": 45, "overflow": "truncate"},
                        "axisLine": {"lineStyle": {"color": AXIS_COLOR}},
                        "nameGap": 45
                    },
                    'tooltip': {},
                    "series": [
                    {
                        "type": echart_type,
                        "itemStyle": {
                                "color": PLOT_COLOR
                        },
                        "symbolSize": 8
                    }
                    ],
                    "grid": {
                        "containLabel": True,
                        "left": "35",
                        "top": "5%",
                        "right": "5%",
                        "bottom": "30",
                    },
                    "title": {
                        "left": 'center',
                        "textStyle": {"color" : TEXT_COLOR}
                    }, 
                    "dataset" : {
                        "source" : {
                            x_axis: echart_data[0],
                            y_axis: echart_data[1]
                        }
                    }
                }
        return pn.Row(pn.pane.ECharts(echart_config, theme=ECHART_TEMPLATE, styles=GRAPH_STYLE), sizing_mode="stretch_both")

    def table_view(self):
        return pn.Column(
            self.table_header(),
            self.table_data(),
            scroll = "x-auto",
        )

    def table_header(self):
        heading = pn.pane.Markdown(f"<h3>{TABLE_HEADER}</h3>", stylesheets=[TEXT_STYLESHEET], align=("center", "center"), sizing_mode="fixed")
        interactive_selects = self.generate_interactive_selects(context=ViewType.TABLE)
        return pn.Row(heading, interactive_selects, sizing_mode="stretch_width")

    def table_data(self):
        try:
            tabulator_pane = pn.widgets.Tabulator(
                self.sample_df, disabled=True, selectable=False, page_size=self.table_rows_per_page,
                sortable=False, pagination="remote", layout="fit_data_stretch", header_align="center", text_align="center",
                sizing_mode="stretch_width", stylesheets=[TEXT_STYLESHEET, TABULATOR_STYLESHEET], theme_classes=['table-sm']
            )
            return pn.Column(tabulator_pane, styles=PAGE_STYLE)
        except Exception as e:
            return self.generate_exception_card(e)

    # Creates interactive selects that are available on every page. Used to control the sampling method, sample size, and plotting library directly from the UI
    def generate_interactive_selects(self, context: ViewType):
        sampling_method_select = pn.widgets.Select(
            name=SAMPLING_METHOD_SELECTOR_NAME,
            options=SAMPLING_METHOD_OPTIONS,
            value=self.metadata["sampling_method"].capitalize(),
            align=('center', 'center'),
            stylesheets=[TEXT_STYLESHEET, SELECT_STYLESHEET],
            sizing_mode="stretch_width",
            min_width=HALF_SELECT_WIDTH,
        )
        sampling_method_select.link(self.summary_tab_index, callbacks={'value': self.update_sampling_method})

        frequency_options = [2000, 5000, 10000]
        if self.metadata["sampling_size"] not in frequency_options:
            frequency_options.append(self.metadata["sampling_size"])
            frequency_options.sort()
        frequency_options = [option for option in frequency_options if option <= self.metadata["original_df_size"]]

        frequency_select = pn.widgets.Select(
            name=SAMPLE_SIZE_SELECTOR_NAME,
            options=frequency_options,
            value=self.metadata["sampling_size"],
            align=('center', 'center'),
            stylesheets=[TEXT_STYLESHEET, SELECT_STYLESHEET],
            sizing_mode="stretch_width",
            min_width=HALF_SELECT_WIDTH,
        )
        frequency_select.link(self.summary_tab_index, callbacks={'value': self.update_size})
        selects_to_display = [sampling_method_select, frequency_select] if frequency_options else []
        metric = pn.pane.Markdown(
            f"""Total Rows in DataFrame: {self.metadata["original_df_size"]}\nTotal Rows Sampled: {self.metadata["rows_sampled"]}\nMethod Used: {self.metadata["sampling_method"]}""",
            margin=(0,0,0,0),
            align = "end",
            styles={"text-align": "right"},
            stylesheets=[TEXT_STYLESHEET],
            sizing_mode="fixed",
            hard_line_break=True,
        )

        if context is ViewType.PLOT:
            disabled_options = []
            # Determine options that need to be disabled when selecting plotting libraries
            # Options are disabled if the library is not installed, the selector tooltip indicates this to the user
            try:
                import pygwalker as pyg
            except ModuleNotFoundError as e:
                disabled_options.append(PlotLibraries.PYGWALKER.value)
            try:
                from ydata_profiling import ProfileReport
            except ModuleNotFoundError as e:
                disabled_options.append(PlotLibraries.YDATA.value)
            try:
                from dataprep.eda import create_report
            except ModuleNotFoundError as e:
                disabled_options.append(PlotLibraries.DATAPREP.value)
            plot_lib_select = pn.widgets.Select(
                name=PLOTTING_LIBRARY_SELECTOR_NAME,
                options=[lib.value for lib in PlotLibraries],
                disabled_options=disabled_options,
                value=self.plot_lib.value,
                align=('center', 'center'),
                stylesheets=[TEXT_STYLESHEET, SELECT_STYLESHEET],
                sizing_mode="stretch_width",
                min_width=HALF_SELECT_WIDTH,
                description="To enable the use of third-party data visualization libraries, install the corresponding libraries in the space."
            )
            plot_lib_select.link(self.plot_tab_index, callbacks={'value': self.update_plot_lib})
            selects_to_display.append(plot_lib_select)
        elif context is ViewType.TABLE:
            table_row_per_page_select = pn.widgets.Select(
                name=ROWS_PER_PAGE_SELECTOR_NAME,
                options=ROWS_PER_PAGE_OPTIONS,
                value=self.table_rows_per_page,
                align=('center', 'center'),
                stylesheets=[TEXT_STYLESHEET, SELECT_STYLESHEET],
                sizing_mode="stretch_width",
                min_width=HALF_SELECT_WIDTH,
            )
            table_row_per_page_select.link(self.table_tab_index, callbacks={'value': self.update_table_rows_per_page})
            selects_to_display.append(table_row_per_page_select)

        if selects_to_display:
            return pn.Row(
                pn.Row(
                    *selects_to_display,
                    align="center",
                    sizing_mode="stretch_width"
                ),
                pn.Column(
                    metric,
                    align="end",
                    sizing_mode="fixed"
                ),
                align="center",
                sizing_mode="stretch_width"
            )
        else:
            return pn.Row(
                pn.Column(
                    metric,
                    align="end",
                    sizing_mode="fixed"
                ),
                align="center",
                sizing_mode="stretch_width"
            )

    # Refreshes all views upon interaction with the UI where the sampling method or sample size was changed. 
    def update_views(self):
        # When sampling techniques updated, update all available views
        if self.table_tab_index is not None: # refreshes table tab
            self.output[self.table_tab_index][0][-1] = self.generate_loading_spinner()
            self.output[self.table_tab_index][0] = self.table_view()
        if self.summary_tab_index is not None: # refreshes summary tab
            self.output[self.summary_tab_index][0][-1] = self.generate_loading_spinner()
            self.output[self.summary_tab_index][0] = self.summary_view()
        if self.column_tab_index is not None: # refreshes column home page, leaving open column pages intact
            heading = pn.pane.Markdown(f"<h3>Column Data Visualization</h3>", stylesheets=[TEXT_STYLESHEET], align = ("center", "center"))
            interactive_selects = self.generate_interactive_selects(context = "column")
            self.output[self.column_tab_index][0][0][0] = pn.Row(heading, interactive_selects) # Different in order to mantain full interactivity with column home, resets column home page interactive selects, but not the dropdown
        if self.plot_tab_index is not None: # refreshes plotting page
            self.output[self.plot_tab_index][0][-1] = self.generate_loading_spinner()
            self.output[self.plot_tab_index][0] = self.plot_view()
        if self.output.active:
            self.output.active = [self.output.active[0]]

    # EVENT HANDLERS for UI interaction
    # User updates sampling method from any sampling method select object
    def update_sampling_method(self, target, event):
        try:
            run_statement(session_manager = self.session_manager, statement = f"""{self.display_magic_compute}.set_sampling_method("{event.new.lower()}")""")
            run_statement(session_manager = self.session_manager, statement = f"""{self.display_magic_compute}.sample()""")
            run_statement_data = run_statement(session_manager = self.session_manager, statement = f"""{self.display_magic_compute}.get_metadata()""", mode = "eval")
            self.metadata = json.loads(run_statement_data.encode('utf-8').decode('unicode_escape'))
            self.sample_df = self.get_sampled_dataframe()
            self.update_views()
        except Exception as e:
            self.output[self.output.active[0]][0][-1] = self.generate_exception_card(e)

    # User updates sample size from any size select object
    def update_size(self, target, event):
        try:
            run_statement(session_manager = self.session_manager, statement = f"""{self.display_magic_compute}.set_size({event.new})""")
            run_statement(session_manager = self.session_manager, statement = f"""{self.display_magic_compute}.sample()""")
            run_statement_data = run_statement(session_manager = self.session_manager, statement = f"""{self.display_magic_compute}.get_metadata()""", mode = "eval")
            self.metadata = json.loads(run_statement_data.encode('utf-8').decode('unicode_escape'))
            self.sample_df = self.get_sampled_dataframe()
            self.update_views()
        except Exception as e:
            self.output[self.output.active[0]][0][-1] = self.generate_exception_card(e)

    # Generates new column view when a column is selected in the column selector
    def update_column_view_from_column_search(self, target, event):
        columns_tab = self.output[self.column_tab_index]
        new_col_list = event.new
        num_existing_columns_shown = len(self.column_tab_list)
        for col in new_col_list[num_existing_columns_shown:]:
            if col not in self.column_tab_list:
                col_view = self.column_view(col)  # Call function to generate new column_view
                columns_tab.append((ACCORDION_TEXT_STYLESHEET + col, col_view))
                self.column_tab_list.append(col)

    # Generates new column view when column name button clicked from Summary View
    def update_column_view_from_summary(self, event):
        col = event.obj.name  # Get the column name from the clicked button
        columns_tab = self.output[self.column_tab_index]
        # Do not create a new tab if the column has already been selected previously
        column_index = len(columns_tab.objects)
        for i in range(len(self.column_tab_list)):
            if self.column_tab_list[i] == col:
                column_index = i + 1
        if column_index == len(columns_tab.objects):
            col_view = self.column_view(col)  # Call the generate_view() function to create the new dashboard
            columns_tab.append((ACCORDION_TEXT_STYLESHEET + col, col_view))
            self.column_tab_list.append(col)
        # Jump to column details
        self.output.active = [self.column_tab_index]
        columns_tab.active = [column_index]

    # Update the number of rows displayed in the paginated table
    def update_table_rows_per_page(self, target, event):
        try:
            self.output[self.table_tab_index][0][-1] = self.generate_loading_spinner()
            self.table_rows_per_page = event.new
            self.output[self.table_tab_index][0] = self.table_view()
        except Exception as e:
            self.output[self.table_tab_index][-1][-1] = self.generate_exception_card(e)

    # Updates the plot library and regenerates a new view dependent on the plot library
    def update_plot_lib(self, target, event):
        try:
            self.output[self.plot_tab_index][-1][-1] = self.generate_loading_spinner()
            self.plot_lib = PlotLibraries(event.new.lower())
            new_plot = self.plot_data()
            self.output[self.plot_tab_index][-1][-1] = new_plot
        except Exception as e:
            self.output[self.plot_tab_index][-1][-1] = self.generate_exception_card(e)

    # Generates new echart pane and replaces old pane upon interaction with EChart selections (x-axis, y-axis, agg_select)
    # target is a list where the select objects are stored in following order (x_axis_select, y_axis_select, agg_select, x_axis_type_select, chart_type_select)
    def update_echart_view(self, target, event):
        try:
            self.output[self.plot_tab_index][-1][-1][-1] = self.generate_loading_spinner()
            echart_data = run_statement(session_manager = self.session_manager, statement = f"""{self.display_magic_compute}.generate_echart_data("{target[0].value}", "{target[1].value}", "{target[2].value.lower()}")""", mode = "eval")
            echart_pane = self.generate_echart_pane(echart_data, echart_type = target[5].value.lower(), x_axis = target[0].value, y_axis = target[1].value, x_axis_type = target[3].value.lower(), y_axis_type = target[4].value.lower())
            self.output[self.plot_tab_index][-1][-1][-1] = echart_pane
        except Exception as e:
            self.output[self.plot_tab_index][-1][-1][-1] = self.generate_exception_card(e)

    def generate_loading_spinner(self):
        return pn.Row(
            pn.indicators.LoadingSpinner(value=True, size=20, name='Kernel is busy, loading...'),
            align = 'center'
        )

    def generate_exception_card(self, exception):
        formatted_stack_trace = "".join(traceback.format_exception(exception))
        return pn.Column(
            pn.Row(pn.pane.Markdown("An exception occurred while rendering the data visualization."), stylesheets=[TEXT_STYLESHEET]),
            pn.Row(
                pn.layout.Card(
                    pn.pane.Markdown(f"```\n{formatted_stack_trace}\n```", stylesheets=[TEXT_STYLESHEET], hard_line_break=True),
                    title = 'Traceback',
                    collapsed = True
                )
            )
        )

