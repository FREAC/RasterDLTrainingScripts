class ToolValidator:
    def __init__(self):
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        # Raster Selection
        self.params[3].enabled = False
        # Custom Convolution
        self.params[18].enabled = False
        self.params[21].enabled = False
        self.params[24].enabled = False
        self.params[18].value = "[[-1, 0, 1],\n [-2, 0, 2],\n [-1, 0, 1]]"
        self.params[21].value = "[[-1, 0, 1],\n [-2, 0, 2],\n [-1, 0, 1]]"
        self.params[24].value = "[[-1, 0, 1],\n [-2, 0, 2],\n [-1, 0, 1]]"
        self.params[43].enabled = False
        # Shaded Relief Settings
        for i in range(25,34):
            self.params[i].enabled = False
        return

    def updateParameters(self):
        # Raster Selection
        folderOrIndividuals = self.params[1].valueAsText
        if folderOrIndividuals == "Folder":
            self.params[2].enabled = True
            self.params[3].enabled = False
        else:
            self.params[2].enabled = False
            self.params[3].enabled = True
        # convs
        conv1 = self.params[17].valueAsText
        conv2 = self.params[20].valueAsText
        conv3 = self.params[23].valueAsText
        if conv1 == "Custom Convolution":
            self.params[18].enabled = True
        else:
            self.params[18].enabled = False
        if conv1 == "Shaded Relief":
            for i in range(19,25):
                self.params[i].enabled = False
            for i in range(25,34):
                self.params[i].enabled = True
        else:
            for i in range(19, 25):
                self.params[i].enabled = True
            for i in range(25,34):
                self.params[i].enabled = False
        if conv2 == "Custom Convolution" and conv1 != "Shaded Relief":
            self.params[21].enabled = True
        else:
            self.params[21].enabled = False
            
        if conv3 == "Custom Convolution" and conv1 != "Shaded Relief":
            self.params[24].enabled = True
        else:
            self.params[24].enabled = False
            
        if self.params[42].value:
            self.params[43].enabled = True
        else:
            self.params[43].enabled = False
        return

    def updateMessages(self):
        return
