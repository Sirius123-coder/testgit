from tkinter import *
from tkinter.messagebox import *
import copy
from pygame import mixer

root = Tk()
root.title(" 推箱子")

imgs = [PhotoImage(file='bmp\\Wall.gif'),
        PhotoImage(file='bmp\\Worker.gif'),
        PhotoImage(file='bmp\\Box.gif'),
        PhotoImage(file='bmp\\Passageway.gif'),
        PhotoImage(file='bmp\\Destination.gif'),
        PhotoImage(file='bmp\\WorkerInDest.gif'),
        PhotoImage(file='bmp\\RedBox.gif'),
        PhotoImage(file='bmp\\Box_Worker.gif'),
        PhotoImage(file='bmp\\succeed.gif'),
        PhotoImage(file='bmp\\background.gif')]
print(imgs)

back=1
# 步数
Steps = 0
#路径
paths = 0
#模式
model = 0
# 0代表墙，1代表人，2代表箱子，3代表路，4代表目的地
# 5代表人在目的地，6代表放到目的地的箱子,7穿越箱子时的状态
# 8代表游戏结束图片
Wall = 0
Worker = 1
Box = 2
Passageway = 3
Destination = 4
WorkerInDest = 5
RedBox = 6
Box_Worker = 7  # 穿越箱子时的状态
level = 0  # 当前关卡
totle_level = 20  # 默认关卡数20

#最短路径
class Shortestpath:
    def __init__(self, line, col=10):
        """
        给一个图，长度为100的字符串表示。
        0代表墙，1代表人，2代表箱子，3代表路，4代表目的地
        :param line: 地图，用字符串表示
        :param col: 地图的长宽，设定为10*10
        """

        self.line = line
        # sta和en 表示开始的状态，结束的状态
        # sta只有2,1,0 2表示箱子开始位置,1表示人的位置,0表示其他。
        # en只有1,4,0 1表示墙,3表示箱子目的地,0表示其他。
        # 现在只需要把sta状态中的2位置移动到en的4的位置即满足条件
        self.sta = ''
        self.en = ''
        self.col = col
        # px, py表示4的位置
        self.px, self.py = -1, -1
        # paths记录最短路径（可能有多条）
        self.paths = []
        # len记录最短路径长度 如
        self.len = -1

        self.pre()
        self.BFS()
        print(self.paths)

    def pre(self):
        """
        1.获得sta开始状态和en结束状态
        2.获得人的起始位置px,py
        代码最后的第一关的地图可视化为
        1111111111
        1111111111
        1110001111
        1110221111
        1114201111
        1111100111
        1111300111
        1113300111
        1111111111
        1111111111
        :return:
        """
        mp = []
        for pos in range(0, 100, 10):
            mp.append(self.line[pos:pos + 10])
        # print(self.line)
        # for x in mp:
        #     print(x)

        for pos, enum in enumerate(self.line):
            cx, cy = pos // 10, pos % 10
            if enum == '1' or enum == '5':
                self.px, self.py = cx, cy
                break

        # 现在只需要把sta开始的状态中的2位置移动到en的4的位置即满足条件

        # 推箱子程序中：0代表墙，1代表人，2代表箱子，3代表路，4代表目的地, 5代表人在目的地
        staDic = {'0': '0', '1': '1', '2': '2', '3': '0', '4': '0', '5': '5', '6':'0'}
        enDic = {'0': '9', '1': '0', '2': '0', '3': '0', '4': '4', '5': '6', '6':'0'}
        for x in self.line:
            self.sta += staDic[x]
            self.en += enDic[x]
        # print(self.sta)
        # print(self.en)

    def is_ok(self, sta):
        """
        sta状态中的2位置移动到en的4的位置。
        :param sta:
        :return:
        """
        for s, e in zip(sta, self.en):
            if e == '4' and s != '2':
                return False
            if e == '6' and s != '2':
                return False
        return True

    def BFS(self):
        """
        BFS获得最短路径保存到paths中
        :return:
        """
        # 4个方向，小写代表只是人移动，大写表示人推着箱子一起移动
        dirs = [[-1, 0, 'l', 'L'], [1, 0, 'r', 'R'], [0, 1, 'd', 'D'], [0, -1, 'u', 'U']]
        # 把开始的状态进入队列(list模拟)，状态包括字符串表示的当前状态、当前的路径、当前人的位置
        states = [[self.sta, '', self.px, self.py]]
        # 访问数组(dict模拟)，访问过的状态（字符串）不再访问
        visi = {}
        visi[self.sta] = 1

        s_len = 1000
        while len(states) > 0:
            sta, path, px, py = states[0]
            # 1状态的位置
            ppos = px * self.col + py
            states = states[1:]
            if len(path) > s_len:
                break
            # 保存最短路径到paths中
            if self.is_ok(sta):
                if self.len == -1 or len(path) == self.len:
                    self.paths.append(path)
                    self.len = len(path)
                continue

            for dir in dirs:

                #当前位置
                curpos = px * self.col + py

                cx, cy = px + dir[0], py + dir[1]
                # 4挨着的状态的位置
                pos = cx * self.col + cy

                nx, ny = px + 2 * dir[0], py + 2 * dir[1]
                # 4挨着挨着的状态的位置
                npos = nx * self.col + ny
                if not (nx >= 0 and nx < self.col and ny >= 0 and ny < self.col):
                    continue
                # python中字符串不可更改，于是把字符串变成list更改状态后再转换为字符串
                if sta[pos] == '2' and sta[npos] == '0' and self.en[npos] != '9':
                    # 人和箱子一起推动，sta中连着的状态为1 2 0，en中第三个不能为1。推完之后sta变为0 1 2
                    digits = [int(x) for x in sta]
                    digits[ppos], digits[pos], digits[npos] = 0, 1, 2
                    new_sta = ''.join(str(x) for x in digits)
                    if new_sta not in visi:
                        visi[new_sta] = 1
                        states.append([new_sta, path + dir[3], cx, cy])
                elif sta[pos] == '0' and self.en[pos] != '9':
                    # 人动箱子不动，sta中连着的状态为1 0，en中第二个不能为1。
                    digits = [int(x) for x in sta]
                    digits[ppos], digits[pos] = 0, 1
                    new_sta = ''.join(str(x) for x in digits)
                    if new_sta not in visi:
                        visi[new_sta] = 1
                        states.append([new_sta, path + dir[2], cx, cy])
                elif sta[curpos] == '5' and sta[pos] == '2' and sta[npos] == '0' and self.en[npos] != '9':
                    # 人和箱子一起推动，sta中连着的状态为5 2 0，en中第三个不能为1。推完之后sta变为0 5 2
                    digits = [int(x) for x in sta]
                    digits[ppos], digits[pos], digits[npos] = 0, 5, 2
                    new_sta = ''.join(str(x) for x in digits)
                    if new_sta not in visi:
                        visi[new_sta] = 1
                        states.append([new_sta, path + dir[3], cx, cy])
                elif sta[curpos] == '5' and sta[pos] == '0' and self.en[pos] != '9':
                    # 人动箱子不动，sta中连着的状态为5 0，en中第二个不能为1。
                    digits = [int(x) for x in sta]
                    digits[ppos], digits[pos] = 0, 5
                    new_sta = ''.join(str(x) for x in digits)
                    if new_sta not in visi:
                        visi[new_sta] = 1
                        states.append([new_sta, path + dir[2], cx, cy])




maplist = [[[] for i in range(10)] for i in range(30)]  # 10*10的地图，可容纳关卡数为30


# 读取地图
def Read_list():
    global totle_level
    file1 = open("关卡.txt", "r")
    list_row = file1.readlines()
    list_source = []
    for i in range(len(list_row)):
        column_list = list_row[i].strip().split(",")  # 每一行split后是一个列表
        list_source.append(column_list)  # 在末尾追加到list_source
    totle_level = len(list_source)
    print("关卡数据读取", list_source)
    for i in range(len(list_source)):  # 行数
        for j in range(len(list_source[i])):  # 列数
            list_source[i][j] = int(list_source[i][j])  # 关卡中的数据存储到二维列表中
    print("关卡数据读取转化为int型", list_source)
    print("总关卡数", totle_level)
    for i in range(len(list_source)):  # 行数
        for j in range(len(list_source[i])):  # 列数
            k = int(j / 10)
            maplist[i][k].append(list_source[i][j])  # 将二维列表转化为地图的三维列表
    print("三维地图列表maplist", maplist)
    file1.close()
    return list_source


# -----------------------------------------------------

# 绘制整个游戏区域图形
def drawGameImage():
    global x, y
    cv.delete("all")
    for i in range(0, len(myArray)):  # 0--9
        for j in range(0, len(myArray[0])):  # 0--9
            if myArray[i][j] == Worker:
                x = i  # 工人当前位置(x,y)
                y = j
                print("工人当前位置:", x, y)
            img1 = imgs[myArray[i][j]]
            cv.create_image((i * 32 + 20, j * 32 + 20), image=img1)
            cv.pack()


# -----------------------------------------------------
#提示最短完整路线
def recommend():
    global x, y, myArray
    str1 = ""
    for i in range(0, len(myArray)):
        str1 = str1 + ''.join([str(x) for x in myArray[i]])
    print("str1:", str1)
    print("最佳路线:")
    gs = Shortestpath(str1)
    if len(gs.paths):
        paths = gs.paths[0]
        print("paths",paths)
        p['text'] = str(paths)
        p.update()
        dir = gs.paths[0][0]
        if dir == 'l' or dir == 'L':
            showinfo(title="提示", message="向左走")
        elif dir == 'r' or dir == 'R':
            showinfo(title="提示", message="向右走")
        elif dir == 'u' or dir == 'U':
            showinfo(title="提示", message="向上走")
        elif dir == 'd' or dir == 'D':
            showinfo(title="提示", message="向下走")
    else:
        showinfo(title="提示", message="没救了")
        return


# -----------------------------------------------------
#按照最短路线自动寻路
def Auto_navigation():
    global x, y, myArray
    str1 = ""
    for i in range(0, len(myArray)):
        str1 = str1 + ''.join([str(x) for x in myArray[i]])
    print("str1:", str1)
    print("最佳路线:")
    gs = Shortestpath(str1)

    if len(gs.paths):
        auto = len(gs.paths[0])
        while auto:
            dir = gs.paths[0][len(gs.paths[0]) - auto]
            if dir == 'l' or dir == 'L':
                print("向左走")
                x1 = x - 1;
                y1 = y;
                x2 = x - 2;
                y2 = y;
                MoveTo(x1, y1, x2, y2);
            elif dir == 'r' or dir == 'R':
                print("向右走")
                x1 = x + 1;
                y1 = y;
                x2 = x + 2;
                y2 = y;
                MoveTo(x1, y1, x2, y2);
            elif dir == 'u' or dir == 'U':
                print("向上走")
                x1 = x;
                y1 = y - 1;
                x2 = x;
                y2 = y - 2;
                MoveTo(x1, y1, x2, y2);
            elif dir == 'd' or dir == 'D':
                print("向下走")
                x1 = x;
                y1 = y + 1;
                x2 = x;
                y2 = y + 2;
                MoveTo(x1, y1, x2, y2);
            auto -= 1
        print("最佳路径的步数", len(gs.paths[0]))

    else:
        showinfo(title="提示", message="没救了")

# -----------------------------------------------------
# 按键处理
def callback(event):
    global x, y, myArray, myArray2, level, totle_level, Steps,back

    print("按下键：", event.char)
    KeyCode = event.keysym
    if KeyCode != "b":  # 按键不为退一步时,记录上一步的状态
        myArray2 = copy.deepcopy(myArray)

    #娱乐模式可穿越箱子
    if model == 1:
        if KeyCode == "w":
            x1 = x;
            y1 = y - 1;
            x2 = x;
            y2 = y - 2;
            # 将所有位置输入以判断并作地图更新
            Through(x1, y1, x2, y2);
        # 向下
        elif KeyCode == "s":
            x1 = x;
            y1 = y + 1;
            x2 = x;
            y2 = y + 2;
            Through(x1, y1, x2, y2);
        # 向左
        elif KeyCode == "a":
            x1 = x - 1;
            y1 = y;
            x2 = x - 2;
            y2 = y;
            Through(x1, y1, x2, y2);
        # 向右
        elif KeyCode == "d":
            x1 = x + 1;
            y1 = y;
            x2 = x + 2;
            y2 = y;
            Through(x1, y1, x2, y2);
    # 工人当前位置(x,y)
    if KeyCode == "Up":  # 分析按键消息
        # 向上
        x1 = x;
        y1 = y - 1;
        x2 = x;
        y2 = y - 2;
        # 将所有位置输入以判断并作地图更新
        MoveTo(x1, y1, x2, y2);

    # 向下
    elif KeyCode == "Down":
        x1 = x;
        y1 = y + 1;
        x2 = x;
        y2 = y + 2;
        MoveTo(x1, y1, x2, y2);
    # 向左
    elif KeyCode == "Left":
        x1 = x - 1;
        y1 = y;
        x2 = x - 2;
        y2 = y;
        MoveTo(x1, y1, x2, y2);
    # 向右
    elif KeyCode == "Right":
        x1 = x + 1;
        y1 = y;
        x2 = x + 2;
        y2 = y;
        MoveTo(x1, y1, x2, y2);

    elif KeyCode == "space":  # 空格键
        print("按下键：空格", event.char)
        Steps = 0
        s['text'] = "步数：" + str(Steps)
        s.update()
        clear_map()
        myArray = copy.deepcopy(myArray1)  # 恢复原始地图
        drawGameImage()

    # 下一关
    elif KeyCode == "n":
        print("按下键：n", event.char)
        next_level()
        print("level", level)
        print("totle_level", totle_level)
        if level == totle_level:
            s.pack_forget()
            b.pack_forget()
            b2.pack_forget()
            p.pack_forget()
            l['text'] = ("第", level + 1, "关暂未更新,敬请期待...")
            l.update()
            img1 = imgs[8]
            cv.create_image((0 * 350 + 170, 0 * 350 + 160), image=img1)
            cv.pack()
            showinfo(title="提示", message=" 游戏结束")


    # 退一步
    elif KeyCode == "b"and back==1:
        print("按下键：b", event.char)
        clear_map()
        myArray = copy.deepcopy(myArray2)
        drawGameImage()


# -----------------------------------------------------

# 判断是否在游戏区域
def IsInGameArea(row, col):
    return (row >= 0 and row < len(myArray) and col >= 0 and col < len(myArray[0]))


# -----------------------------------------------------
#移动玩家具体实现
def MoveTo(x1, y1, x2, y2):
    global x, y, Steps
    P1 = None
    P2 = None

    if IsInGameArea(x1, y1):  # 判断是否在游戏区域
        P1 = myArray[x1][y1];
    if IsInGameArea(x2, y2):
        P2 = myArray[x2][y2]
    if P1 == Passageway:  # P1处为通道
        MoveMan(x, y);  # 人原来的位置信息更新
        x = x1;
        y = y1;
        myArray[x1][y1] = Worker;  # 人新的位置信息更新
    if P1 == Destination:  # P1处为目的地
        MoveMan(x, y);
        x = x1;
        y = y1;
        myArray[x1][y1] = WorkerInDest;
    if P1 == Wall or not IsInGameArea(x1, y1):
        # P1处为墙或出界
        return;

    # 以下P1处为箱子
    if P1 == Box:  # P1处为箱子
        if P2 == Wall or not IsInGameArea(x1, y1) or P2 == Box:  ##P2处为墙或出界
            return;

    # P1处为箱子,P2处为通道
    if P1 == Box and P2 == Passageway:
        MoveMan(x, y);
        x = x1;
        y = y1;
        myArray[x2][y2] = Box;
        myArray[x1][y1] = Worker;
    if P1 == Box and P2 == Destination:
        MoveMan(x, y);
        x = x1;
        y = y1;
        myArray[x2][y2] = RedBox;
        myArray[x1][y1] = Worker;
    # P1处为放到目的地的箱子,P2处为通道
    if P1 == RedBox and P2 == Passageway:
        MoveMan(x, y);
        x = x1;
        y = y1;
        myArray[x2][y2] = Box;
        myArray[x1][y1] = WorkerInDest;
    # P1处为放到目的地的箱子,P2处为目的地
    if P1 == RedBox and P2 == Destination:
        MoveMan(x, y);
        x = x1;
        y = y1;
        myArray[x2][y2] = RedBox;
        myArray[x1][y1] = WorkerInDest;
    Steps += 1
    s['text'] = "步数：" + str(Steps)
    s.update()
    drawGameImage()
    # 这里要验证是否过关
    if IsFinish():
        if Isgameover():
            return
        showinfo(title="提示", message=" 恭喜你顺利过关")
        print("下一关")
        next_level()


# -----------------------------------------------------

# 翻越箱子
def Through(x1, y1, x2, y2):
    global x, y
    P1 = None
    if IsInGameArea(x1, y1):  # 判断是否在游戏区域
        P1 = myArray[x1][y1];
    # P1处为箱子
    if P1 == Box:
        MoveMan(x, y);
        x = x1;
        y = y1;
        myArray[x1][y1] = Box_Worker;
    if P1 == Passageway and myArray[x][y] == Box_Worker:
        myArray[x][y] = Box;
        MoveMan(x, y);
        x = x1;
        y = y1;
        myArray[x1][y1] = Worker;
    if P1 == Destination and myArray[x][y] == Box_Worker:
        myArray[x][y] = Box;
        MoveMan(x, y);
        x = x1;
        y = y1;
        myArray[x1][y1] = WorkerInDest;
    drawGameImage()


# -----------------------------------------------------
#移动玩家
def MoveMan(x, y):
    if myArray[x][y] == Worker:
        myArray[x][y] = Passageway;
    elif myArray[x][y] == WorkerInDest:
        myArray[x][y] = Destination;
    elif myArray[x][y] == Box_Worker:
        myArray[x][y] = Box;


# -----------------------------------------------------
#判断当前关卡是否完成
def IsFinish():  # 验证是否过关
    bFinish = True;
    for i in range(0, len(myArray)):  # 0--10
        for j in range(0, len(myArray[0])):  # 0--10
            if (myArray[i][j] == Destination
                    or myArray[i][j] == WorkerInDest):
                bFinish = False;
    return bFinish;


# -----------------------------------------------------
#判断关卡是否为最后一关
def Isgameover():
    global level, totle_level
    if level == totle_level - 1:

        showinfo(title="提示", message=" 游戏结束")
        img1 = imgs[8]
        cv.create_image((0 * 350 + 170, 0 * 350 + 160), image=img1)
        cv.pack()
        s.pack_forget()
        b.pack_forget()
        b2.pack_forget()
        p.pack_forget()
        l['text'] = ("第", level + 2, "关暂未更新,敬请期待...")
        l.update()
        return True
    return False


# -----------------------------------------------------

# 输出map地图
def print_map():
    for i in range(0, 15):  # 0--14
        for j in range(0, 15):  # 0--14
            print(map[i][j], end=' ')
        print('w')


# -----------------------------------------------------
#用“路”清除地图
def clear_map():
    for i in range(0, len(myArray)):  # 0--10
        for j in range(0, len(myArray[0])):  # 0--10
            img1 = imgs[3]
            cv.create_image((i * 32 + 20, j * 32 + 20), image=img1)
            cv.pack()


# -----------------------------------------------------
#绘制下一关地图
def next_level():
    global myArray, level, myArray1, Steps
    Steps = 0
    s['text'] ="步数："+str(Steps)
    s.update()
    p['text'] = str("")
    p.update()
    level += 1
    l['text'] = ("第", level + 1, "关")
    l.update()
    clear_map()
    myArray1 = maplist[level]
    myArray = copy.deepcopy(myArray1)
    drawGameImage()
# -----------------------------------------------------

#退出到主界面时初始化信息，以便后续再次进行游戏
def game_init():
    global myArray, level, myArray1, myArray2, Steps, model, level, paths
    level = 0
    myArray1 = maplist[level]
    myArray = []
    myArray = copy.deepcopy(myArray1)
    myArray2 = []
    myArray2 = copy.deepcopy(myArray1)
    model = 0
    Steps = 0
    paths = ""
    s['text'] ="步数："+str(Steps)
    s.update()
    p['text'] = str("")
    p.update()
    l['text'] = ("第", level + 1, "关")
    l.update()

# -----------------------------------------------------

#正常模式
def Model1():
    global back
    back=1
    clear_map()
    drawGameImage()

    head.pack_forget()
    foot.pack_forget()
    tip.pack_forget()

    s.pack(fill=Y, expand=1, side=LEFT)
    l.pack(fill=Y, expand=1, side=LEFT)
    e.pack(fill=Y, expand=1, side=LEFT)

    cv.pack()

    b.pack(fill=Y, expand=1, side=RIGHT)
    b2.pack(fill=Y, expand=1, side=RIGHT)

    p.pack(fill=Y, side=BOTTOM)

    model1.pack_forget()
    model2.pack_forget()

# -----------------------------------------------------

#娱乐模式
def Model2():
    global model,back
    back = 0
    model = 1
    clear_map()
    drawGameImage()

    head.pack_forget()
    foot.pack_forget()

    s.pack(fill=Y, expand=1, side=LEFT)
    l.pack(fill=Y, expand=1, side=LEFT)
    e.pack(fill=Y, expand=1, side=LEFT)

    cv.pack(fill=Y, expand=1, side=LEFT)

    tip.pack(fill=X, expand=1, side=LEFT)

    model1.pack_forget()
    model2.pack_forget()
# -----------------------------------------------------

#退出到主菜单，隐藏标签、按钮等并重新绘制初始界面
def tuichu():
    clear_map()
    game_init()
    s.pack_forget()
    l.pack_forget()
    e.pack_forget()
    b.pack_forget()
    b2.pack_forget()
    p.pack_forget()
    tip.pack_forget()

    cv.create_image((0 * 350 + 170, 0 * 350 + 160), image=img1)
    cv.pack()
    cv.create_window(163, 50, window=Title)
    cv.create_window(163, 130, window=model1)
    cv.create_window(163, 200, window=model2)
    cv.create_window(163, 270, window=over)

#退出游戏回到主菜单
def exit_game():
    global level, totle_level
    if level == totle_level:
        tuichu()
        return
    flag = askokcancel('退出', '退出会丢失所有数据，确定退出吗？')
    if flag:
        tuichu()
    else:
        return
# -----------------------------------------------------

#结束游戏
def quit_game():
    root.quit()



fm1=Frame(root,bg='#f3e4bb')
fm1.pack(fill=X, side=TOP, expand=1)
fm2=Frame(root,bg='#f3e4bb')
fm2.pack(fill=X, expand=1)
fm3=Frame(root, bg='#f3e4bb')
fm3.pack(fill=X, expand=1)
fm4=Frame(root, bg='#f3e4bb')
fm4.pack(fill=X, side=BOTTOM, expand=1)

head = Label(fm1,bg='#f3e4bb',height=2)
head.pack()
foot = Label(fm4,bg='#f3e4bb',height=4)
foot.pack()

# 显示关卡标签
l = Label(fm1,bg='#f3e4bb',font=("华文行楷", 16), fg='blue', text=("第", level + 1, "关"))
# 显示步数标签
s = Label(fm1,bg='#f3e4bb',fg='blue', font=("华文行楷", 16), text="步数："+str(Steps))
# 退出按钮
e = Button(fm1,bg='#f3e4bb', fg='blue', text='退出', font=("华文行楷", 16), width=4, command=exit_game)

#游戏画布
cv = Canvas(fm2, bg='green', width=326, height=326)

# 提示按钮
b = Button(fm3,bg='#f3e4bb', fg='blue', text='提示', font=("华文行楷", 16), width=4, command=recommend)
# 自动导航按钮
b2 = Button(fm3,bg='#f3e4bb',fg='blue', text='自动寻路', font=("华文行楷", 16), width=8, command=Auto_navigation)
# 显示路径标签
p = Label(fm4,bg='#f3e4bb', fg='green', font=("宋体", 16), wraplength=260, text=str(paths))

# 显示娱乐模式标签
tip = Label(fm3,bg='#f3e4bb', fg='green', font=("宋体", 10), text="tips:碰到箱子时，按wsad可翻越箱子,本模式禁用悔步")

#读取地图
list = Read_list()
myArray1 = maplist[level]
myArray = []
myArray = copy.deepcopy(myArray1)
myArray2 = []
myArray2 = copy.deepcopy(myArray1)
print("长", len(myArray))
print("宽", len(myArray[0]))

#----------------------------------
Title = Label(root, bg='#f3e4bb', font=('华文行楷', 30), width=16, text='推箱子小游戏')
model1 = Button(bg='#f3e4bb', text='正常模式', font=("华文行楷", 20), width=8, command=Model1)
model2 = Button(bg='#f3e4bb', text='娱乐模式', font=("华文行楷", 20), width=8, command=Model2)
over = Button(bg='#f3e4bb', text='退出游戏', font=("华文行楷", 20), width=8, command=quit_game)

img1 = imgs[9]
cv.create_image((0 * 350 + 170, 0 * 350 + 160), image=img1)
cv.pack()

cv.create_window(163, 50, window=Title)
cv.create_window(163, 130, window=model1)
cv.create_window(163, 200, window=model2)
cv.create_window(163, 270, window=over)


# 播放背景音乐
mixer.init()
mixer.music.load('bgm.mp3')  # 加载音乐
mixer.music.play(loops=20, start=69)  # 播放音乐，歌曲播放完20次后会自动停止

cv.bind("<KeyPress>", callback)
cv.focus_set()  # 将焦点设置到cv上


root.mainloop()
