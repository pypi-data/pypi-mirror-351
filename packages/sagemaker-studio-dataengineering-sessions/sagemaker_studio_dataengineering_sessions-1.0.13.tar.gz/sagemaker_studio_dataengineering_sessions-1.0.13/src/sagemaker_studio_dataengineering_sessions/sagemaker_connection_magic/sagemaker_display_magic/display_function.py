import logging
from IPython import get_ipython

from sagemaker_studio_dataengineering_sessions.sagemaker_connection_magic.sagemaker_display_magic.display_render import DisplayMagicRender
from sagemaker_studio_dataengineering_sessions.sagemaker_connection_magic.sagemaker_display_magic.run_statement import generate_var_name_for_compute, run_statement

logger = logging.getLogger(__name__)


def create_display_magic_render(
    df,
    session_manager,
    last_line_execution=False,
    spark_session=False,
    size=10_000,
    sampling_method="head",
    columns=None,
    type_inference=False,
    plot_lib="default",
    view="all",
    spark_use_threshold=1_000_000,
    max_sample=1_000_000_000,
    graph_render_threshold=1_000_000,
) -> DisplayMagicRender:
    # GET VARIABLE NAME TO USE ON COMPUTE AND STORE DISPLAYMAGICCOMPUTE OBJECT INTO
    var_str = generate_var_name_for_compute("_display_magic_")

    # There are two cases where the create_display_magic_render() function is called. One where the df argument is an instance of a string.
    # This occurs when the user uses the magic and the variable name is parsed from the magic call as a string. As a result,
    # a slightly altered invocation of the DisplayMagicCompute class is needed to accomodate the parsing of this variable from
    # its presence on the compute. In the else statement, this typically occurs when the dataframe is of a dataframe type
    # (either pandas or pyspark) and this we can call the DisplayMagicCompute class directly without needing to add the parsing
    # from the namespace step. This will typically be invoked when performing eager execution from the connect magic when a
    #  dataframe is returned (typically from the DataBaseSessionManagers and SQL queries). This if/else statement is needed
    # to accomodate these two use-cases.

    # df is a variable name (used if called from magic or last statement of a pyspark cell evaluates to a dataframe)
    if isinstance(df, str):
        # Neccesary to send the display_compute.py code to the remote instance
        import importlib.resources as resources
        from .. import __name__ as pkg_name

        compute_path = resources.files(pkg_name) / "sagemaker_display_magic" / "display_compute.py"

        # SEND COMPUTE UTILS TO COMPUTE
        with compute_path.open() as f:
            display_magic_compute_class_code = f.read()
            run_statement(session_manager=session_manager, statement=display_magic_compute_class_code)

        # CREATE OBJECT ON COMPUTE
        create_compute = run_statement(
            session_manager=session_manager,
            statement=f"""{var_str} = DisplayMagicCompute(df={df}, size={size}, last_line_execution={last_line_execution}, sampling_method="{sampling_method}", spark_session={spark_session}, columns={columns}, type_inference={type_inference}, plot_lib="{plot_lib}", spark_use_threshold={spark_use_threshold}, max_sample={max_sample}, graph_render_threshold={graph_render_threshold})""",
        )
        # Return None, do not try to create a DisplayMagicRender object as it will fail if the DisplayMagicCompute creation fails
        if create_compute != "" and create_compute is not None:  # create compute also stores any warnings
            logger.warning(f"Warnings from display compute creation: {create_compute}")
            return None

    # df is a dataframe object on the local kernel (used as eager execution)
    # The only cases where this is applicable are for SQL queries in Athena/Redshift/EMR. In all of these cases, a pandas dataframe
    # is created on the local kernel to store the results.
    else:
        # Create OBJECT
        from .display_compute import DisplayMagicCompute

        try:
            display_magic_compute = DisplayMagicCompute(
                df=df,
                last_line_execution=last_line_execution,
                size=size,
                sampling_method=sampling_method,
                spark_session=spark_session,
                columns=columns,
                type_inference=type_inference,
                plot_lib=plot_lib,
                spark_use_threshold=spark_use_threshold,
                max_sample=max_sample,
                graph_render_threshold=graph_render_threshold,
            )
            # Send DisplayMagicCompute object to local IAM and set session manager to None to indicate local IAM execution.
            # Setting session_manager to None ensures that the local kernel is used for sampling the dataframe. Otherwise, SQL queries on
            # EMR compute will fail as Sparkmagic will return a pandas dataframe to the local kernel (for SQL queries), while the DisplayMagicRender
            # object will attempt to use the EMR session manager to find the dataframe (which does not exist in the EMR compute).
            get_ipython().user_ns[var_str] = display_magic_compute
            session_manager = None
        except Exception as e:
            logger.error(f"Could not create display compute: {e}")
            return None

    # Return object that will render UI on local IAM / loose leaf instance
    return DisplayMagicRender(display_magic_compute=var_str, session_manager=session_manager, plot_lib=plot_lib, view=view, columns=columns)
