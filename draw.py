"""Render the 20 November 2026 front page from supplied editorial copy."""
from functools import lru_cache
from math import cos, sin, pi
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

S = 2
PAPER, RED, NAVY = '#F7F3E8', '#9E2B25', '#1F3552'
INK, GREY, RULE = '#20272B', '#555B60', '#A79A86'
SEA, LAND = '#DCE8EE', '#E8D9A8'
image = Image.new('RGB', (1024*S, 1024*S), PAPER)
draw = ImageDraw.Draw(image)
faces = dict(serif='DejaVuSerif', title='DejaVuSerif-Bold',
             italic='DejaVuSerif-Italic', sans='DejaVuSans', bold='DejaVuSans-Bold')
checked = []


@lru_cache
def font(face, size):
    path = Path('/usr/share/fonts/truetype/dejavu') / (faces.get(face, face) + '.ttf')
    if face == 'brief':
        path = Path('/usr/share/fonts/truetype/noto/NotoSans-ExtraCondensed.ttf')
    if face == 'italic' and not path.exists():
        path = Path('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf')
    return ImageFont.truetype(str(path), round(size*S))


def scale(values):
    return tuple(round(n*S) for n in values)


def rect(box, fill, outline=None):
    draw.rectangle(scale(box), fill, outline, width=S)


def line(points, fill=RULE, width=1):
    draw.line([scale(p) for p in points], fill, max(1, round(width*S)), joint='curve')


def poly(points, fill, outline=None):
    draw.polygon([scale(p) for p in points], fill, outline)


def dot(x, y, r, fill, outline=None):
    draw.ellipse(scale((x-r, y-r, x+r, y+r)), fill, outline)


def wrap(text, face, size, width):
    rows = ['']
    for word in text.split(' '):
        candidate = (rows[-1] + ' ' + word).strip()
        if rows[-1] and font(face, size).getlength(candidate) > width*S:
            rows.append(word)
        else:
            rows[-1] = candidate
    return rows


def block(text, box, face, max_size, color=INK, rows=1, align='left', leading=1.12):
    x, y, w, h = box
    for half in range(round(max_size*2), 9, -1):
        size = half / 2
        f = font(face, size)
        parts = wrap(text, face, size, w)
        step = round(size*leading*S)
        bounds = [f.getbbox(part, anchor='lt') for part in parts]
        if (len(parts) <= rows
                and all(max(f.getlength(p), b[2])-min(0, b[0]) <= w*S
                        for p, b in zip(parts, bounds))
                and max(i*step+b[3] for i, b in enumerate(bounds)) <= h*S):
            break
    else:
        raise AssertionError((text, box))
    for i, (part, b) in enumerate(zip(parts, bounds)):
        left = min(0, b[0])
        width = max(f.getlength(part), b[2])-left
        offset = {'left': 0, 'right': w*S-width, 'center': (w*S-width)/2}[align]
        px = round(x*S + offset-left)
        py = round(y*S) + i*step
        assert x*S-0.51 <= px+left and px+left+width <= (x+w)*S+0.51, text
        assert py+b[3] <= (y+h)*S+0.51, text
        draw.text((px, py), part, font=f, fill=color, anchor='lt')
    checked.append(text)


def local_shapes(x, y):
    """Translate illustration coordinates to the page."""
    return (
        lambda b, c: rect((x+b[0], y+b[1], x+b[2], y+b[3]), c),
        lambda p, c, w=1: line([(x+a, y+b) for a, b in p], c, w),
        lambda p, c: poly([(x+a, y+b) for a, b in p], c),
        lambda a, b, r, c: dot(x+a, y+b, r, c),
    )


def hero_art(index, x, y, w):
    r, l, p, d = local_shapes(x, y)
    h = 121
    if index == 1:
        for yy in range(h):
            r((0, yy, w, yy+1), (25+yy//5, 36+yy//5, 62+yy//5))
        d(269, 27, 13, '#D8C6A5')
        r((0, 76, w, h), '#223E58')
        for i in range(23):
            a, height = i*14, 7+(i*17)%28
            r((a, 76-height, min(a+11, w), 76), '#172337')
            for j in range(2):
                r((a+3+j*5, 71-height, a+4+j*5, 73-height), '#E8B572')
        for i in range(16):
            a, b = (i*59)%282, 78+(i*11)%42
            l([(a,b),(a+14,b)], '#43617A')
        for i, (a,b) in enumerate([(20,85),(105,94),(199,105)]):
            l([(a,b+4),(a+69,b-10)], '#BDAE99', 3)
            for shift in (5,25,45):
                u, v = a+shift, b+5-shift/5
                l([(u,v+7),(u+3,v+2),(u+8,v-1),(u+13,v-1),(u+18,v+3)],
                  '#84939C', 1.2)
            for j in range(5):
                xx, yy = a+30+j*8, b-10-j*9
                l([(xx,yy),(xx+5,yy-6)], '#F7CA93', 1.5)
            p([(a+20,b),(a+25,b-13),(a+29,b-7),(a+34,b-18),
               (a+39,b)], '#E17346')
            d(a+30,b-3,2,'#FFE0A6')
    elif index == 2:
        r((0,0,w,h), '#386482')
        p([(0,0),(195,0),(174,18),(156,26),(148,39),(132,47),
           (114,68),(86,78),(53,109),(44,h),(0,h)], '#9FAD84')
        l([(195,0),(174,18),(156,26),(148,39),(132,47),(114,68),
           (86,78),(53,109),(44,h)], '#E5D9AE', 2)
        for i in range(3):
            pts = []
            for j in range(66):
                a = j*.076+i*2*pi/3
                radius = 7+j*.94
                pts.append((179+radius*cos(a), 59+radius*.81*sin(a)))
            l(pts, ['#E7EBE4','#B8D1D8','#86AFBD'][i], 3)
        for i in range(18):
            a, b = 6+(i*67)%283, 8+(i*19)%100
            l([(a,b),(a-4,b+7)], '#A8C1C3', .6)
        d(132,47,4,'#F8EACB')
        d(132,47,2.5,RED)
        l([(129,45),(107,29),(61,29)], '#263E40')
        block('GOPALPUR', (x+61,y+17,62,11), 'bold', 9, '#203A3E')
    else:
        r((0,0,w,h), '#222E43')
        for b in range(17,109,18):
            l([(14,b),(w-14,b)], '#3C4B61', .6)
        for a in range(15,235,31):
            l([(a,12),(a,108)], '#3C4B61', .6)
        points = [(15,26),(31,29),(46,20),(66,37),(80,35),(99,56),
                  (118,51),(136,65),(151,61),(170,89),(186,82),(202,97)]
        p(points + [(202,108),(15,108)], '#463849')
        l(points, '#F17A71', 2.5)
        d(202,97,3,'#F17A71')
        for i, label in enumerate(('Taipei −6.2%', 'Seoul −5.2%', 'Tokyo −5.1%')):
            block(label, (x+217,y+21+i*27,w-227,15), 'bold', 12, '#FFF1DE')


HEROES = [
    ("1 · KYIV, UKRAINE · WAR", "Russian missiles hit three Kyiv bridges",
     "An overnight barrage of about 110 missiles and 400 drones hit three bridges over the Dnipro; at least 3 killed in Kyiv, power and water cut.",
     "— Kyiv Independent · BBC"),
    ("2 · ODISHA, INDIA · CYCLONE", "Cyclone Akvan comes ashore in eastern India",
     "The storm crossed the coast near Gopalpur from about 8 am after more than 300,000 people were moved to shelters. No deaths reported.",
     "— IMD · Deccan Herald"),
    ("3 · TAIPEI · SEOUL · TOKYO · MARKETS", "AI sell-off sinks Asia's stock markets",
     "Taiwan's index fell 6.2% to end its worst week since 1991. Seoul lost 5.2% and Tokyo 5.1% as chipmakers led the slide.",
     "— Al Jazeera · Anadolu"),
]

TILES = [
    ("4 · BRUSSELS · DIPLOMACY", "UK and EU hold a “reset” summit", "Food trade, youth visas, carbon link."),
    ("5 · ANTALYA · CLIMATE", "COP31 reaches its final day with no deal", "Draft text leaves out fossil fuels."),
    ("6 · RIYADH · WAR", "Houthi missile damages Riyadh tower", "Strike hits the PIF tower; more intercepted."),
    ("7 · HORMUZ · ENERGY", "Tanker on fire as Gulf attacks grow", "Iran war enters its ninth month."),
    ("8 · GAZA · WAR", "Israeli troops cross the Yellow Line", "First incursion since the truce."),
    ("9 · TOKYO · ECONOMY", "Japan's inflation picks up to 2.3%", "A December rate rise stays in view."),
    ("10 · WASHINGTON · TECH", "White House fires its cyber chief", "Cairncross out after a week of outages."),
    ("11 · SAN SALVADOR · POLITICS", "Bukele files to run for a third term", "Vote is on 28 February 2027."),
    ("12 · ROME · LABOUR", "General strike over Italy's budget", "Workers and students march in ~100 squares."),
    ("13 · MERCURY · SPACE", "BepiColombo reaches Mercury", "8-year, 6-billion-mile trip ends Saturday."),
]

BRIEFS = [
    '14 LVIV — A strike on a railway station kills two. BBC',
    '15 BERLIN — Merz rejects a "new Yalta" deal over Europe. Reuters',
    '16 COPENHAGEN — Denmark approves Greenland–US Arctic pact. AFP',
    '17 TALLINN — Estonia to shut its Russia border over sabotage. Reuters',
    '18 LONDON — UK and Norway fund £100m+ for two Ukrainian naval vessels. BBC',
    '19 BAGHDAD — Iraqi army enters a militia stronghold. Reuters',
    '20 WASHINGTON — Pentagon puts the US war cost vs Iran at $48.3bn. Reuters',
    '21 PORT-AU-PRINCE — Haiti police kill 34 suspected gang members. Reuters',
    '22 YENNE — Migrant boat capsizes off Senegal; dozens missing. Al Jazeera',
    '23 SOUTH KORDOFAN — Drone strike kills 10 at a Sudan gold mine. Reuters',
    '24 CARACAS — US and Venezuela sign a military cooperation deal. AP',
    '25 NAIROBI — Kenya discharges its last Ebola patient. Reuters',
    '26 MOGADISHU — Somalia orders the UAE ambassador out in 72 hours. Reuters',
    '27 ABUJA — Nigeria moves to end jail for attempted suicide. Reuters',
    '28 BRASÍLIA — Lula advances Indigenous land rights with Chief Raoni. Al Jazeera',
    '29 BOGOTÁ — Colombia protests over tax proposals. Reuters',
    '30 BEIJING — China holds its loan rates for an 18th month. Xinhua',
    '31 TAIPEI — Taiwan flags 2,700 China-linked accounts. Reuters',
    '32 SEOUL — Ruling party moves to impeach the top judge. SBS',
    '33 NEW YORK — Anthropic shares slide on day two after its record IPO. Reuters',
    '34 WELLINGTON — Phillips hits 118 as New Zealand beat India. ICC',
    '35 SYDNEY — Australian shares fall 1.8% in the sell-off. Reuters',
    '36 SUVA — Severe Tropical Cyclone Xavier watched near Fiji. Fiji Met Service',
    '37 CINCINNATI — Fiona the hippo dies after swallowing a hat. AP',
]


def draw_panel(index, x, y, w, content):
    kicker, headline, deck, source = content
    hero_art(index, x, y, w)
    block(kicker, (x,y+129,w,15), 'bold', 12.5, RED)
    block(headline, (x,y+148,w,55), 'title', 25, NAVY, rows=2)
    block(deck, (x,y+207,w,44), 'sans', 13, rows=3)
    block(source, (x,y+253,w,12), 'italic', 11, GREY)


def draw_banner(n, x, y, w):
    r, l, p, d = local_shapes(x, y)
    backgrounds = ['#DCE8EE','#DCE8DF','#27334A','#314F61','#E8DFBF',
                   '#DEE8E7','#303D55','#E9DECA','#E6CCBB','#212C44']
    r((0,0,w,41), backgrounds[n-4])
    if n == 4:
        r((28,6,85,36),'#244783')
        for i in range(12):
            a = i*2*pi/12
            d(56+10*cos(a),21+10*sin(a),1.15,'#F4CF55')
        r((101,6,158,36),'#254578')
        for a,b in ((101,158),(158,101)):
            l([(a,7),(b,35)], '#FFF4E1', 5)
            l([(a,7),(b,35)], RED, 2)
        l([(101,21),(158,21)], '#FFF4E1', 9)
        l([(129,6),(129,36)], '#FFF4E1', 9)
        l([(101,21),(158,21)], RED, 4)
        l([(129,6),(129,36)], RED, 4)
    elif n == 5:
        d(55,21,17,'#54849B')
        p([(43,12),(52,7),(62,12),(59,19),(49,19),(47,27),(41,23)], '#A7BF8B')
        p([(58,23),(69,21),(65,32),(58,36),(54,29)], '#A7BF8B')
        l([(77,8),(77,31)], '#FFF7DE', 7)
        l([(77,11),(77,31)], RED, 2)
        d(77,32,4,RED)
        r((97,10,157,32),RED)
        block('NO DEAL',(x+99,y+16,56,12),'bold',11,'#FFF6DF',align='center')
    elif n == 6:
        for i in range(14):
            a = 8+i*12
            height = 6+i*7%16
            r((a,41-height,a+8,41),'#172336')
            d(a+3,45-height,1,'#BE986E')
        p([(78,41),(78,8),(85,4),(99,4),(106,8),(106,41)], '#172336')
        p([(99,4),(106,8),(106,41),(99,41)], '#2C3B51')
        for row in range(7):
            for column in range(4):
                a, b = 81+6*column, 9+4*row
                color = '#F9CB83' if (row+2*column)%4 else '#586678'
                r((a,b,a+2,b+1), color)
        l([(164,5),(137,8),(108,13)], '#E2AD8D')
        p([(107,6),(109,11),(116,9),(112,14),(116,18),(110,17),
           (107,22),(105,17),(99,18),(103,14),(100,10),(105,11)], '#B9352B')
        d(107,14,1.5,'#FFD692')
    elif n == 7:
        for i in range(4):
            l([(0,29+i*4),(w,29+i*4)], '#578091')
        p([(25,22),(143,22),(130,34),(43,34)], '#242A36')
        r((44,16,64,22),'#DAD2BE')
        r((75,19,117,23),'#A47959')
        p([(100,21),(104,10),(109,15),(113,5),(120,21)], '#EC8650')
        d(108,18,3,'#FFD692')
        d(157,31,4,'#202833')
        l([(157,24),(157,37)], '#202833')
        l([(151,28),(163,34)], '#202833')
    elif n == 8:
        for i in range(6):
            a = 7+i*29
            p([(a,8),(a+14,5),(a+19,21),(a+4,23)], '#CFC49D')
        l([(0,34),(39,20),(79,25),(111,13),(148,16),(w,8)], '#74664D', 5)
        l([(0,34),(39,20),(79,25),(111,13),(148,16),(w,8)], '#F3C849', 2)
        l([(101,29),(101,5)], NAVY, 2)
        p([(102,6),(121,7),(102,16)], RED)
    elif n == 9:
        for i in range(5):
            r((16+i*13,34-i*4,24+i*13,37), '#8BABAA')
        l([(13,33),(28,25),(41,29),(58,19),(76,13),(91,6)], '#326B6B', 2)
        block('2.3%',(x+102,y+9,77,25),'title',25,NAVY)
    elif n == 10:
        p([(55,7),(77,4),(99,7),(96,25),(77,38),(58,25)], '#B6CFD8')
        p([(60,11),(77,8),(94,11),(91,24),(77,33),(63,24)], '#486281')
        l([(25,23),(66,23),(74,17)], '#E3BE95', 3)
        l([(82,26),(90,20),(158,20)], '#E3BE95', 3)
        l([(79,13),(77,20),(83,18),(78,29)], '#FFB377', 1.4)
    elif n == 11:
        r((47,17,98,36), '#48687A')
        r((43,15,102,20), '#608497')
        l([(59,17),(85,17)], INK, 2)
        p([(63,5),(81,7),(79,17),(61,15)], '#FFF1D7')
        l([(67,10),(70,13),(76,8)], RED)
        block('3RD TERM',(x+108,y+15,69,14),'bold',11,RED)
    elif n == 12:
        for i in range(17):
            a,b = 7+i*10.5, 29+(i*7)%7
            d(a,b,2.4,'#70483E')
            r((a-3,b+3,a+3,41), ['#805046','#9E2B25','#414B58'][i%3])
            if i%3 == 0:
                l([(a,b+3),(a,b-14)], '#6B4B3D')
                r((a-6,b-16,a+5,b-10), '#B66858')
        r((54,3,130,16), '#F7E4C7')
        block('SCIOPERO',(x+55,y+5,74,10),'bold',10,RED,align='center')
    else:
        d(136,21,20,'#A6A7AB')
        for a,b,rad in [(124,12,3),(143,10,4),(139,29,5),(151,22,3),(125,28,2)]:
            d(a,b,rad,'#797C87')
        l([(37,27),(67,18),(94,14)], '#E3C894',1.3)
        p([(64,18),(76,14),(80,23),(68,27)], '#E5C593')
        p([(48,9),(58,7),(70,17),(61,20)], '#668CA7')
        p([(74,24),(82,20),(96,29),(87,33)], '#668CA7')
        for a,b in [(12,9),(36,36),(103,8),(167,14),(172,34)]:
            d(a,b,.8,'#F6E5BE')


CONTINENTS = [
    [(-168,66),(-140,70),(-125,72),(-110,73),(-95,80),(-85,66),(-75,62),(-65,60),(-55,52),(-60,45),(-70,42),(-75,35),(-80,25),(-85,30),(-95,20),(-105,20),(-110,25),(-120,35),(-125,48),(-140,60),(-155,58),(-165,60)],
    [(-80,10),(-75,5),(-70,0),(-60,-5),(-50,-5),(-40,-10),(-35,-15),(-40,-25),(-50,-30),(-60,-35),(-70,-40),(-75,-50),(-70,-55),(-75,-35),(-80,-20),(-80,-5)],
    [(-10,35),(0,35),(10,37),(20,32),(30,31),(35,28),(40,20),(45,12),(50,10),(45,0),(40,-10),(35,-20),(30,-30),(20,-35),(15,-30),(10,-15),(5,0),(0,5),(-10,10),(-15,25)],
    [(-10,36),(-5,40),(0,43),(5,45),(10,55),(15,58),(20,60),(25,65),(30,70),(35,68),(30,60),(25,55),(20,50),(15,45),(10,40),(5,38),(0,36)],
    [(35,70),(50,72),(70,73),(90,75),(110,76),(130,72),(150,70),(170,66),(160,60),(150,55),(140,45),(130,40),(120,35),(110,25),(100,20),(95,10),(90,5),(85,15),(80,20),(75,25),(70,30),(60,30),(55,25),(50,30),(45,35),(40,40),(35,45),(35,55),(40,60)],
    [(113,-22),(120,-15),(130,-12),(140,-17),(145,-15),(150,-22),(150,-30),(145,-38),(140,-38),(130,-32),(120,-35),(113,-30)],
]
LOCATIONS = [
    (33,52),(85,20),(121,25),(2,48),(33,35),(47,25),(56,26),(34,31),(140,36),
    (-77,39),(-89,14),(14,40),None,(27,48),(9,50),(8,59),(28,62),(-4,54),
    (47,36),(-80,36),(-72,19),(-17,15),(30,11),(-67,10),(37,-1),(45,2),
    (7,9),(-48,-16),(-74,5),(116,40),(118,28),(127,37),(-74,41),(175,-41),
    (151,-34),(178,-18),(-84,39),
]


def draw_map(x, y, w, h):
    def project(lon, lat):
        return x+(lon+180)/360*w, y+(90-lat)/180*h

    rect((x,y,x+w,y+h), SEA)
    for lon in range(-150,180,30):
        line([project(lon,90),project(lon,-90)], '#CADBE2', .5)
    for lat in range(-60,90,30):
        line([project(-180,lat),project(180,lat)], '#CADBE2', .5)
    for continent in CONTINENTS:
        poly([project(*point) for point in continent], LAND, '#68746B')
    # Spread labels in dense clusters and retain the projected anchors with leaders.
    placed = []
    radius = 5.5
    offsets = [(0,0)] + [(r*cos(a*pi/8),r*sin(a*pi/8))
                         for r in range(8,73,3) for a in range(16)]
    for number, location in enumerate(LOCATIONS, 1):
        if location is None:
            continue
        px, py = project(*location)
        for dx,dy in offsets:
            a = min(x+w-radius-1, max(x+radius+1, px+dx))
            b = min(y+h-radius-1, max(y+radius+1, py+dy))
            if all((a-u)**2+(b-v)**2 >= (2*radius+1)**2 for _,u,v in placed):
                break
        else:
            raise AssertionError(number)
        if abs(a-px)+abs(b-py) > 1:
            line([(px,py),(a,b)], '#714744', .8)
            dot(px,py,1.15,RED)
        placed.append((number,a,b))
    for number,a,b in placed:
        dot(a,b,radius,RED,'#FFF8EB')
        block(str(number),(a-5,b-2.5,10,5.5),'bold',7,'#FFFFFF',align='center')
    rect((x,y,x+w,y+h), None, '#8C9998')


def render():
    regions = [('EUROPE',9),('ASIA',6),('MIDDLE EAST',4),('AFRICA',5),
               ('AMERICAS',9),('OCEANIA',3),('GLOBAL',1)]
    assert len(HEROES)+len(TILES)+len(BRIEFS) == sum(n for _,n in regions) == 37
    line([(24,24),(1000,24)], RED, 2)
    eyebrow = ' '.join(' '.join(word) for word in 'THE WORLD IN ONE DAY'.split())
    block(eyebrow, (24,31,455,14), 'bold', 12, RED)
    block('37 STORIES · EVERY CONTINENT · ALL FROM THIS ONE DAY',
          (508,31,492,14),'bold',12,RED,align='right')
    block('Friday 20 November 2026',(24,50,976,65),'title',62,NAVY)
    block("Russian missiles hit Kyiv's bridges · Cyclone Akvan strikes India · An AI sell-off sinks Asia's markets · UK and EU hold a reset summit",
          (24,117,976,24),'italic',21,RED)
    line([(24,141),(1000,141)], NAVY)
    colors = ['#563E48','#324D67','#794438','#5E542D','#7B3D42','#426363','#4A425E']
    for i, (name,count) in enumerate(regions):
        a = 24+i*140
        rect((a,148,a+135,166), colors[i])
        block(f'{name} {count}', (a+3,152,129,12), 'bold', 10.5, '#FFF7E6', align='center')
    line([(24,173),(1000,173)], RULE)
    stats = [
        ('3','Kyiv bridges hit over the Dnipro'),
        ('300,000+','people moved to shelters before Akvan'),
        ('−6.2%',"Taiwan's share index, Friday's close"),
        ('2.3%','Japan consumer inflation in October'),
        ('$48.3bn',"Pentagon's US war cost vs Iran"),
        ('8 yrs',"BepiColombo's trip to Mercury"),
    ]
    for i,(value,label) in enumerate(stats):
        a = 24+i*163
        if i:
            line([(a-3,182),(a-3,222)])
        block(value,(a+4,178,150,31),'title',29,NAVY,align='center')
        block(label,(a+5,208,149,24),'sans',11.5,GREY,rows=2,align='center')
    line([(24,233),(1000,233)], NAVY)
    for i, content in enumerate(HEROES):
        a = 24+i*329
        if i:
            line([(a-6,240),(a-6,505)])
        draw_panel(i+1,a,240,318,content)
    line([(24,510),(1000,510)], NAVY, 1.5)
    for i,(kicker, headline, deck) in enumerate(TILES):
        j,k = divmod(i,5)
        a,b = 24+k*197,517+j*99
        if k:
            line([(a-5,b),(a-5,b+89)])
        draw_banner(i+4,a,b,188)
        block(kicker,(a,b+45,188,11),'bold',10.5,RED)
        block(headline,(a,b+58,188,26),'bold',14.5,NAVY,rows=2)
        block(deck,(a,b+85,188,11),'sans',10.5)
    line([(24,613),(1000,613)])
    line([(24,717),(1000,717)], NAVY, 1.5)
    block('WHERE IT HAPPENED',(24,725,440,17),'bold',13,NAVY)
    block('ALSO ON FRIDAY 20 NOVEMBER 2026',(445,725,555,17),'bold',13,NAVY)
    draw_map(24,745,407,193)
    line([(438,725),(438,938)])
    line([(722,747),(722,938)])
    for i, brief in enumerate(BRIEFS):
        column, row = divmod(i,12)
        a,b = 445+column*279,747+row*16
        block(brief,(a,b,276,13),'brief',9.5)
        if row < 11:
            line([(a,b+12),(a+275,b+12)], '#D8CDBC', .5)
    rect((24,946,1000,985), None, RED)
    block("DATE CHECK ✓ Every story on this page happened, or was first reported, on Friday 20 November 2026. LEFT OUT AS THURSDAY'S NEWS: the Shenzhen summit and its joint declaration, the World Court's Myanmar genocide ruling, Anthropic's Nasdaq debut, the GTA VI launch and Voyager 1's one-light-day mark (all first reported 19 Nov).",
          (31,953,962,27),'bold',10.5,RED,rows=2)
    block('Claims are attributed, not stated as fact · Pictures and map: original, drawn in code · Sources: Reuters, AP, AFP, BBC, Al Jazeera, UN News, Euronews, Xinhua, SBS, ICC · 2026-11-20',
          (24,991,976,10),'sans',10,GREY)
    output = Path(__file__).resolve().with_name('entry.png')
    image.resize((1024,1024), Image.Resampling.LANCZOS).save(output, optimize=True)
    with Image.open(output) as result:
        assert result.size == (1024,1024) and result.format == 'PNG'
    size = output.stat().st_size
    assert size < 1048576, size
    print(f'entry.png: 1024 × 1024, {size:,} bytes, 37 stories, {len(checked)} text blocks checked')


if __name__ == '__main__':
    render()
