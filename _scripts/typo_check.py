#!/usr/bin/env python3
"""扫描博客文章中的中英文错别字"""

import os
import re
import json

POSTS_DIR = "/Users/sunyazhou/Documents/sunyazhou/_posts"

# 常见中文错别字（错 -> 正）
# 格式: (错误词, 正确词, 说明)
CHINESE_TYPOS = [
    # 的地得混用
    ("认真的学习", "认真地学习", "地：修饰动词应用'地'"),
    ("认真的思考", "认真地思考", "地：修饰动词应用'地'"),
    ("认真的看", "认真地看", "地：修饰动词应用'地'"),
    ("认真的听", "认真地听", "地：修饰动词应用'地'"),
    ("认真的研究", "认真地研究", "地：修饰动词应用'地'"),
    ("慢慢的走", "慢慢地走", "地：修饰动词应用'地'"),
    ("慢慢的看", "慢慢地看", "地：修饰动词应用'地'"),
    ("静静的看", "静静地看", "地：修饰动词应用'地'"),
    # 在/再
    ("在次", "再次", "再：表示重复应用'再'"),
    ("在来", "再来", "再：表示重复应用'再'"),
    ("在见", "再见", "再：表示重复应用'再'"),
    ("在说", "再说", "再：表示重复应用'再'"),
    ("在试", "再试", "再：表示重复应用'再'"),
    ("在看看", "再看看", "再：表示重复应用'再'"),
    ("在想", "再想", "再：表示重复应用'再'"),
    ("在去", "再去", "再：表示重复应用'再'"),
    ("在给", "再给", "再：表示重复应用'再'"),
    # 做/作
    ("做为", "作为", "作：表示当作应用'作'"),
    ("做出贡献", "作出贡献", "作：搭配抽象名词应用'作'"),
    ("做出决定", "作出决定", "作：搭配抽象名词应用'作'"),
    ("做出努力", "作出努力", "作：搭配抽象名词应用'作'"),
    # 即/既
    ("即然", "既然", "既：表示既然应用'既'"),
    ("即使", "即使", "既/即：即使应为'即使'"),
    # 因/应
    # 这类太依赖上下文，跳过
    # 其他常见错别字
    ("帐号", "账号", "账：财务相关应用'账'"),
    ("帐户", "账户", "账：财务相关应用'账'"),
    ("帐单", "账单", "账：财务相关应用'账'"),
    ("帐目", "账目", "账：财务相关应用'账'"),
    ("帐单", "账单", "账：财务相关应用'账'"),
    ("部步", "步骤", "步：步骤应用'步'"),
    ("按装", "安装", "安：安装应用'安'"),
    ("尽然", "竟然", "竟：竟然应用'竟'"),
    ("透名", "透明", "明：透明应用'明'"),
    ("蓝量", "蓝量", ""),  # skip
    ("确却", "确切", "切：确切应用'切'"),
    ("确时", "确实", "实：确实应用'实'"),
    ("以经", "已经", "已：已经应用'已'"),
    ("以久", "已久", "已：已久应用'已'"),
    ("以然", "已然", "已：已然应用'已'"),
    ("因该", "应该", "应：应该应用'应'"),
    ("因有", "应有", "应：应有应用'应'"),
    ("因有尽有", "应有尽有", "应：应有尽有应用'应'"),
    ("历来", "历来", ""),  # 正确用法
    ("历害", "厉害", "厉：厉害应用'厉'"),
    ("利害", "利害", ""),  # 利害可以作为正确词
    ("覆复", "恢复", "恢：恢复应用'恢'"),
    ("恢复", "恢复", ""),  # 正确
    ("重导覆辙", "重蹈覆辙", "蹈：重蹈覆辙应用'蹈'"),
    ("代词", "代词", ""),  # 正确
    ("代替", "代替", ""),  # 正确
    ("签到", "签到", ""),  # 正确
    ("报道", "报道", ""),  # 正确
    ("报倒", "报到", "到：报到应用'到'"),
    ("登录到", "登录到", ""),  # 正确
    ("登陆", "登录", "录：登录应用'录'"),  # 登陆/登录有争议，但IT语境下登录更常见
    ("登入", "登录", "录：IT语境登录应用'录'"),  # 登入也是合法的，但在IT语境下登录更标准
    ("按耐不住", "按捺不住", "捺：按捺不住应用'捺'"),
    ("不修边副", "不修边幅", "幅：不修边幅应用'幅'"),
    ("走头无路", "走投无路", "投：走投无路应用'投'"),
    ("凭空", "凭空", ""),  # 正确
    ("名副其实", "名副其实", ""),  # 正确
    ("名符其实", "名副其实", "副：名副其实应用'副'"),
    ("迫不及待", "迫不及待", ""),  # 正确
    ("迫不急待", "迫不及待", "及：迫不及待应用'及'"),
    ("一愁莫展", "一筹莫展", "筹：一筹莫展应用'筹'"),
    ("一愁莫展", "一筹莫展", "筹：一筹莫展应用'筹'"),
    ("默守成规", "墨守成规", "墨：墨守成规应用'墨'"),
    ("磨肩接踵", "摩肩接踵", "摩：摩肩接踵应用'摩'"),
    ("天崖海角", "天涯海角", "涯：天涯海角应用'涯'"),
    ("纺碍", "妨碍", "妨：妨碍应用'妨'"),
    ("防碍", "妨碍", "妨：妨碍应用'妨'"),
    ("妨预", "防御", "御：防御应用'御'"),
    ("抵预", "抵御", "御：抵御应用'御'"),
    ("洋溢", "洋溢", ""),  # 正确
    ("旁证博引", "旁征博引", "征：旁征博引应用'征'"),
    ("证实", "证实", ""),  # 正确
    ("证据", "证据", ""),  # 正确
    ("明辩是非", "明辨是非", "辨：明辨是非应用'辨'"),
    ("辩论", "辩论", ""),  # 正确
    ("辨别", "辨别", ""),  # 正确
    ("分辨", "分辨", ""),  # 正确
    ("分辩", "分辨", "辨：分辨应用'辨'"),
    ("象形", "象形", ""),  # 正确
    ("形象", "形象", ""),  # 正确
    ("现象", "现象", ""),  # 正确
    ("印像", "印象", "象：印象应用'象'"),  # 注意：印象是正确的
    ("印像", "印象", "象：印象应用'象'"),
    ("好象", "好像", "像：好像应用'像'"),
    ("好象", "好像", "像：好像应用'像'"),
    ("象是", "像是", "像：像是应用'像'"),
    ("象他", "像他", "像：像他应用'像'"),
    ("象我", "像我", "像：像我应用'像'"),
    ("象你", "像你", "像：像你应用'像'"),
    ("象这样", "像这样", "像：像这样应用'像'"),
    ("象那样", "像那样", "像：像那样应用'像'"),
    ("不象", "不像", "像：不像应用'像'"),
    ("想象", "想象", ""),  # 正确，想象是对的
    ("相象", "相像", "像：相像应用'像'"),
    ("象征", "象征", ""),  # 正确
    ("既然如此", "既然如此", ""),  # 正确
    ("必需品", "必需品", ""),  # 正确
    ("必须", "必须", ""),  # 正确
    ("必需", "必需", ""),  # 正确，必需也是对的
    ("不须", "不需", "需：不需应用'需'"),
    ("无须", "无须", ""),  # 正确
    ("必须品", "必需品", "需：必需品应用'需'"),
    ("必备品", "必备品", ""),  # 正确
    ("泛滥", "泛滥", ""),  # 正确
    ("兰色", "蓝色", "蓝：蓝色应用'蓝'"),
    ("篮球", "篮球", ""),  # 正确
    ("兰球", "篮球", "篮：篮球应用'篮'"),
    ("彩排", "彩排", ""),  # 正确
    ("彩排", "彩排", ""),  # 正确
    ("圆心", "圆心", ""),  # 正确
    ("园心", "圆心", "圆：圆心应用'圆'"),
    ("园林", "园林", ""),  # 正确
    ("满园", "满园", ""),  # 正确
    ("园圈", "圆圈", "圆：圆圈应用'圆'"),
    ("旋转", "旋转", ""),  # 正确
    ("选择", "选择", ""),  # 正确
    ("选项", "选项", ""),  # 正确
    ("轮回", "轮回", ""),  # 正确
    ("轮回", "轮回", ""),  # 正确
    ("部署", "部署", ""),  # 正确
    ("布署", "部署", "部：部署应用'部'"),
    ("布置", "布置", ""),  # 正确
    ("部骤", "步骤", "步：步骤应用'步'"),
    ("既使", "即使", "即：即使应用'即'"),
    ("即然", "既然", "既：既然应用'既'"),
    ("辗转", "辗转", ""),  # 正确
    ("展开", "展开", ""),  # 正确
    ("发展", "发展", ""),  # 正确
    ("展示", "展示", ""),  # 正确
    ("斩时", "暂时", "暂：暂时应用'暂'"),
    ("暂进", "暂进", ""),  # skip
    ("暂时", "暂时", ""),  # 正确
    ("暂时", "暂时", ""),  # 正确
    ("帐蓬", "帐篷", "篷：帐篷应用'篷'"),
    ("帐篷", "帐篷", ""),  # 正确
    ("账目", "账目", ""),  # 正确
    ("帐目", "账目", "账：账目应用'账'"),
    ("帐篷", "帐篷", ""),  # 正确
    ("颓费", "颓废", "废：颓废应用'废'"),
    ("消费", "消费", ""),  # 正确
    ("废用", "废用", ""),  # 正确
    ("费弃", "废弃", "弃：废弃应用'弃'"),
    ("废品", "废品", ""),  # 正确
    ("废话", "废话", ""),  # 正确
    ("费话", "废话", "废：废话应用'废'"),
    ("费除", "废除", "废：废除应用'废'"),
    ("费止", "废止", "废：废止应用'废'"),
    ("繁植", "繁殖", "殖：繁殖应用'殖'"),
    ("繁殖", "繁殖", ""),  # 正确
    ("种植", "种植", ""),  # 正确
    ("培值", "培育", "育：培育应用'育'"),
    ("培育", "培育", ""),  # 正确
    ("饲养", "饲养", ""),  # 正确
    ("伺养", "饲养", "饲：饲养应用'饲'"),
    ("伺服器", "服务器", "服：服务器应用'服'"),
    ("服务器", "服务器", ""),  # 正确
    ("服务器", "服务器", ""),  # 正确
    ("渲染", "渲染", ""),  # 正确
    ("宣染", "渲染", "渲：渲染应用'渲'"),
    ("渲泄", "宣泄", "宣：宣泄应用'宣'"),
    ("宣泄", "宣泄", ""),  # 正确
    ("泄漏", "泄漏", ""),  # 正确
    ("泄露", "泄露", ""),  # 正确
    ("泄露", "泄露", ""),  # 正确
    ("泄密", "泄密", ""),  # 正确
    ("泻密", "泄密", "泄：泄密应用'泄'"),
    ("泄漏", "泄漏", ""),  # 正确
    ("泄气", "泄气", ""),  # 正确
    ("泻气", "泄气", "泄：泄气应用'泄'"),
    ("泻药", "泻药", ""),  # 正确
    ("泄药", "泻药", "泻：泻药应用'泻'"),
    ("急剧", "急剧", ""),  # 正确
    ("极剧", "急剧", "急：急剧应用'急'"),
    ("急剧", "急剧", ""),  # 正确
    ("急剧", "急剧", ""),  # 正确
    ("争辩", "争辩", ""),  # 正确
    ("辨证", "辨证", ""),  # 正确
    ("辩证", "辩证", ""),  # 正确
    ("辩论", "辩论", ""),  # 正确
    ("分辨", "分辨", ""),  # 正确
    ("分辩", "分辨", "辨：分辨应用'辨'"),
    ("辨析", "辨析", ""),  # 正确
    ("辩析", "辨析", "辨：辨析应用'辨'"),
    ("辨认", "辨认", ""),  # 正确
    ("辩认", "辨认", "辨：辨认应用'辨'"),
    ("辨识", "辨识", ""),  # 正确
    ("辩识", "辨识", "辨：辨识应用'辨'"),
    ("鉴别", "鉴别", ""),  # 正确
    ("签别", "鉴别", "鉴：鉴别应用'鉴'"),
    ("鉴赏", "鉴赏", ""),  # 正确
    ("签赏", "鉴赏", "鉴：鉴赏应用'鉴'"),
    ("鉴定", "鉴定", ""),  # 正确
    ("签定", "鉴定", "鉴：鉴定应用'鉴'"),
    ("借鉴", "借鉴", ""),  # 正确
    ("借签", "借鉴", "鉴：借鉴应用'鉴'"),
    ("摹拟", "模拟", "模：模拟应用'模'"),
    ("模拟", "模拟", ""),  # 正确
    ("模型", "模型", ""),  # 正确
    ("模形", "模型", "型：模型应用'型'"),
    ("模板", "模板", ""),  # 正确
    ("模版", "模板", "板：模板应用'板'"),  # 版/板有争议，但模板是标准用法
    ("版图", "版图", ""),  # 正确
    ("板图", "版图", "版：版图应用'版'"),
    ("版本", "版本", ""),  # 正确
    ("板本", "版本", "版：版本应用'版'"),
    ("出版", "出版", ""),  # 正确
    ("出板", "出版", "版：出版应用'版'"),
    ("排版", "排版", ""),  # 正确
    ("排板", "排版", "版：排版应用'版'"),
    ("版面", "版面", ""),  # 正确
    ("板面", "版面", "版：版面应用'版'"),
    ("安装", "安装", ""),  # 正确
    ("按装", "安装", "安：安装应用'安'"),
    ("安全", "安全", ""),  # 正确
    ("安装包", "安装包", ""),  # 正确
    ("按装包", "安装包", "安：安装包应用'安'"),
    ("安装程序", "安装程序", ""),  # 正确
    ("按装程序", "安装程序", "安：安装程序应用'安'"),
    ("安装路径", "安装路径", ""),  # 正确
    ("按装路径", "安装路径", "安：安装路径应用'安'"),
    ("安装目录", "安装目录", ""),  # 正确
    ("按装目录", "安装目录", "安：安装目录应用'安'"),
    # 英文常见拼写错误（技术语境）
]

# 英文常见拼写错误（错误 -> 正确）
ENGLISH_TYPOS = {
    "recieve": "receive",
    "recieved": "received",
    "recieving": "receiving",
    "seperate": "separate",
    "seperated": "separated",
    "seperately": "separately",
    "seperation": "separation",
    "definately": "definitely",
    "definatly": "definitely",
    "definitly": "definitely",
    "occured": "occurred",
    "occuring": "occurring",
    "occurence": "occurrence",
    "accomodate": "accommodate",
    "accomodation": "accommodation",
    "neccessary": "necessary",
    "necesary": "necessary",
    "neccessary": "necessary",
    "tommorow": "tomorrow",
    "tomorow": "tomorrow",
    "tommorrow": "tomorrow",
    "untill": "until",
    "wich": "which",
    "teh": "the",
    "adn": "and",
    "nad": "and",
    "taht": "that",
    "thta": "that",
    "htis": "this",
    "fro": "for",
    "ofthe": "of the",
    "andthe": "and the",
    "tobe": "to be",
    "thier": "their",
    "tihs": "this",
    "pleaes": "please",
    "becuase": "because",
    "becasue": "because",
    "alot": "a lot",
    "aswell": "as well",
    "infomation": "information",
    "infromation": "information",
    "informaiton": "information",
    "enviroment": "environment",
    "enviornment": "environment",
    "exsist": "exist",
    "existance": "existence",
    "existant": "existent",
    "charactor": "character",
    "charactors": "characters",
    "charachter": "character",
    "calender": "calendar",
    "calender": "calendar",
    "cemetary": "cemetery",
    "comitted": "committed",
    "commited": "committed",
    "commitee": "committee",
    "comittee": "committee",
    "concious": "conscious",
    "deduceable": "deducible",
    "defendent": "defendant",
    "dependant": "dependent",
    "descript": "description",  # context dependent
    "developement": "development",
    "dimentions": "dimensions",
    "dissapoint": "disappoint",
    "dissappear": "disappear",
    "drummer": "drummer",  # skip
    "embarass": "embarrass",
    "embaress": "embarrass",
    "enviroment": "environment",
    "existance": "existence",
    "firey": "fiery",
    "fluorescent": "fluorescent",  # correct
    "foriegn": "foreign",
    "goverment": "government",
    "gaurd": "guard",
    "harassement": "harassment",
    "harrassment": "harassment",
    "happend": "happened",
    "heirarchy": "hierarchy",
    "hierachy": "hierarchy",
    "hygeine": "hygiene",
    "idiosyncracy": "idiosyncrasy",
    "imitible": "inimitable",
    "immminent": "imminent",
    "independant": "independent",
    "indispensible": "indispensable",
    "innappropriate": "inappropriate",
    "intelectual": "intellectual",
    "intelegent": "intelligent",
    "intelligent": "intelligent",  # correct
    "jewelery": "jewelry",
    "jewellery": "jewelry",
    "judgement": "judgment",  # both correct, skip
    "knowlege": "knowledge",
    "knowlegde": "knowledge",
    "lenght": "length",
    "lenght": "length",
    "liason": "liaison",
    "liaision": "liaison",
    "libary": "library",
    "liberry": "library",
    "lisence": "license",
    "liscense": "license",
    "maintainance": "maintenance",
    "maintainence": "maintenance",
    "managable": "manageable",
    "maneouvre": "maneuver",
    "maneuvar": "maneuver",
    "marshmellow": "marshmallow",
    "medecine": "medicine",
    "millenium": "millennium",
    "millepede": "millipede",
    "miniscule": "minuscule",
    "mischeivous": "mischievous",
    "mischevious": "mischievous",
    "mischievious": "mischievous",
    "misquito": "mosquito",
    "mointain": "mountain",
    "mucous": "mucous",  # correct, skip
    "necesary": "necessary",
    "neccessary": "necessary",
    "nickle": "nickel",
    "noticable": "noticeable",
    "noticably": "noticeably",
    "nusance": "nuisance",
    "nuiscance": "nuisance",
    "occassion": "occasion",
    "occassionally": "occasionally",
    "occassional": "occasional",
    "occured": "occurred",
    "occuring": "occurring",
    "occurence": "occurrence",
    "pavillion": "pavilion",
    "percieve": "perceive",
    "percived": "perceived",
    "persistant": "persistent",
    "personell": "personnel",
    "persue": "pursue",
    "pidgeon": "pigeon",
    "playright": "playwright",
    "posession": "possession",
    "posession": "possession",
    "possesion": "possession",
    "posession": "possession",
    "posessions": "possessions",
    "posess": "possess",
    "posesses": "possesses",
    "posession": "possession",
    "prefered": "preferred",
    "prefering": "preferring",
    "priviledge": "privilege",
    "priviledges": "privileges",
    "probaly": "probably",
    "proffesional": "professional",
    "professonial": "professional",
    "promiss": "promise",
    "pronounciation": "pronunciation",
    "publically": "publicly",
    "quitar": "guitar",  # skip, too aggressive
    "readible": "readable",
    "realitive": "relative",
    "reciept": "receipt",
    "recomend": "recommend",
    "recomendation": "recommendation",
    "reccommend": "recommend",
    "reccommendation": "recommendation",
    "refered": "referred",
    "refering": "referring",
    "relevent": "relevant",
    "religous": "religious",
    "religiuos": "religious",
    "repitition": "repetition",
    "resear": "research",  # skip
    "resistence": "resistance",
    "rythm": "rhythm",
    "rythym": "rhythm",
    "sacreligious": "sacrilegious",
    "seperate": "separate",
    "seperated": "separated",
    "seperately": "separately",
    "seperation": "separation",
    "sherif": "sheriff",
    "similiar": "similar",
    "sincerly": "sincerely",
    "speach": "speech",
    "stoping": "stopping",
    "strange": "strange",  # correct, skip
    "strangth": "strength",
    "succesful": "successful",
    "succesfully": "successfully",
    "successfull": "successful",
    "successfuly": "successfully",
    "supercede": "supersede",
    "supress": "suppress",
    "suprise": "surprise",
    "surprize": "surprise",
    "tatoo": "tattoo",
    "temparature": "temperature",
    "temprature": "temperature",
    "tendancy": "tendency",
    "threshhold": "threshold",
    "threshhold": "threshold",
    "tommorow": "tomorrow",
    "tomorow": "tomorrow",
    "tongiht": "tonight",
    "truely": "truly",
    "uncomforable": "uncomfortable",
    "unforseen": "unforeseen",
    "untill": "until",
    "useable": "usable",  # both correct, skip
    "vaccum": "vacuum",
    "vaccum": "vacuum",
    "wether": "whether",
    "withold": "withhold",
    "wich": "which",
    "writting": "writing",
    "writen": "written",
    "yatch": "yacht",
    "yield": "yield",  # correct, skip
    # 技术相关
    "alloc": "alloc",  # correct (ObjC)
    "dealloc": "dealloc",  # correct
    "implemtation": "implementation",
    "implemenation": "implementation",
    "implementaion": "implementation",
    "implemenatation": "implementation",
    "fucntion": "function",
    "funtion": "function",
    "funciton": "function",
    "funtional": "functional",
    "fucntional": "functional",
    "paramter": "parameter",
    "paramater": "parameter",
    "paramaters": "parameters",
    "paramters": "parameters",
    "paramter": "parameter",
    "parmaeter": "parameter",
    "parmaeters": "parameters",
    "arguement": "argument",
    "arguements": "arguments",
    "writen": "written",
    "varible": "variable",
    "variables": "variables",  # correct
    "varibles": "variables",
    "varialbe": "variable",
    "defualt": "default",
    "defualtValue": "defaultValue",
    "defualts": "defaults",
    "reciever": "receiver",
    "transmition": "transmission",
    "transmitions": "transmissions",
    "anonomous": "anonymous",
    "annonymous": "anonymous",
    "anonynous": "anonymous",
    "automatcially": "automatically",
    "automaticaly": "automatically",
    "automaticlly": "automatically",
    "begining": "beginning",
    "begining": "beginning",
    "boundry": "boundary",
    "boundries": "boundaries",
    "boundries": "boundaries",
    "cancellation": "cancellation",  # correct
    "cancelation": "cancellation",
    "compilier": "compiler",
    "complier": "compiler",
    "confgiuration": "configuration",
    "configration": "configuration",
    "configuraiton": "configuration",
    "conifguration": "configuration",
    "destory": "destroy",
    "destoryed": "destroyed",
    "destorying": "destroying",
    "distrubution": "distribution",
    "distrubute": "distribute",
    "distrubuted": "distributed",
    "enviornment": "environment",
    "excecute": "execute",
    "excecuted": "executed",
    "excecution": "execution",
    "executation": "execution",
    "familar": "familiar",
    "familarize": "familiarize",
    "familarity": "familiarity",
    "inital": "initial",
    "initalization": "initialization",
    "initailize": "initialize",
    "initailized": "initialized",
    "intialize": "initialize",
    "intialized": "initialized",
    "intialization": "initialization",
    "lable": "label",
    "labled": "labeled",
    "lables": "labels",
    "lauch": "launch",
    "lauched": "launched",
    "lauching": "launching",
    "managment": "management",
    "managment": "management",
    "performace": "performance",
    "performace": "performance",
    "performanc": "performance",
    "performace": "performance",
    "performancs": "performances",
    "prefernce": "preference",
    "prefernces": "preferences",
    "recorgnize": "recognize",
    "recorgnized": "recognized",
    "recorgnise": "recognise",
    "recoginze": "recognize",
    "recongnize": "recognize",
    "recongnise": "recognise",
    "refernce": "reference",
    "refernces": "references",
    "registeration": "registration",
    "registery": "registry",
    "registery": "registry",
    "relevent": "relevant",
    "relevent": "relevant",
    "repsonse": "response",
    "repsonses": "responses",
    "responce": "response",
    "responces": "responses",
    "resgister": "register",
    "resgistration": "registration",
    "succes": "success",
    "sucess": "success",
    "sucessful": "successful",
    "sucessfully": "successfully",
    "sucessfull": "successful",
    "successfull": "successful",
    "synchornize": "synchronize",
    "synchornized": "synchronized",
    "synchornization": "synchronization",
    "synchronzied": "synchronized",
    "synchronsized": "synchronized",
    "thred": "thread",  # could be valid
    "threds": "threads",
    "threadding": "threading",
    "uninitalized": "uninitialized",
    "unintialized": "uninitialized",
    "uptate": "update",
    "uptated": "updated",
    "uptates": "updates",
    "uptdating": "updating",
    "wraper": "wrapper",
    "wrapers": "wrappers",
    "wrappers": "wrappers",  # correct
    "wrraper": "wrapper",
    "compatibilty": "compatibility",
    "compatibily": "compatibility",
    "compatiable": "compatible",
    "compatibale": "compatible",
    "incompatable": "incompatible",
    "incompatibile": "incompatible",
    "unsuported": "unsupported",
    "unsuport": "unsupport",
    "unsupoorted": "unsupported",
    "architechture": "architecture",
    "architecure": "architecture",
    "architechure": "architecture",
    "architecutre": "architecture",
    "archtecture": "architecture",
    "dependancy": "dependency",
    "dependancies": "dependencies",
    "depencency": "dependency",
    "depencencies": "dependencies",
    "interupt": "interrupt",
    "interupted": "interrupted",
    "interuption": "interruption",
    "interupts": "interrupts",
    "interupting": "interrupting",
    "interuption": "interruption",
    "overide": "override",
    "overides": "overrides",
    "overiding": "overriding",
    "overide": "override",
    "overriden": "overridden",
    "overwriten": "overwritten",
    "overwritting": "overwriting",
    "overwrote": "overwrote",  # correct
    "siginificant": "significant",
    "signifiant": "significant",
    "signifcant": "significant",
    "signifcantly": "significantly",
    "theshold": "threshold",
    "threshhold": "threshold",
    "threshod": "threshold",
    "threshhold": "threshold",
    "utilties": "utilities",
    "utilty": "utility",
    "utillity": "utility",
    "utillities": "utilities",
    "varient": "variant",
    "varients": "variants",
    "virsion": "version",  # skip, too aggressive
    "verison": "version",
    "verison": "version",
    "verson": "version",
    "verisons": "versions",
    "versoin": "version",
    "versoins": "versions",
    "verisons": "versions",
    "writen": "written",
    "writting": "writing",
    "writting": "writing",
}


def find_chinese_typos(content):
    """在内容中查找中文错别字"""
    results = []
    for wrong, correct, note in CHINESE_TYPOS:
        if not note:  # 跳过空说明（正确的词）
            continue
        idx = 0
        while True:
            pos = content.find(wrong, idx)
            if pos == -1:
                break
            # 获取行号
            line_no = content[:pos].count('\n') + 1
            # 获取上下文
            line_start = content.rfind('\n', 0, pos) + 1
            line_end = content.find('\n', pos)
            if line_end == -1:
                line_end = len(content)
            context = content[line_start:line_end].strip()
            results.append({
                'line': line_no,
                'wrong': wrong,
                'correct': correct,
                'note': note,
                'context': context,
            })
            idx = pos + len(wrong)
    return results


def find_english_typos(content):
    """在内容中查找英文拼写错误（单词级别）"""
    results = []
    # 使用正则匹配单词
    for line_no, line in enumerate(content.split('\n'), 1):
        # 跳过代码块、URL、HTML标签等
        if line.strip().startswith('```') or line.strip().startswith('|'):
            continue
        if 'http' in line or 'https' in line:
            continue
        
        # 匹配单词
        words = re.finditer(r'\b([a-zA-Z]+)\b', line)
        for m in words:
            word = m.group(1).lower()
            if word in ENGLISH_TYPOS:
                correct = ENGLISH_TYPOS[word]
                if word == correct:
                    continue
                # 获取上下文
                context = line.strip()
                # 获取原始大小写
                orig_word = m.group(1)
                results.append({
                    'line': line_no,
                    'wrong': orig_word,
                    'correct': correct,
                    'note': f'英文拼写错误: {word} -> {correct}',
                    'context': context,
                })
    return results


def scan_file(filepath):
    """扫描单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    
    chinese_results = find_chinese_typos(content)
    english_results = find_english_typos(content)
    
    all_results = chinese_results + english_results
    
    return filename, all_results


def main():
    all_findings = {}
    total_typos = 0
    
    files = sorted([f for f in os.listdir(POSTS_DIR) if f.endswith('.md')])
    
    for filename in files:
        filepath = os.path.join(POSTS_DIR, filename)
        name, results = scan_file(filepath)
        if results:
            all_findings[name] = results
            total_typos += len(results)
    
    print(f"\n{'='*60}")
    print(f"扫描完成！共扫描 {len(files)} 篇文章")
    print(f"发现 {len(all_findings)} 篇文章有错别字")
    print(f"共发现 {total_typos} 处疑似错别字")
    print(f"{'='*60}\n")
    
    for filename, results in sorted(all_findings.items()):
        print(f"\n📄 {filename}")
        print(f"   {len(results)} 处错别字:")
        for r in results:
            print(f"   行 {r['line']}: 「{r['wrong']}」→「{r['correct']}」 - {r['note']}")
            print(f"      上下文: {r['context'][:80]}")
    
    # 输出JSON
    output = {
        'total_files': len(files),
        'files_with_typos': len(all_findings),
        'total_typos': total_typos,
        'findings': all_findings,
    }
    
    output_path = "/Users/sunyazhou/Documents/sunyazhou/_scripts/typo_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n详细结果已保存到: {output_path}")
    
    return output


if __name__ == '__main__':
    main()
