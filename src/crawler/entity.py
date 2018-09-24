class personalInfo:
    def __init__(self):
        self.uid = None
        self.location = None#所在地
        self.userName = None#用户名
        self.gender = None
        self.userNumCame = None
        self.onlineTime = None#在线时间
        self.registerTime = None#注册时间。时间戳
        self.lastLoginTime = None#上次登录时间
        self.communityRPScore = None#声望值，可能为负值
        self.HPLevel = None#论坛等级
        self.theOrg = None#所属社团,可能有多个
        self.HPCalorie = None#银行现金
        self.favoriteSports = None#喜欢的运动
        self.favoriteLeagues = None#喜欢的联赛
        self.favoriteTeams = None#喜欢的队伍
        self.homeTeams = None#主队，可能有多个。以联赛为key,队名为value
        self.selfDesc = None#自我介绍
        self.dutiesHP = None#在虎扑的职务，可能有多个
        self.recommend = None#推荐的帖子
        self.follow = None#关注的人，uid列表
        self.fans = None#关注他的人，uid列表
        self.crawlTime = None

    #把信息组织成json并返回
    def trans2Json(self):
        res = {}
        for key in self.__dict__.keys():
            if self.__dict__[key] != None and self.__dict__[key] != [] and \
                self.__dict__[key] != {}:
                res[key] = self.__dict__[key]
        res['_id'] = self.uid
        return res
