from math import log, exp, sqrt, tan
import time

PI = 3.1415
c = - 1 / (1495 * 0.0039) * exp(-0.0039 * 100) - log(0.850)   # 常数项


def from_p_to_density(p):
    """
    通过 压强p 计算 密度 density
    :param p: 压强
    :return: 密度 density
    """
    density = exp(exp(-0.0039 * p) / (-1495 * 0.0039) - c)
    return density

def from_density_to_p(density):
    """
    通过 密度density 计算 压强p
    :param density: 密度
    :return: 压强p
    """
    p = log((log(density) + c) * (-1495 * 0.0039)) / -0.0039
    return p

def get_init_V_pump(V_surplus=20, d=5, h_max=4.826):
    """
    获得高压油泵的初始体积
    :param V_surplus: 残余容积
    :param d: 泵的直径
    :param h_max: 凸轮能抬高柱塞的最大高度
    :return: 油泵的初始体积
    """
    V = V_surplus + h_max * PI * pow(d / 2, 2)
    return V

def from_angle_to_h(angle):
    """
    有角度得到柱塞的高度
    :param angle: 角度
    :return: 柱塞的高度
    """
    h = -0.558 * pow(angle, 2) + 3.503 * angle + 1.161
    return h

def get_h_of_valve(t):
    """
    当前时间针阀的升程
    :param t: 当前时间
    :return: 针阀的升程
    """
    h = 0.0
    if t > 50:
        t -= 50
    if 0 < t <= 0.44:
        h = 16.367 * pow(t, 2) - 2.274 * t + 0.044
    elif 0.44 < t <= 2.0:
        h = 2
    elif 2.0 < t <= 2.44:
        h = 16.402 * pow(t, 2) - 78.071 * t + 92.863
    return h

def get_mass_pump_to_tube(density_pumb, p_from, p_to, dt, d=1.4, C=0.85):
    """
    从油泵转移到油管的油的质量
    :param density_pumb: 油泵处的密度
    :param p_from: 油泵处的压强
    :param p_to: 油管处的压强
    :param dt: 极短的时间
    :param d: A小孔的直径
    :param C: 流量系数
    :return: 油泵转移到油管的油的质量
    """
    A = PI * pow(d/2, 2)
    delta_p = p_from - p_to
    Q = C * A * sqrt(2 * delta_p / density_pumb)
    m = Q * dt * density_pumb
    return m

def get_mass_tube_to_out(density_tube, p_from, p_to, t, dt, C=0.85):
    """
    从油管转移到外部的油的质量
    :param density_tube: 油管处的密度
    :param p_from: 油管处的压强
    :param p_to: 外部的压强
    :param t: 当前时间
    :param dt: 极短的时间
    :param C: 流量系数
    :return: 从油管转移到外部的油的质量
    """
    h = get_h_of_valve(t)
    A = PI * (pow((h + 1.25 / tan(PI/20)) * tan(PI/20), 2) - pow(1.25, 2))
    delta_p = p_from - p_to
    Q = C * A * sqrt(2 * delta_p / density_tube)
    m = Q * dt * density_tube
    return m

def main(interval_length=0.000001, max_angular_velocity=0.1, dt=0.0001, iteration_time=500):
    """
    获得一个时间区间，角速度的值便在区间之中
    :param interval_length: 容忍的最小区间长度（误差容忍度）
    :param max_angular_velocity: 最大的转速
    :param dt: 极短的时间
    :param iteration_time: 进行迭代的时间的长度
    :return: 一个时间区间，角速度的值便在区间之中
    """
    left, right = 0.0, max_angular_velocity
    p_tube = 100
    V_tube = PI * pow(10/2, 2) * 500

    while (left + interval_length < right):
        angular_velocity  = left + (right - left) / 2
        print("test {}".format(angular_velocity))
        t = 0.0
        angle = 0.0
        increase_angle = angular_velocity * dt

        V_pump = get_init_V_pump()
        p_pump = 0.5
        density_pump = from_p_to_density(p_pump)
        m_pump = V_pump * density_pump

        p_tube = 100
        density_tube = 0.850
        m_tube = V_tube * density_tube
        m_tube_sum = 0.0

        while (t < iteration_time):
            t = t + dt
            angle += increase_angle
            delta_h = from_angle_to_h(angle) - from_angle_to_h(angle - increase_angle)
            V_pump = V_pump - delta_h * PI * pow(5 / 2, 2)
            density_pump = m_pump / V_pump
            p_pump = from_density_to_p(density_pump)

            if angle >= 6.28: # 补充燃油
                angle = 0.0
                p_pump = 0.5
                V_pump = get_init_V_pump()
                density_pump = from_p_to_density(p_pump)
                m_pump = density_pump * V_pump

            if p_pump > p_tube:
                m_pump_to_tube = get_mass_pump_to_tube(density_pump, p_pump, p_tube, dt)
                m_pump -= m_pump_to_tube
                density_pump = m_pump / V_pump
                m_tube = m_tube + m_pump_to_tube

            m_tube_to_out = get_mass_tube_to_out(density_tube, p_tube, 0.5, t, dt)
            m_tube -= m_tube_to_out
            density_tube = m_tube / V_tube
            p_tube = from_density_to_p(density_tube)
            m_tube_sum += m_tube

        print("p = {}".format(p_tube))
        m_tube_mean = m_tube_sum / (iteration_time / dt)
        if m_tube_mean <= 0.850 * V_tube:
            left = angular_velocity
        else:
            right = angular_velocity

    print("最后的压强值： {}".format(p_tube))
    return left, right

if __name__ == "__main__":
    start = time.time()
    l, r = main()
    end = time.time()
    print("当有两个喷油器时，转速应该为：{}".format(l))
    print("耗时： {}s".format(end - start))     # 约六分钟