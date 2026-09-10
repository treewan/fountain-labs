#!/usr/bin/env python3
"""Build the supplier dataset the supply-chain page reads.

Two sources are joined here. The listed-company set is the Chinese humanoid
supplier index published at humanityslastmachine.com; the per-company figures
on seven of those rows, and three companies the index does not carry, come
from the April 2026 36Kr analysis of the Optimus chain.

The index has defects that would become ours on republication, so they are
handled rather than passed through: an exact duplicate row is dropped, one of
two contradictory rows for the same company is dropped, and ticker formats
are normalised. One row whose English name, Chinese name and ticker do not
agree with each other is kept and flagged rather than silently rewritten —
guessing which of the three fields is the wrong one is not our call.

A third source is merged in from tools/global_suppliers.py: the component
makers outside the Chinese listed index, without which the page maps one
supply base rather than the part. Those rows carry a country and an evidence
grade instead of a ticker, because that is what their sources actually give.

Emits public/_assets/supply-chain-data.js.
"""

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from global_suppliers import GLOBAL, GROUP, rows as global_rows  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent.parent / "public" / "_assets" / "supply-chain-data.js"

# en, cn, category, city, founded, ticker, customers
INDEX = [
["Allwinner Tech","全志科技","PCBs & Logic","Zhuhai","2007","300458.SZ","Unitree"],
["Ampelon","安培龙","Sensors","Shenzhen","2004","301289.SZ","Tesla"],
["AVIC Electromech","中航电测","Hand Units","Xi'an","1965","300114.SZ","Tesla"],
["Bafang Electric","八方股份","Motors","Suzhou","2003","603489.SH","Tesla"],
["Baowu Magnesium","宝武镁业","Materials","Nanjing","1993","002182.SZ","Tesla"],
["Bee-Inventive","必创科技","Sensors","Beijing","2005","300667.SZ","Tesla"],
["Beite Technology","贝特科技","Screws","Shanghai","2002","603009.SH","Tesla/Unitree"],
["Bethel Automotive","伯特利","Other Components","Wuhu","2004","603596.SH","Tesla"],
["BluePark New Energy","北汽蓝谷","Other Components","Beijing","1992","600733.SH","Tesla"],
["Bojie Technology","博杰股份","Sensors","Zhuhai","2012","002975.SZ","Tesla"],
["Bozhong Precision","博众精工","Assemblies","Suzhou","2006","688097.SH","AGI Bot"],
["CATL","宁德时代","Other Components","Ningde","2011","300750.SZ","Tesla"],
["Changqing Technology","长青科技","Hand Units","Changzhou","2005","001323.SZ","Tesla"],
["Changsheng Bearings","长盛轴承","Bearings","Jiaxing","1995","300718.SZ","Tesla/AGI Bot/Unitree"],
["ConST Instruments","康斯特","Sensors","Beijing","2004","300445.SZ","Tesla"],
["CubeMars","三合智能","Motors","Nanchang","2009","Private","Unitree"],
["Dafeng Industry","大丰实业","Data","Ningbo","2002","603081.SH","AGI Bot"],
["Dahua Technology","大华股份","Other Components","Hangzhou","2001","002236.SZ","Tesla"],
["Dechang Motors","德昌股份","Motors","Ningbo","2002","605555.SH","Tesla"],
["Dingzhi Technology","鼎智科技","Screws","Changzhou","2008","873593.BJ","Tesla"],
["DJI","大疆","Sensors","Shenzhen","2006","Private","Unitree"],
["Donghua Test","东华测试","Sensors","Jingjiang","1993","300354.SZ","AGI Bot"],
["Dongyangguang","东阳光","Data","Shenzhen","1992","600673.SH","AGI Bot"],
["Estun Automation","埃斯顿","Other Components","Nanjing","1993","002747.SZ","Tesla"],
["Everwin Precision","长盈精密","Other Components","Shenzhen","2001","300115.SZ","Tesla/Figure AI"],
["Forly Intelligent","丰立智能","Reducers","Taizhou","1995","301368.SZ","Tesla"],
["Founder Motor","方正电源","Motors","Lishui","1995","002196.SZ","Tesla"],
["Fulin Precision","富临精工","Actuators","Mianyang","1997","300432.SZ","AGI Bot"],
["Furi Medical","福瑞股份","Sensors","Hohhot","1998","300049.SZ","Tesla"],
["Guangyang Bearings","光洋股份","Bearings","Changzhou","1987","002708.SZ","Tesla"],
["Guomao Reducer","国茂股份","Reducers","Changzhou","1993","603915.SH","Tesla"],
["Hangzhou Seenpin Electromechanical Transmission","新华传动","Hand Units","Hangzhou","1999","Private","Tesla/Unitree"],
["Hanwei Electronics","汉威科技","Sensors","Zhengzhou","1998","300007.SZ","Tesla/AGI Bot"],
["Hanwei Electronics Group","汉威科技","Hand Units","Zhengzhou","1998","300007 SZ","AGI Bot/Unitree"],
["Hanyu Group","汉宇集团","Hand Units","Jiangmen","2002","300403.SZ","Tesla"],
["Haoneng Technology","豪能股份","Reducers","Chengdu","2006","603809.SH","Tesla"],
["Haozhi Electromechanical","昊志机电","Reducers","Guangzhou","2006","300503.SZ","Tesla"],
["Hechuan Technology","禾川科技","Motors","Quzhou","2011","688320.SH","Tesla/Unitree"],
["Henggong Precision","恒工精密","Reducers","Handan","2012","301261.SZ","Tesla/AGI Bot"],
["Hengli Hydraulic","恒立液压","Screws","Changzhou","1991","601100.SH","Tesla"],
["Hengshuai","恒帅股份","Screws","Ningbo","2001","300969.SZ","Tesla"],
["Hikvision","海康威视","Other Components","Hangzhou","2001","002415.SZ","Tesla"],
["Hongsheng Huayuan","宏盛华源","Reducers","Jinan","2000","601096.SH","Tesla"],
["Huachang Chemical","华昌化工","Materials","Suzhou","1999","002274.SZ","Tesla"],
["Huaxiang Elec.","华翔电子","Actuators","Ningbo","1988","002048.SZ","AGI Bot"],
["Huayan Precision","华研精机","Sensors","Guangzhou","2002","301138.SZ","Tesla"],
["Huayi Tech","华依科技","Sensors","Shanghai","1998","688071.SH","AGI Bot"],
["iFLYTEK","科大讯飞","Intelligence","Hefei","1999","002230.SZ","AGI Bot"],
["Inovance Technology","汇川技术","Motors","Shenzhen","2003","300124.SZ","Tesla"],
["iSoftStone","软通动力","Intelligence","Beijing","2005","301236.SZ","AGI Bot"],
["Jiangsu Gian Technology","精研科技","Hand Units","Changzhou","2004","300709 SZ","AGI Bot"],
["Jifeng Auto Parts","继峰股份","Assemblies","Ningbo","1996","603997.SH","Tesla"],
["Jinli Precision","金力股份","Screws","Handan","2010","300984.SZ","Tesla"],
["Jinyang Shares","金杨股份","Other Components","Wuxi","1998","301210.SZ","AGI Bot"],
["Jones Tech","中石科技","Materials","Beijing","1997","300684.SZ","Tesla"],
["Joyson Electronics","均胜电子","Assemblies","Ningbo","2004","600699.SH","Tesla"],
["Junpu Intelligent","均普智能","Intelligence","Ningbo","2008","688306.SH","AGI Bot"],
["Kaite Auto Parts","凯特股份","Sensors","Wuhan","1996","832978.BJ","Tesla"],
["Keli Sensing","柯力传感","Sensors","Ningbo","1995","603662.SH","Tesla"],
["Kinco Automation","步科股份","Reducers","Shenzhen","1996","688160.SH","Tesla"],
["Kingfa Tech","金发科技","Materials","Guangzhou","1993","600143.SH","Tesla/Unitree"],
["Leaderdrive","绿的谐波","Reducers","Suzhou","2011","688017.SH","Tesla/Figure AI/AGI Bot/Unitree"],
["Leadshine Technology","雷赛智能","Screws","Shenzhen","1997","002979.SZ","Tesla"],
["Lens Technology","蓝思科技","Periphery","Changsha","2003","300433.SZ","Tesla/AGI Bot"],
["Lianming Automotive","联明股份","Castings","Shanghai","2003","603006.SH","Tesla"],
["Lixing Steel Ball","力星股份","Bearings","Nantong","1989","300421.SZ","Tesla"],
["Longsheng Technology","隆盛科技","Reducers","Wuxi","2004","300680.SZ","Tesla"],
["Longxi Bearing","龙溪股份","Screws","Zhangzhou","1958","600592.SH","AGI Bot"],
["Luster","凌云光","Sensors","Beijing","2002","688400.SH","Unitree"],
["Luxshare ICT","立讯精密","Other Components","Dongguan","2004","002475.SZ","Tesla"],
["Luxvisions Innovation","立讯创新","Hand Units","Guangzhou","2018","Private","AGI Bot"],
["LY iTech","领益智造","Other Components","Dongguan","2006","002600.SZ","Tesla/Figure AI/AGI Bot"],
["Meilixin Die-casting","美利信","Castings","Chongqing","2001","301307.SZ","Tesla"],
["MEMSensing","敏芯股份","Sensors","Suzhou","2007","688286.SH","Tesla"],
["MOONS' Industries","鸣志电器","Motors","Shanghai","1994","603728.SH","Tesla/Figure AI/Unitree"],
["Ningbo Dongli","宁波东力","Reducers","Ningbo","1997","002164.SZ","Tesla"],
["Orbbec","奥比中光","Sensors","Shenzhen","2013","688322.SH","AGI Bot/Unitree"],
["PaXiNi","帕西尼","Hand Units","Shenzhen","2021","Private","Figure AI/Unitree"],
["Power Transmission","全力传动","Reducers","Yinchuan","2003","300904.SZ","Tesla"],
["Prestige New Materials","普利特","Materials","Shanghai","1993","002324.SZ","Tesla"],
["Qinchuan Machine Tool","秦川机床","Reducers","Baoji","1965","000837.SZ","Tesla"],
["Rayly Micro-Motor","江苏雷利","Screws","Changzhou","1993","300660.SZ","Tesla/AGI Bot/Unitree"],
["Riying Electronics","日盈电子","Sensors","Changzhou","1998","603286.SH","Tesla"],
["Rongtai Industry","嵘泰股份","Castings","Yangzhou","2000","605133.SH","Tesla"],
["Ruide Design","锐德智能","Screws","Foshan","1997","301135.SZ","Tesla"],
["Sanhua Intelligent Controls","三花智控","Actuators","Shaoxing","1994","002050.SZ","Tesla/AGI Bot"],
["Shanghai Longcheer Tech","龙旗科技","Actuators","Shanghai","2002","603341.SH","AGI Bot"],
["Shengyi Technology","生益科技","PCBs & Logic","Dongguan","1985","600183.SH","Tesla"],
["Shengyi Technology","生益科技","PCBs & Logic","Dongguan","1985","600183.SH","Tesla"],
["Shenhao Technology","神浩科技","Sensors","Hangzhou","2002","300853.SZ","Tesla"],
["Shijie Technology","世运电路","PCBs & Logic","Jiangmen","1985","300476.SZ","Tesla"],
["Shijie Technology","世运电路","PCBs & Logic","Jiangmen","1985","603920.SH","Tesla"],
["Shuanghuan Driveline","双环传动","Reducers","Taizhou","1980","002472.SZ","Tesla/Unitree"],
["Shuanglin","双林股份","Screws","Ningbo","1987","300100.SZ","Unitree"],
["Sling Smart","斯菱股份","Reducers","Huai'an","2004","301550.SZ","Tesla"],
["Sugon","中科曙光","Intelligence","Beijing","1996","603019.SH","AGI Bot"],
["Suzhou TZTEK Technology","天准科技","Screws","Suzhou","2005","688003.SH","AGI Bot"],
["Tengya Precision","腾亚精工","Sensors","Nanjing","1999","301125.SZ","Tesla"],
["Tongli Transmission","通力科技","Reducers","Wenzhou","2008","301255.SZ","Tesla"],
["Topstar","拓斯达","Other Components","Dongguan","2007","300607.SZ","Tesla"],
["Tuopu Group","拓普集团","Actuators","Ningbo","1983","601689.SH","Tesla"],
["Veichi Electric","伟创电气","Motors","Suzhou","2005","688698.SH","Tesla"],
["Veko Technology","富科科技","Screws","Xiamen","2005","301196.SZ","Tesla"],
["Victory Giant Tech","崇达技术","PCBs & Logic","Huizhou","1995","300476.SZ","Tesla"],
["Wanma","万马股份","Other Components","Hangzhou","1989","002276.SZ","Unitree"],
["Wanxiang Qianchao","万向钱潮","Other Components","Hangzhou","1969","000559.SZ","Tesla"],
["Weiguang Electronic","微光股份","Motors","Hangzhou","1986","002801.SZ","Tesla"],
["Wolong Electric","卧龙电驱","Motors","Shaoxing","1984","600580.SH","Tesla/AGI Bot/Unitree"],
["Wuxi Best","贝斯特","Screws","Wuxi","1997","300580.SZ","Unitree"],
["XCC Group","亚洲新巴","Screws","Shaoxing","2002","603667.SH","Tesla"],
["Xiangxin Technology","祥鑫科技","Reducers","Dongguan","2004","002965.SZ","Tesla"],
["Xiaxia Precision","夏厦精密","Reducers","Ningbo","1999","001306.SZ","Tesla"],
["Xindong Link","芯动联科","Sensors","Wuxi","2012","688582.SH","Tesla"],
["Xingyuan Zhuomei","星源卓镁","Materials","Ningbo","2003","301398.SZ","Tesla"],
["Xinquan Automotive Trim","新泉股份","Assemblies","Changzhou","2001","603179.SH","Tesla"],
["Xusheng Group","旭升集团","Materials","Ningbo","2003","603305 CH","Figure AI"],
["Yantai Fuli New Material Technology","福莱新材","Hand Units","Jiaxing","2009","Private","Tesla"],
["Yinlun Machinery","银轮股份","Actuators","Tiantaishan","1958","002126 CH","Figure AI"],
["Yusanxia","渝三峡A","Materials","Chongqing","1992","000565.SZ","Tesla"],
["Zhaowei Machinery","兆威机电","Reducers","Shenzhen","2001","003021.SZ","Tesla/Unitree"],
["Zhejiang Jingu Co","金固股份","Other Components","Hangzhou","1996","002488.SZ","AGI Bot"],
["Zhejiang Laifual Drive","来福谐波","Reducers","Zhejiang","2013","Private","Unitree"],
["Zhejiang Rongtai Electric Material Co.","浙江融泰","Screws","Jiaxing","2004","Private","Tesla"],
["Zhongda Leader","中大力德","Reducers","Ningbo","1998","002896.SZ","AGI Bot/Unitree"],
]

# Rows in the index carrying a figure from the 36Kr analysis, keyed by Chinese
# name because the English names differ between the two sources.
NOTES = {
"拓普集团": "Tier 0.5 for Optimus, assembling linear and rotary actuators. Tesla reported at 35–40% of revenue; Mexico plant in production, 300,000 sets targeted for Q2 2026.",
"三花智控": "Joint module assemblies. $685M Tesla order in October 2025, deliveries from Mexico from 2026.",
"绿的谐波": "Harmonic reducers: over 60% of the domestic market, over 35% globally. Passed Tesla verification and supplies its Mexico plant exclusively; humanoid revenue reached 30% in Q1 2025.",
"双环传动": "RV reducers. Reaches Optimus indirectly, through Tuopu and Sanhua rather than directly.",
"兆威机电": "Dexterous-hand drive modules, integrating micro-motor, gearbox and screw in one part.",
"汇川技术": "Servo motors, and also upstream of UBTECH and Unitree.",
"柯力传感": "The only domestic maker in volume production of six-axis force/torque sensors; parts in Tesla verification.",
}

# Named in the analysis but absent from the index.
EXTRA = [
["Wuzhou New Spring","五洲新春","Screws","Xinchang","1997","603667.SH","Tesla",
 "Main supplier of the reverse planetary roller screws used in hip and knee. Thailand plant online 2026; share price rose 183% across 2025."],
["Xinjian Transmission","新剑传动","Screws","Hangzhou","","Private","Tesla",
 "Planetary roller screws, unlisted. Filed for listing guidance 9 January 2026 with CITIC advising; line rated at one million screws a year."],
["AMETEK","","Motors","—","1930","NYSE: AME","Tesla",
 "Coreless motors, among the top three worldwide. Selection for 2026 considered likely rather than settled."],
]

# The English name, Chinese name and ticker on this row do not agree with each
# other. Left as published and marked, rather than us picking which to rewrite.
DISPUTED = {("Victory Giant Tech", "300476.SZ")}

# Of the two rows published for this company, only one ticker can be right.
DROP = {("Shijie Technology", "300476.SZ")}


def ticker(t):
    """002126 CH and 300709 SZ are the same thing as 002126.SZ; normalise."""
    t = t.strip()
    m = re.fullmatch(r"(\d{6})[ .](SZ|SH|BJ|CH)", t)
    if not m:
        return t
    board = m.group(2)
    if board == "CH":  # exchange inferred from the number range
        board = "SH" if m.group(1)[0] == "6" else "SZ"
    return f"{m.group(1)}.{board}"


def main():
    seen, rows, dropped, dupes = set(), [], 0, 0
    for en, cn, cat, city, yr, stk, cu in INDEX:
        stk = ticker(stk)
        if (en, stk) in DROP:
            dropped += 1
            continue
        key = (en, cn, cat, stk)
        if key in seen:
            dupes += 1
            continue
        seen.add(key)
        rows.append({"en": en, "cn": cn, "cat": cat, "co": "China", "city": city, "yr": yr,
                     "stk": stk, "cu": cu.split("/") if cu else [],
                     **({"note": NOTES[cn]} if cn in NOTES else {}),
                     **({"flag": "Name, Chinese name and ticker do not agree in the source"}
                        if (en, stk) in DISPUTED else {})})

    for en, cn, cat, city, yr, stk, cu, note in EXTRA:
        rows.append({"en": en, "cn": cn, "cat": cat,
                     "co": "United States" if en == "AMETEK" else "China",
                     "city": city, "yr": yr, "stk": stk, "cu": cu.split("/"),
                     "note": note, "only": True})

    index_rows = len(rows)
    rows.extend(global_rows())
    for r in rows:
        r["grp"] = GROUP.get(r["cat"], "Structure")

    rows.sort(key=lambda r: r["en"].lower())
    cats = {}
    custs = {}
    cos = {}
    for r in rows:
        cats[r["cat"]] = cats.get(r["cat"], 0) + 1
        cos[r["co"]] = cos.get(r["co"], 0) + 1
        for c in r["cu"]:
            custs[c] = custs.get(c, 0) + 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("window.SUPPLIERS = " + json.dumps(rows, ensure_ascii=False) + ";\n")

    print(f"wrote {OUT.name}: {len(rows)} suppliers "
          f"({index_rows} from the listed index, {len(rows) - index_rows} from the component guides)")
    print("  countries: " + ", ".join(f"{k} {v}" for k, v in sorted(cos.items(), key=lambda x: -x[1])))
    print(f"  dropped {dupes} exact duplicate, {dropped} contradictory row")
    print(f"  {len(EXTRA)} added from the analysis, {len(NOTES)} index rows annotated")
    print("  categories: " + ", ".join(f"{k} {v}" for k, v in sorted(cats.items(), key=lambda x: -x[1])))
    print("  customers: " + ", ".join(f"{k} {v}" for k, v in sorted(custs.items(), key=lambda x: -x[1])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
