var cityArray = [
    {name:"北京",items:[{id:11,name:"北京"}]},//[{id:110101,name:"东城区"},{id:110102,name:"西城区"},{id:110103,name:"崇文区"},{id:110104,name:"宣武区"},{id:110105,name:"朝阳区"},{id:110106,name:"丰台区"},{id:110107,name:"石景山区"},{id:110108,name:"海淀区"},{id:110109,name:"门头沟区"},{id:110111,name:"房山区"},{id:110112,name:"通州区"},{id:110113,name:"顺义区"},{id:110114,name:"昌平区"},{id:110115,name:"大兴区"},{id:110116,name:"怀柔区"},{id:110117,name:"平谷区"},{id:110228,name:"密云县"},{id:110229,name:"延庆县"}]},
   {name:"上海",items:[{id:31,name:"上海"}]},//[{id:310101,name:"黄浦区"},{id:310103,name:"卢湾区"},{id:310104,name:"徐汇区"},{id:310105,name:"长宁区"},{id:310106,name:"静安区"},{id:310107,name:"普陀区"},{id:310108,name:"闸北区"},{id:310109,name:"虹口区"},{id:310110,name:"杨浦区"},{id:310112,name:"闵行区"},{id:310113,name:"宝山区"},{id:310114,name:"嘉定区"},{id:310115,name:"浦东新区"},{id:310116,name:"金山区"},{id:310117,name:"松江区"},{id:310118,name:"青浦区"},{id:310119,name:"南汇区"},{id:310120,name:"奉贤区"},{id:310230,name:"崇明县"}]},
   {name:"天津",items:[{id:12,name:"天津"}]},//[{id:120101,name:"和平区"},{id:120102,name:"河东区"},{id:120103,name:"河西区"},{id:120104,name:"南开区"},{id:120105,name:"河北区"},{id:120106,name:"红桥区"},{id:120107,name:"塘沽区"},{id:120108,name:"汉沽区"},{id:120109,name:"大港区"},{id:120110,name:"东丽区"},{id:120111,name:"西青区"},{id:120112,name:"津南区"},{id:120113,name:"北辰区"},{id:120114,name:"武清区"},{id:120115,name:"宝坻区"},{id:120221,name:"宁河县"},{id:120223,name:"静海县"},{id:120225,name:"蓟县"}]},
   {name:"重庆",items:[{id:50,name:"重庆"}]},//[{id:500101,name:"万州区"},{id:500102,name:"涪陵区"},{id:500103,name:"渝中区"},{id:500104,name:"大渡口区"},{id:500105,name:"江北区"},{id:500106,name:"沙坪坝区"},{id:500107,name:"九龙坡区"},{id:500108,name:"南岸区"},{id:500109,name:"北碚区"},{id:500110,name:"万盛区"},{id:500111,name:"双桥区"},{id:500112,name:"渝北区"},{id:500113,name:"巴南区"},{id:500114,name:"黔江区"},{id:500115,name:"长寿区"},{id:500116,name:"江津区"},{id:500117,name:"合川区"},{id:500118,name:"永川区"},{id:500119,name:"南川区"},{id:500222,name:"綦江县"},{id:500223,name:"潼南县"},{id:500224,name:"铜梁县"},{id:500225,name:"大足县"},{id:500226,name:"荣昌县"},{id:500227,name:"璧山县"},{id:500228,name:"梁平县"},{id:500229,name:"城口县"},{id:500230,name:"丰都县"},{id:500231,name:"垫江县"},{id:500232,name:"武隆县"},{id:500233,name:"忠县"},{id:500234,name:"开县"},{id:500235,name:"云阳县"},{id:500236,name:"奉节县"},{id:500237,name:"巫山县"},{id:500238,name:"巫溪县"},{id:500240,name:"石柱土家族自治县"},{id:500241,name:"秀山土家族苗族自治县"},{id:500242,name:"酉阳土家族苗族自治县"},{id:500243,name:"彭水苗族土家族自治县"}]},
   {name:"黑龙江",items:[{id:2301,name:"哈尔滨"},{id:2302,name:"齐齐哈尔"},{id:2303,name:"鸡西"},{id:2304,name:"鹤岗"},{id:2305,name:"双鸭山"},{id:2306,name:"大庆"},{id:2307,name:"伊春"},{id:2308,name:"佳木斯"},{id:2309,name:"七台河"},{id:2310,name:"牡丹江"},{id:2311,name:"黑河"},{id:2312,name:"绥化"},{id:2327,name:"大兴安岭地区"}]},
   {name:"吉林",items:[{id:2201,name:"长春"},{id:2202,name:"吉林"},{id:2203,name:"四平"},{id:2204,name:"辽源"},{id:2205,name:"通化"},{id:2206,name:"白山"},{id:2207,name:"松原"},{id:2208,name:"白城"},{id:2224,name:"延边朝鲜族自治州"}]},
   {name:"沈阳",items:[{id:2101,name:"沈阳"},{id:2102,name:"大连"},{id:2103,name:"鞍山"},{id:2104,name:"抚顺"},{id:2105,name:"本溪"},{id:2106,name:"丹东"},{id:2107,name:"锦州"},{id:2108,name:"营口"},{id:2109,name:"阜新"},{id:2110,name:"辽阳"},{id:2111,name:"盘锦"},{id:2112,name:"铁岭"},{id:2113,name:"朝阳"},{id:2114,name:"葫芦岛"}]},
   {name:"山东",items:[{id:3701,name:"济南"},{id:3702,name:"青岛"},{id:3703,name:"淄博"},{id:3704,name:"枣庄"},{id:3705,name:"东营"},{id:3706,name:"烟台"},{id:3707,name:"潍坊"},{id:3708,name:"济宁"},{id:3709,name:"泰安"},{id:3710,name:"威海"},{id:3711,name:"日照"},{id:3712,name:"莱芜"},{id:3713,name:"临沂"},{id:3714,name:"德州"},{id:3715,name:"聊城"},{id:3716,name:"滨州"},{id:3717,name:"菏泽"}]},
   {name:"山西",items:[{id:1401,name:"太原"},{id:1402,name:"大同"},{id:1403,name:"阳泉"},{id:1404,name:"长治"},{id:1405,name:"晋城"},{id:1406,name:"朔州"},{id:1407,name:"晋中"},{id:1408,name:"运城"},{id:1409,name:"忻州"},{id:1410,name:"临汾"},{id:1411,name:"吕梁"}]},
   {name:"西安",items:[{id:6101,name:"西安"},{id:6102,name:"铜川"},{id:6103,name:"宝鸡"},{id:6104,name:"咸阳"},{id:6105,name:"渭南"},{id:6106,name:"延安"},{id:6107,name:"汉中"},{id:6108,name:"榆林"},{id:6109,name:"安康"},{id:6110,name:"商洛"}]},
   {name:"河北",items:[{id:1301,name:"石家庄"},{id:1302,name:"唐山"},{id:1303,name:"秦皇岛"},{id:1304,name:"邯郸"},{id:1305,name:"邢台"},{id:1306,name:"保定"},{id:1307,name:"张家口"},{id:1308,name:"承德"},{id:1309,name:"沧州"},{id:1310,name:"廊坊"},{id:1311,name:"衡水"}]},
   {name:"河南",items:[{id:4101,name:"郑州"},{id:4102,name:"开封"},{id:4103,name:"洛阳"},{id:4104,name:"平顶山"},{id:4105,name:"安阳"},{id:4106,name:"鹤壁"},{id:4107,name:"新乡"},{id:4108,name:"焦作"},{id:4109,name:"濮阳"},{id:4110,name:"许昌"},{id:4111,name:"漯河"},{id:4112,name:"三门峡"},{id:4113,name:"南阳"},{id:4114,name:"商丘"},{id:4115,name:"信阳"},{id:4116,name:"周口"},{id:4117,name:"驻马店"},{id:4118,name:"济源"}]},
   {name:"湖北",items:[{id:4201,name:"武汉"},{id:4202,name:"黄石"},{id:4203,name:"十堰"},{id:4205,name:"宜昌"},{id:4206,name:"襄樊"},{id:4207,name:"鄂州"},{id:4208,name:"荆门"},{id:4209,name:"孝感"},{id:4210,name:"荆州"},{id:4211,name:"黄冈"},{id:4212,name:"咸宁"},{id:4213,name:"随州"},{id:4228,name:"恩施土家族苗族自治州"},{id:429004,name:"仙桃"},{id:429005,name:"潜江"},{id:429006,name:"天门"},{id:429021,name:"神农架林区"}]},
   {name:"湖南",items:[{id:4301,name:"长沙"},{id:4302,name:"株洲"},{id:4303,name:"湘潭"},{id:4304,name:"衡阳"},{id:4305,name:"邵阳"},{id:4306,name:"岳阳"},{id:4307,name:"常德"},{id:4308,name:"张家界"},{id:4309,name:"益阳"},{id:4310,name:"郴州"},{id:4311,name:"永州"},{id:4312,name:"怀化"},{id:4313,name:"娄底"},{id:4331,name:"湘西土家族苗族自治州"}]},
   {name:"海口",items:[{id:4601,name:"海口"},{id:4602,name:"三亚"},{id:469001,name:"五指山"},{id:469002,name:"琼海"},{id:469003,name:"儋州"},{id:469005,name:"文昌"},{id:469006,name:"万宁"},{id:469007,name:"东方"},{id:469025,name:"定安县"},{id:469026,name:"屯昌县"},{id:469027,name:"澄迈县"},{id:469028,name:"临高县"},{id:469030,name:"白沙黎族自治县"},{id:469031,name:"昌江黎族自治县"},{id:469033,name:"乐东黎族自治县"},{id:469034,name:"陵水黎族自治县"},{id:469035,name:"保亭黎族苗族自治县"},{id:469036,name:"琼中黎族苗族自治县"}]},
   {name:"江苏",items:[{id:3201,name:"南京"},{id:3202,name:"无锡"},{id:3203,name:"徐州"},{id:3204,name:"常州"},{id:3205,name:"苏州"},{id:3206,name:"南通"},{id:3207,name:"连云港"},{id:3208,name:"淮安"},{id:3209,name:"盐城"},{id:3210,name:"扬州"},{id:3211,name:"镇江"},{id:3212,name:"泰州"},{id:3213,name:"宿迁"}]},
   {name:"江西",items:[{id:3601,name:"南昌"},{id:3602,name:"景德镇"},{id:3603,name:"萍乡"},{id:3604,name:"九江"},{id:3605,name:"新余"},{id:3606,name:"鹰潭"},{id:3607,name:"赣州"},{id:3608,name:"吉安"},{id:3609,name:"宜春"},{id:3610,name:"抚州"},{id:3611,name:"上饶"}]},
   {name:"广东",items:[{id:4401,name:"广州"},{id:4402,name:"韶关"},{id:4403,name:"深圳"},{id:4404,name:"珠海"},{id:4405,name:"汕头"},{id:4406,name:"佛山"},{id:4407,name:"江门"},{id:4408,name:"湛江"},{id:4409,name:"茂名"},{id:4412,name:"肇庆"},{id:4413,name:"惠州"},{id:4414,name:"梅州"},{id:4415,name:"汕尾"},{id:4416,name:"河源"},{id:4417,name:"阳江"},{id:4418,name:"清远"},{id:4419,name:"东莞"},{id:4420,name:"中山"},{id:4451,name:"潮州"},{id:4452,name:"揭阳"},{id:4453,name:"云浮"}]},
   {name:"广西",items:[{id:4501,name:"南宁"},{id:4502,name:"柳州"},{id:4503,name:"桂林"},{id:4504,name:"梧州"},{id:4505,name:"北海"},{id:4506,name:"防城港"},{id:4507,name:"钦州"},{id:4508,name:"贵港"},{id:4509,name:"玉林"},{id:4510,name:"百色"},{id:4511,name:"贺州"},{id:4512,name:"河池"},{id:4513,name:"来宾"},{id:4514,name:"崇左"}]},
   {name:"云南",items:[{id:5301,name:"昆明"},{id:5303,name:"曲靖"},{id:5304,name:"玉溪"},{id:5305,name:"保山"},{id:5306,name:"昭通"},{id:5307,name:"丽江"},{id:5308,name:"普洱"},{id:5309,name:"临沧"},{id:5323,name:"楚雄彝族自治州"},{id:5325,name:"红河哈尼族彝族自治州"},{id:5326,name:"文山壮族苗族自治州"},{id:5328,name:"西双版纳傣族自治州"},{id:5329,name:"大理白族自治州"},{id:5331,name:"德宏傣族景颇族自治州"},{id:5333,name:"怒江傈僳族自治州"},{id:5334,name:"迪庆藏族自治州"}]},
   {name:"贵州",items:[{id:5201,name:"贵阳"},{id:5202,name:"六盘水"},{id:5203,name:"遵义"},{id:5204,name:"安顺"},{id:5222,name:"铜仁地区"},{id:5223,name:"黔西南布依族苗族自治州"},{id:5224,name:"毕节地区"},{id:5226,name:"黔东南苗族侗族自治州"},{id:5227,name:"黔南布依族苗族自治州"}]},
   {name:"四川",items:[{id:5101,name:"成都"},{id:5103,name:"自贡"},{id:5104,name:"攀枝花"},{id:5105,name:"泸州"},{id:5106,name:"德阳"},{id:5107,name:"绵阳"},{id:5108,name:"广元"},{id:5109,name:"遂宁"},{id:5110,name:"内江"},{id:5111,name:"乐山"},{id:5113,name:"南充"},{id:5114,name:"眉山"},{id:5115,name:"宜宾"},{id:5116,name:"广安"},{id:5117,name:"达州"},{id:5118,name:"雅安"},{id:5119,name:"巴中"},{id:5120,name:"资阳"},{id:5132,name:"阿坝藏族羌族自治州"},{id:5133,name:"甘孜藏族自治州"},{id:5134,name:"凉山彝族自治州"}]},
   {name:"内蒙古",items:[{id:1501,name:"呼和浩特"},{id:1502,name:"包头"},{id:1503,name:"乌海"},{id:1504,name:"赤峰"},{id:1505,name:"通辽"},{id:1506,name:"鄂尔多斯"},{id:1507,name:"呼伦贝尔"},{id:1508,name:"巴彦淖尔"},{id:1509,name:"乌兰察布"},{id:1522,name:"兴安盟"},{id:1525,name:"锡林郭勒盟"},{id:1529,name:"阿拉善盟"}]},
   {name:"宁夏",items:[{id:6401,name:"银川"},{id:6402,name:"石嘴山"},{id:6403,name:"吴忠"},{id:6404,name:"固原"},{id:6405,name:"中卫"}]},
   {name:"甘肃",items:[{id:6201,name:"兰州"},{id:6202,name:"嘉峪关"},{id:6203,name:"金昌"},{id:6204,name:"白银"},{id:6205,name:"天水"},{id:6206,name:"武威"},{id:6207,name:"张掖"},{id:6208,name:"平凉"},{id:6209,name:"酒泉"},{id:6210,name:"庆阳"},{id:6211,name:"定西"},{id:6212,name:"陇南"},{id:6229,name:"临夏回族自治州"},{id:6230,name:"甘南藏族自治州"}]},
   {name:"青藏",items:[{id:6301,name:"西宁"},{id:6321,name:"海东地区"},{id:6322,name:"海北藏族自治州"},{id:6323,name:"黄南藏族自治州"},{id:6325,name:"海南藏族自治州"},{id:6326,name:"果洛藏族自治州"},{id:6327,name:"玉树藏族自治州"},{id:6328,name:"海西蒙古族藏族自治州"}]},
   {name:"西藏",items:[{id:5401,name:"拉萨"},{id:5421,name:"昌都地区"},{id:5422,name:"山南地区"},{id:5423,name:"日喀则地区"},{id:5424,name:"那曲地区"},{id:5425,name:"阿里地区"},{id:5426,name:"林芝地区"}]},
   {name:"新疆",items:[{id:6501,name:"乌鲁木齐"},{id:6502,name:"克拉玛依"},{id:6521,name:"吐鲁番地区"},{id:6522,name:"哈密地区"},{id:6523,name:"昌吉回族自治州"},{id:6527,name:"博尔塔拉蒙古自治州"},{id:6528,name:"巴音郭楞蒙古自治州"},{id:6529,name:"阿克苏地区"},{id:6530,name:"克孜勒苏柯尔克孜自治州"},{id:6531,name:"喀什地区"},{id:6532,name:"和田地区"},{id:6540,name:"伊犁哈萨克自治州"},{id:6542,name:"塔城地区"},{id:6543,name:"阿勒泰地区"},{id:659001,name:"石河子"},{id:659002,name:"阿拉尔"},{id:659003,name:"图木舒克"},{id:659004,name:"五家渠"}]},
   {name:"安徽",items:[{id:3401,name:"合肥"},{id:3402,name:"芜湖"},{id:3403,name:"蚌埠"},{id:3404,name:"淮南"},{id:3405,name:"马鞍山"},{id:3406,name:"淮北"},{id:3407,name:"铜陵"},{id:3408,name:"安庆"},{id:3410,name:"黄山"},{id:3411,name:"滁州"},{id:3412,name:"阜阳"},{id:3413,name:"宿州"},{id:3414,name:"巢湖"},{id:3415,name:"六安"},{id:3416,name:"亳州"},{id:3417,name:"池州"},{id:3418,name:"宣城"}]},
   {name:"浙江",items:[{id:3301,name:"杭州"},{id:3302,name:"宁波"},{id:3303,name:"温州"},{id:3304,name:"嘉兴"},{id:3305,name:"湖州"},{id:3306,name:"绍兴"},{id:3307,name:"金华"},{id:3308,name:"衢州"},{id:3309,name:"舟山"},{id:3310,name:"台州"},{id:3311,name:"丽水"}]},
   {name:"福建",items:[{id:3501,name:"福州"},{id:3502,name:"厦门"},{id:3503,name:"莆田"},{id:3504,name:"三明"},{id:3505,name:"泉州"},{id:3506,name:"漳州"},{id:3507,name:"南平"},{id:3508,name:"龙岩"},{id:3509,name:"宁德"}]},
   {name:"台湾",items:[{id:7101,name:"台北"},{id:7102,name:"高雄"},{id:7103,name:"基隆"},{id:7104,name:"台中"},{id:7105,name:"台南"},{id:7106,name:"新竹"},{id:7107,name:"嘉义"}]},
   {name:"香港",items:[{id:8101,name:"中西区"},{id:8102,name:"湾仔区"},{id:8103,name:"东区"},{id:8104,name:"南区"},{id:8105,name:"油尖旺区"},{id:8106,name:"深水埗区"},{id:8107,name:"九龙城区"},{id:8108,name:"黄大仙区"},{id:8109,name:"观塘区"},{id:8110,name:"荃湾区"},{id:8111,name:"葵青区"},{id:8112,name:"沙田区"},{id:8113,name:"西贡区"},{id:8114,name:"大埔区"},{id:8115,name:"北区"},{id:8116,name:"元朗区"},{id:8117,name:"屯门区"},{id:8118,name:"离岛区"}]},
   {name:"澳门",items:[{id:8200,name:"澳门"}]},
   {name:"海外",items:[{id:60700000,name:"美国"},{id:60501000,name:"英国"},{id:60600000,name:"加拿大"},{id:60100000,name:"澳大利亚"},{id:60200001,name:"法国"},{id:60300001,name:"新加坡"},{id:60400001,name:"新西兰"},{id:60800001,name:"德国"},{id:60900001,name:"韩国"},{id:61000001,name:"俄罗斯"},{id:61100001,name:"日本"},{id:61200001,name:"意大利"},{id:61300001,name:"爱尔兰"},{id:61400001,name:"荷兰"},{id:61500001,name:"马来西亚"},{id:61600001,name:"瑞士"},{id:61700001,name:"泰国"},{id:61800001,name:"乌克兰"},{id:61900001,name:"南非"},{id:62000001,name:"芬兰"},{id:62100001,name:"瑞典"},{id:62900000,name:"奥地利"},{id:62200001,name:"西班牙"},{id:62300001,name:"比利时"},{id:62400001,name:"挪威"},{id:62500001,name:"丹麦"},{id:62600001,name:"菲律宾"},{id:62700001,name:"波兰"},{id:62800001,name:"印度"},{id:63000000,name:"阿根廷"},{id:63100000,name:"巴西"},{id:63200000,name:"白俄罗斯"},{id:63300000,name:"哥伦比亚"},{id:63400000,name:"古巴"},{id:63500000,name:"埃及"},{id:63600000,name:"希腊"},{id:63700000,name:"匈牙利"},{id:63800000,name:"印度尼西亚"},{id:63900000,name:"伊朗"},{id:64000000,name:"蒙古"},{id:64100000,name:"墨西哥"},{id:64200000,name:"葡萄牙"},{id:64300000,name:"沙特阿拉伯"},{id:64400000,name:"土耳其"}]},
//   {name:"海外2",items:[{id:9101,name:"美国"},{id:9102,name:"澳大利亚"},{id:9103,name:"加拿大"},{id:919001,name:"英国"},{id:919002,name:"新加坡"}]}
    
]





