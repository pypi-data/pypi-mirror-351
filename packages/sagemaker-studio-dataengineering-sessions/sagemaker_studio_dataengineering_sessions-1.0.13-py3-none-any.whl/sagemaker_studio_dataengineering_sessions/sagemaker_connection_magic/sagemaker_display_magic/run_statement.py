from IPython.display import display, HTML
from IPython import get_ipython
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.constants import Language
from sagemaker_studio_dataengineering_sessions.sagemaker_base_session_manager.common.exceptions import NoSessionException


# Runs the given statement on the passed session_manager. Added to allow for increased
# flexbility when dealing with no remote compute and using default IAM. Because
# default IAM has no session manager, there is no run_statement() instance method
# of the session manager to use. Thus this method is used to perform the handling of 
# this discrepancy 
def run_statement(session_manager, statement, mode = "exec"):
    if session_manager is None: # USE DEFAULT IAM
        if mode == "exec": # Executes code on IAM with no return value expected.
            get_ipython().ex(statement)
        
        elif mode == "eval":
            return get_ipython().ev(statement) # Evaluates expression, returning the evaluation

    else: # USE SESSION MANAGER TO RUN STATEMENT
        if not session_manager.is_session_connectable():
            raise NoSessionException("Session is not connectable")
        
        try:
            return session_manager.run_statement(statement, Language.python, mode)
        except NoSessionException as e:
            display(HTML(f"No session exists. "
                            f"Please try to rerun the cell or restart kernel. Error: {e}"))
        except Exception as e:
            display(HTML(f"Unable to run statement for connection. Error: {e}"))


# Appends a random hex code to a given prefix, used to generate a random variable name for the compute
# We perform this random generation in order to generate multiple unique variables. Without the multiple
# unique variables, the display magic functionality will become muddied when the user uses multiple
# display magics. When the user invokes the display magic, there is a an object created on the remote instance
# that holds the necessary data and methods for computation. This name is then stored in the render function
# to call its instance methods when the user interacts with the UI (for example, changing the sample size). 
# If the user were to invoke multiple display magics and override the previous object created, when the user
# interacts with an earlier created display magic's UI, the interaction will now be calling an instance method
# on a fundamentally different object with different data, causing a completely different dataframe view to 
# display to the user.
def generate_var_name_for_compute(prefix):
    import uuid
    return prefix + uuid.uuid4().hex