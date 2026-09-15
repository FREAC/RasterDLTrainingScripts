class ToolValidator:
    def __init__(self):
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        self.params[2].enabled = False
        
        self.params[9].enabled = False
        self.params[10].enabled = False
        self.params[11].enabled = False
        
        self.params[13].enabled = False
        return

    def updateParameters(self):
        
        if self.params[0].value == "Individual Chips":
            self.params[1].enabled = False
            self.params[2].enabled = True
        else:
            self.params[1].enabled = True
            self.params[2].enabled = False
        
        if self.params[12].value:
           self.params[13].enabled = True
        else:
           self.params[13].enabled = False
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
