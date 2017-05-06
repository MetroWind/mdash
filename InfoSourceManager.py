import WebSpider
import ServerPinger
import BigText

InfoSourceTypes = dict()

def registerInfoSource(src_type):
    global InfoSourceTypes
    InfoSourceTypes[src_type.__name__] = src_type

registerInfoSource(WebSpider.ResponseSpider)
registerInfoSource(WebSpider.JsonSpider)
registerInfoSource(WebSpider.AppStorePrice)
registerInfoSource(ServerPinger.SocketPinger)
registerInfoSource(BigText.BigText)

def buildInfoSource(info_src_dict):
    Type = tuple(info_src_dict.keys())[0]
    return InfoSourceTypes[Type].fromDict(info_src_dict[Type])
