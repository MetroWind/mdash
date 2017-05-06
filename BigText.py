import subprocess as SubP
import InfoSource

class BigText(InfoSource.InfoSource):
    def __init__(self):
        super(BigText, self).__init__()
        self.Text = ""
        self.Font = "standard"
        self.Figlet = "figlet"

    def __call__(self):
        Text = SubP.check_output([self.Figlet, "-f", self.Font, self.Text])
        self.Result = Text
        return Text

    @classmethod
    def fromDict(cls, src_dict):
        Text = cls()
        Text.Text = src_dict["Text"]
        if "Font" in src_dict:
            Text.Font = src_dict["Font"]
        if "Figlet" in src_dict:
            Text.Figlet = src_dict["Figlet"]
        return Text
