import math

"""
计算两个点之间的距离：L2距离（欧式距离）
"""
def points_distance(x0, y0, x1, y1):
    return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)


"""
计算两条线段之间的夹角，以弧度表示
"""
def compute_angle(x0, y0, x1, y1, x2, y2, x3, y3):
    AB = [x1 - x0, y1 - y0]
    CD = [x3 - x2, y3 - y2]

    dot_product = AB[0] * CD[0] + AB[1] * CD[1]

    AB_distance = points_distance(x0, y0, x1, y1) + 0.001   # 防止分母出现0
    CD_distance = points_distance(x2, y2, x3, y3) + 0.001

    cos_theta = dot_product / (AB_distance * CD_distance)

    theta = math.acos(cos_theta)

    return theta


"""
检测所有手指状态（判断每根手指弯曲 or 伸直）
大拇指只有弯曲和伸直两种状态，其他手指除了弯曲和伸直还包含第三种状态（手指没有伸直，但是也没有达到弯曲的标准），第三种状态是为了后续更新迭代用的，这里用不到
"""
def detect_all_finger_state(all_points):
    finger_first_angle_bend_threshold = math.pi * 0.25  # 大拇指弯曲阈值
    finger_other_angle_bend_threshold = math.pi * 0.5  # 其他手指弯曲阈值
    finger_other_angle_straighten_threshold = math.pi * 0.2  # 其他手指伸直阈值

    first_is_bend = False
    first_is_straighten = False
    second_is_bend = False
    second_is_straighten = False
    third_is_bend = False
    third_is_straighten = False
    fourth_is_bend = False
    fourth_is_straighten = False
    fifth_is_bend = False
    fifth_is_straighten = False

    finger_first_angle = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point1'][0], all_points['point1'][1],
                                       all_points['point2'][0], all_points['point2'][1], all_points['point4'][0], all_points['point4'][1])
    finger_second_angle = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point5'][0], all_points['point5'][1],
                                        all_points['point6'][0], all_points['point6'][1], all_points['point8'][0], all_points['point8'][1])
    finger_third_angle = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point9'][0], all_points['point9'][1],
                                       all_points['point10'][0], all_points['point10'][1], all_points['point12'][0], all_points['point12'][1])
    finger_fourth_angle = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point13'][0], all_points['point13'][1],
                                        all_points['point14'][0], all_points['point14'][1], all_points['point16'][0], all_points['point16'][1])
    finger_fifth_angle = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point17'][0], all_points['point17'][1],
                                       all_points['point18'][0], all_points['point18'][1], all_points['point20'][0], all_points['point20'][1])

    if finger_first_angle > finger_first_angle_bend_threshold:  # 判断大拇指是否弯曲
        first_is_bend = True
        first_is_straighten = False
    else:
        first_is_bend = False
        first_is_straighten = True

    if finger_second_angle > finger_other_angle_bend_threshold:  # 判断食指是否弯曲
        second_is_bend = True
    elif finger_second_angle < finger_other_angle_straighten_threshold:
        second_is_straighten = True
    else:
        second_is_bend = False
        second_is_straighten = False

    if finger_third_angle > finger_other_angle_bend_threshold:  # 判断中指是否弯曲
        third_is_bend = True
    elif finger_third_angle < finger_other_angle_straighten_threshold:
        third_is_straighten = True
    else:
        third_is_bend = False
        third_is_straighten = False

    if finger_fourth_angle > finger_other_angle_bend_threshold:  # 判断无名指是否弯曲
        fourth_is_bend = True
    elif finger_fourth_angle < finger_other_angle_straighten_threshold:
        fourth_is_straighten = True
    else:
        fourth_is_bend = False
        fourth_is_straighten = False

    if finger_fifth_angle > finger_other_angle_bend_threshold:  # 判断小拇指是否弯曲
        fifth_is_bend = True
    elif finger_fifth_angle < finger_other_angle_straighten_threshold:
        fifth_is_straighten = True
    else:
        fifth_is_bend = False
        fifth_is_straighten = False

    # 将手指的弯曲或伸直状态存在字典中，简化后续函数的参数
    bend_states = {'first': first_is_bend, 'second': second_is_bend, 'third': third_is_bend, 'fourth': fourth_is_bend, 'fifth': fifth_is_bend}
    straighten_states = {'first': first_is_straighten, 'second': second_is_straighten, 'third': third_is_straighten, 'fourth': fourth_is_straighten, 'fifth': fifth_is_straighten}

    return bend_states, straighten_states


def judge_Palm_No_Thumb(all_points, bend_states, straighten_states):
    """
    判断是否为 Palm_No_Thumb 手势：大拇指弯曲，其他手指伸直
    """
    if bend_states['first'] and \
       straighten_states['second'] and \
       straighten_states['third'] and \
       straighten_states['fourth'] and \
       straighten_states['fifth']:
        return 'Palm_No_Thumb'
    else:
        return False


"""
判断是否为 OK 手势
"""
def judge_OK(all_points, bend_states, straighten_states):
    angle5_6_and_6_8 = compute_angle(all_points['point5'][0], all_points['point5'][1], all_points['point6'][0], all_points['point6'][1],
                                     all_points['point6'][0], all_points['point6'][1], all_points['point8'][0], all_points['point8'][1])

    if angle5_6_and_6_8 > 0.1 * math.pi and straighten_states['third'] and straighten_states['fourth'] and straighten_states['fifth']:
        distance4_and_8 = points_distance(all_points['point4'][0], all_points['point4'][1], all_points['point8'][0], all_points['point8'][1])
        distance2_and_6 = points_distance(all_points['point2'][0], all_points['point2'][1], all_points['point6'][0], all_points['point6'][1])
        distance4_and_6 = points_distance(all_points['point4'][0], all_points['point4'][1], all_points['point6'][0], all_points['point6'][1])

        if distance4_and_8 < distance2_and_6 and distance4_and_6 > distance4_and_8 and all_points['point11'][1] < all_points['point10'][1]:
            return 'OK'
        else:
            return False
    else:
        return False


"""
判断是否为 Return 手势
"""
def judge_Return(all_points, bend_states, straighten_states):
    angle18_6_and_18_18_ = compute_angle(all_points['point18'][0], all_points['point18'][1], all_points['point6'][0], all_points['point6'][1],
                                         all_points['point18'][0], all_points['point18'][1], all_points['point18'][0] + 10, all_points['point18'][1])
    angle_6_18_and_6_6_ = compute_angle(all_points['point6'][0], all_points['point6'][1], all_points['point18'][0], all_points['point18'][1],
                                         all_points['point6'][0], all_points['point6'][1], all_points['point6'][0] + 10, all_points['point6'][1])
    angle_0_2_and_0_17 = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point2'][0], all_points['point2'][1],
                                       all_points['point0'][0], all_points['point0'][1], all_points['point17'][0], all_points['point17'][1])

    if (bend_states['first'] and bend_states['second'] and bend_states['third'] and bend_states['fourth'] and bend_states['fifth'] and
            angle_0_2_and_0_17 > 0.15 * math.pi and
            all_points['point7'][1] > all_points['point6'][1] and all_points['point11'][1] > all_points['point10'][1] and
            all_points['point15'][1] > all_points['point14'][1] and all_points['point19'][1] > all_points['point18'][1]):

        if angle18_6_and_18_18_ < 0.1 * math.pi or angle_6_18_and_6_6_ < 0.1 * math.pi:
            return 'Return'
        else:
            return False
    else:
        return False


"""
判断是否为 Left 手势
"""
def judge_Left(all_points, bend_states, straighten_states):
    angle5_6_and_6_8 = compute_angle(all_points['point5'][0], all_points['point5'][1], all_points['point6'][0], all_points['point6'][1],
                                     all_points['point6'][0], all_points['point6'][1], all_points['point8'][0], all_points['point8'][1])
    angle9_10_and_10_12 = compute_angle(all_points['point9'][0], all_points['point9'][1], all_points['point10'][0], all_points['point10'][1],
                                        all_points['point10'][0], all_points['point10'][1], all_points['point12'][0], all_points['point12'][1])
    angle13_14_and_14_16 = compute_angle(all_points['point13'][0], all_points['point13'][1], all_points['point14'][0], all_points['point14'][1],
                                         all_points['point14'][0], all_points['point14'][1], all_points['point16'][0], all_points['point16'][1])
    angle17_18_and_18_20 = compute_angle(all_points['point17'][0], all_points['point17'][1], all_points['point18'][0], all_points['point18'][1],
                                         all_points['point18'][0], all_points['point18'][1], all_points['point20'][0], all_points['point20'][1])
    angle0_6_and_0_4 = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point6'][0], all_points['point6'][1],
                                     all_points['point0'][0], all_points['point0'][1], all_points['point4'][0], all_points['point4'][1])
    angle0_5_and_0_17 = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point5'][0], all_points['point5'][1],
                                      all_points['point0'][0], all_points['point0'][1], all_points['point17'][0], all_points['point17'][1])

    if ((straighten_states['first'] and bend_states['second'] and bend_states['third'] and bend_states['fourth'] and bend_states['fifth']) or
        (straighten_states['first'] and angle5_6_and_6_8 > 0.2 * math.pi and angle9_10_and_10_12 > 0.2 * math.pi and
         angle13_14_and_14_16 > 0.2 * math.pi and angle17_18_and_18_20 > 0.2 * math.pi)):

        angle0_0__and_0_4 = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point0'][0] + 10, all_points['point0'][1],
                                          all_points['point0'][0], all_points['point0'][1], all_points['point4'][0], all_points['point4'][1])

        if (angle0_5_and_0_17 > 0.15 * math.pi and angle0_0__and_0_4 > 0.7 * math.pi and all_points['point3'][0] < all_points['point2'][0] and
            angle0_6_and_0_4 > 0.1 * math.pi and all_points['point11'][1] > all_points['point10'][1] and all_points['point7'][1] > all_points['point6'][1] and
            all_points['point15'][1] > all_points['point14'][1] and all_points['point19'][1] > all_points['point18'][1]):
            return 'Left'
        else:
            return False
    else:
        return False


"""
判断是否为 Right 手势
"""
def judge_Right(all_points, bend_states, straighten_states):
    angle0_5_and_0_17 = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point5'][0], all_points['point5'][1],
                                      all_points['point0'][0], all_points['point0'][1], all_points['point17'][0], all_points['point17'][1])
    angle5_6_and_6_8 = compute_angle(all_points['point5'][0], all_points['point5'][1], all_points['point6'][0], all_points['point6'][1],
                                     all_points['point6'][0], all_points['point6'][1], all_points['point8'][0], all_points['point8'][1])
    angle9_10_and_10_12 = compute_angle(all_points['point9'][0], all_points['point9'][1], all_points['point10'][0], all_points['point10'][1],
                                        all_points['point10'][0], all_points['point10'][1], all_points['point12'][0], all_points['point12'][1])
    angle13_14_and_14_16 = compute_angle(all_points['point13'][0], all_points['point13'][1], all_points['point14'][0], all_points['point14'][1],
                                         all_points['point14'][0], all_points['point14'][1], all_points['point16'][0], all_points['point16'][1])
    angle17_18_and_18_20 = compute_angle(all_points['point17'][0], all_points['point17'][1], all_points['point18'][0], all_points['point18'][1],
                                         all_points['point18'][0], all_points['point18'][1], all_points['point20'][0], all_points['point20'][1])
    angle0_6_and_0_4 = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point6'][0], all_points['point6'][1],
                                     all_points['point0'][0], all_points['point0'][1], all_points['point4'][0], all_points['point4'][1])

    if ((straighten_states['first'] and bend_states['second'] and bend_states['third'] and bend_states['fourth'] and bend_states['fifth']) or
        (straighten_states['first'] and angle5_6_and_6_8 > 0.2 * math.pi and angle9_10_and_10_12 > 0.2 * math.pi and
         angle13_14_and_14_16 > 0.2 * math.pi and angle17_18_and_18_20 > 0.2 * math.pi)):

        angle0_0__and_0_4 = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point0'][0] + 10, all_points['point0'][1],
                                          all_points['point0'][0], all_points['point0'][1], all_points['point4'][0], all_points['point4'][1])

        if (angle0_5_and_0_17 > 0.15 * math.pi and angle0_0__and_0_4 < 0.25 * math.pi and all_points['point3'][0] > all_points['point2'][0] and
            angle0_6_and_0_4 > 0.1 * math.pi and all_points['point11'][1] > all_points['point10'][1] and all_points['point7'][1] > all_points['point6'][1] and
            all_points['point15'][1] > all_points['point14'][1] and all_points['point19'][1] > all_points['point18'][1]):
            return 'Right'
        else:
            return False
    else:
        return False


"""
判断是否为 Thumbs_up 手势
"""
def judge_Thumbs_up(all_points, bend_states, straighten_states):
    angle2_4_and_2_8 = compute_angle(all_points['point2'][0], all_points['point2'][1], all_points['point4'][0], all_points['point4'][1],
                                     all_points['point2'][0], all_points['point2'][1], all_points['point8'][0], all_points['point8'][1])
    angle2_3_and_3_4 = compute_angle(all_points['point2'][0], all_points['point2'][1], all_points['point3'][0], all_points['point3'][1],
                                     all_points['point3'][0], all_points['point3'][1], all_points['point4'][0], all_points['point4'][1])
    angle5_6_and_6_8 = compute_angle(all_points['point5'][0], all_points['point5'][1], all_points['point6'][0], all_points['point6'][1],
                                     all_points['point6'][0], all_points['point6'][1], all_points['point8'][0], all_points['point8'][1])
    angle9_10_and_10_12 = compute_angle(all_points['point9'][0], all_points['point9'][1], all_points['point10'][0], all_points['point10'][1],
                                        all_points['point10'][0], all_points['point10'][1], all_points['point12'][0], all_points['point12'][1])
    angle13_14_and_14_16 = compute_angle(all_points['point13'][0], all_points['point13'][1], all_points['point14'][0], all_points['point14'][1],
                                         all_points['point14'][0], all_points['point14'][1], all_points['point16'][0], all_points['point16'][1])
    angle17_18_and_18_20 = compute_angle(all_points['point17'][0], all_points['point17'][1], all_points['point18'][0], all_points['point18'][1],
                                         all_points['point18'][0], all_points['point18'][1], all_points['point20'][0], all_points['point20'][1])
    angle0_6_and_0_4 = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point6'][0], all_points['point6'][1],
                                     all_points['point0'][0], all_points['point0'][1], all_points['point4'][0], all_points['point4'][1])

    if (angle2_3_and_3_4 < 0.2 * math.pi and bend_states['second'] and bend_states['third'] and bend_states['fourth'] and bend_states['fifth']) or (
            angle2_3_and_3_4 < 0.2 * math.pi and angle5_6_and_6_8 > 0.2 * math.pi and angle9_10_and_10_12 > 0.2 * math.pi and angle13_14_and_14_16 > 0.2 * math.pi and angle17_18_and_18_20 > 0.2 * math.pi):

        angle0_0__and_0_4 = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point0'][0] + 10, all_points['point0'][1],
                                          all_points['point0'][0], all_points['point0'][1], all_points['point4'][0], all_points['point4'][1])

        if angle0_0__and_0_4 > 0.25 * math.pi and angle0_0__and_0_4 < 0.75 * math.pi and all_points['point3'][1] > all_points['point4'][1] and all_points['point5'][1] < all_points['point9'][1] and all_points['point9'][1] < all_points['point13'][1] and all_points['point13'][1] < all_points['point17'][1] and all_points['point2'][1] < all_points['point5'][1] and angle0_6_and_0_4 > 0.1 * math.pi and angle2_4_and_2_8 > 0.1 * math.pi:
            return 'Thumbs_up'
        else:
            return False
    else:
        return False


"""
判断是否为 Pause 手势
"""
# def judge_Pause(all_points, bend_states, straighten_states):
def judge_Rotation(all_points, bend_states, straighten_states):
    angle0_5_and_0_17 = compute_angle(all_points['point0'][0], all_points['point0'][1], all_points['point5'][0], all_points['point5'][1],
                                      all_points['point0'][0], all_points['point0'][1], all_points['point17'][0], all_points['point17'][1])
    angle2_3_and_2_4 = compute_angle(all_points['point2'][0], all_points['point2'][1], all_points['point3'][0], all_points['point3'][1],
                                      all_points['point2'][0], all_points['point2'][1], all_points['point4'][0], all_points['point4'][1])
    angle5_6_and_6_8 = compute_angle(all_points['point5'][0], all_points['point5'][1], all_points['point6'][0], all_points['point6'][1],
                                      all_points['point6'][0], all_points['point6'][1], all_points['point8'][0], all_points['point8'][1])
    angle9_10_and_10_12 = compute_angle(all_points['point9'][0], all_points['point9'][1], all_points['point10'][0], all_points['point10'][1],
                                         all_points['point10'][0], all_points['point10'][1], all_points['point12'][0], all_points['point12'][1])
    angle13_14_and_14_16 = compute_angle(all_points['point13'][0], all_points['point13'][1], all_points['point14'][0], all_points['point14'][1],
                                         all_points['point14'][0], all_points['point14'][1], all_points['point16'][0], all_points['point16'][1])
    angle17_18_and_18_20 = compute_angle(all_points['point17'][0], all_points['point17'][1], all_points['point18'][0], all_points['point18'][1],
                                         all_points['point18'][0], all_points['point18'][1], all_points['point20'][0], all_points['point20'][1])
    angle1_2_and_2_4 = compute_angle(all_points['point1'][0], all_points['point1'][1], all_points['point2'][0], all_points['point2'][1],
                                     all_points['point2'][0], all_points['point2'][1], all_points['point4'][0], all_points['point4'][1])

    if angle2_3_and_2_4 < 0.2 * math.pi and angle5_6_and_6_8 < 0.07 * math.pi and angle9_10_and_10_12 < 0.07 * math.pi and angle13_14_and_14_16 < 0.07 * math.pi and angle17_18_and_18_20 < 0.07 * math.pi and angle9_10_and_10_12 < 0.07 * math.pi and angle1_2_and_2_4 < 0.25 * math.pi:
        if angle0_5_and_0_17 > 0.1 * math.pi and all_points['point3'][1] > all_points['point4'][1] and all_points['point6'][1] > all_points['point8'][1] and all_points['point10'][1] > all_points['point12'][1]:
            # return 'Pause'
            return 'Rotation'
        else:
            return False
    else:
        return False

def judge_Thumbs_Down(all_points, bend_states, straighten_states):
    # 检查拇指是否伸直
    if not straighten_states['first']:
        return False

    # 检查其他手指是否弯曲（根据需求可选）
    # if not (bend_states['second'] and bend_states['third'] and bend_states['fourth'] and bend_states['fifth']):
    #     return False

    # 计算垂直方向的角度（手腕到拇指尖与垂直向下方向的夹角）
    vertical_angle = compute_angle(
        all_points['point0'][0], all_points['point0'][1],  # 手腕点
        all_points['point0'][0], all_points['point0'][1] + 1,  # 垂直向下方向
        all_points['point0'][0], all_points['point0'][1],  # 手腕点
        all_points['point4'][0], all_points['point4'][1]   # 拇指尖
    )

    # 角度阈值（30度）
    if vertical_angle > math.pi/6:
        return False

    # 检查拇指尖在手腕下方（假设y轴向下增大）
    if all_points['point4'][1] <= all_points['point0'][1]:
        return False

    # 检查拇指长度（防止误判小幅度动作）
    thumb_length = points_distance(all_points['point0'][0], all_points['point0'][1],
                                   all_points['point4'][0], all_points['point4'][1])
    if thumb_length < 0.15:  # 根据实际场景调整阈值
        return False

    return 'Thumbs_Down'


"""
检测当前手势，返回当前手势
"""
def detect_hand_state(all_points, bend_states, straighten_states):
    state_OK = judge_OK(all_points, bend_states, straighten_states)
    state_Return = judge_Return(all_points, bend_states, straighten_states)
    state_Left = judge_Left(all_points, bend_states, straighten_states)
    state_Right = judge_Right(all_points, bend_states, straighten_states)
    state_Thumbs_up = judge_Thumbs_up(all_points, bend_states, straighten_states)
    # state_Pause = judge_Pause(all_points, bend_states, straighten_states)
    state_Rotation = judge_Rotation(all_points, bend_states, straighten_states)
    state_Thumbs_down =judge_Thumbs_Down(all_points, bend_states, straighten_states)
    state_Palm_No_Thumb = judge_Palm_No_Thumb(all_points, bend_states, straighten_states)


    if state_OK == 'OK':
        return 'OK'
    elif state_Return == 'Return':
        return 'Return'
    elif state_Left == 'Left':
        return 'Left'
    elif state_Right == 'Right':
        return 'Right'
    elif state_Thumbs_up == 'Thumbs_up':
        return 'Thumbs_up'
    # elif state_Pause == 'Pause':
    elif state_Rotation == 'Rotation':
        # return 'Pause'
        return 'Rotation'
    elif state_Thumbs_down == 'Thumbs_Down':
        return 'Thumbs_Down'
    elif state_Palm_No_Thumb == 'Palm_No_Thumb':
        return 'Palm_No_Thumb'
    else:
        return 'None'


