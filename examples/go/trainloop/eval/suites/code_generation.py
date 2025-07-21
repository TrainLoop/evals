from trainloop_cli.eval_core.helpers import tag
from ..metrics.outputs_single_codeblock import outputs_single_codeblock
from ..metrics.code_runs_correctly import code_runs_correctly

# Evaluation suite for code generation
# Tests that the output contains a single code block and that the code runs correctly
results = tag("code-generation").check(outputs_single_codeblock, code_runs_correctly)
