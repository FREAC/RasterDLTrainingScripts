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
        # export chips
        export_chips = self.params[42].value
        if not export_chips:
            self.params[5].enabled = False
            self.params[6].enabled = False
            self.params[7].enabled = False
            self.params[8].enabled = False
            self.params[9].enabled = False
            self.params[10].enabled = False
            self.params[11].enabled = False
            self.params[12].enabled = False
            self.params[13].enabled = False
            self.params[14].enabled = False
            self.params[15].enabled = False
            self.params[34].enabled = False
            self.params[35].enabled = False
            self.params[36].enabled = False
            self.params[37].enabled = False
            self.params[38].enabled = False
            self.params[39].enabled = False
            self.params[40].enabled = False
            self.params[41].enabled = False
        else:
            self.params[5].enabled = True
            self.params[6].enabled = True
            self.params[7].enabled = True
            self.params[8].enabled = True
            self.params[9].enabled = True
            self.params[10].enabled = True
            self.params[11].enabled = True
            self.params[12].enabled = True
            self.params[13].enabled = True
            self.params[14].enabled = True
            self.params[15].enabled = True
            self.params[34].enabled = True
            self.params[35].enabled = True
            self.params[36].enabled = True
            self.params[37].enabled = True
            self.params[38].enabled = True
            self.params[39].enabled = True
            self.params[40].enabled = True
            self.params[41].enabled = True
        
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
            
        return

    def updateMessages(self):
        return
