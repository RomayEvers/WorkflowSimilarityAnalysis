# WorkflowSimilarityAnalysis
 Analyzing rfd workflows in correlation with question strings

How to run:
1. Copy all workflow ttl files to "workflowData" folder. The folder should contain only ttl files with valid RDF syntax.
2. Run python script "main.py" in PyCharm environment to serialize all RDF workflows into a string format. All output from the script will be stored in folder "pythonOutputData".
3. Open R script "main.R" in RStudio. This script does all the statistical analyses.
4. In the R script, set the global variable "root" to the absolute path of the root folder (folder where the R script is located).
5. Run the R script.

NOTE: The R script should be rerun if the python script was again executed afterward. It should be done even if there were no changes to the python script or ttl files.