class ToolValidator:
  # Class to add custom behavior and properties to the tool and tool parameters.

    def __init__(self):
        # Set self.params for use in other validation methods.
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        self.params[2].enabled = False
        return

    def updateParameters(self):
        folderOrIndividuals = self.params[0].valueAsText
        if folderOrIndividuals == "Folder":
            self.params[1].enabled = True
            self.params[2].enabled = False
        else:
            self.params[1].enabled = False
            self.params[2].enabled = True
        return

    def updateMessages(self):
        # Modify the messages created by internal validation for each tool
        # parameter. This method is called after internal validation.
        return

    # def isLicensed(self):
    #     # Set whether the tool is licensed to execute.
    #     return True

    # def postExecute(self):
    #     # This method takes place after outputs are processed and
    #     # added to the display.
    #     return
