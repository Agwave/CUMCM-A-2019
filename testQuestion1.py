from math import log, exp, sqrt
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

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

def flow_in_a(C=0.85, d=1.4, p_from = 160, p_to=100):
    """
    求出A口的流量
    :param C: 流量系数，default=0.85
    :param d: 小孔的直径，default=1.4
    :param p_in: A处压强，default=160
    :param p_out: 高压油管内的压强，default=100
    :return: A口的进油量
    """
    density = from_p_to_density(160)
    A = PI * pow(d/2, 2)
    delta_p = p_from - p_to
    Q = C * A * sqrt(2 * delta_p / density)
    return Q

def compute_the_mass_of_a(t, T, density_a, p_b, dt):
    """
    计算dt时间内a处流入的油的质量
    :param t: 当前时间
    :param T: 待定的A的开口时间，二分法的中点mid
    :param density_a: a处的密度
    :param p_b: b处在当前时刻的压强
    :param dt: 分割出来的时间间隔，一小段时间
    :return: 在dt内进入的油的质量
    """
    while t > T + 10:
        t -= T + 10
    mass = 0.0
    if 0 < t <= T:
        mass = density_a * flow_in_a(p_to=p_b) * dt
    return mass

def compute_the_mass_of_b(t, dt):
    """
    计算dt时间内b处流出的油的质量
    :param t: 当前时间
    :param dt: 分割出来的时间间隔，一小段时间
    :return: 在dt内流出的油的质量
    """
    while t > 100:
        t -= 100
    mass = 0.0
    if 0 < t <= 0.2:
        mass = 50 * pow(t, 2) - 50 * pow(t-dt, 2)
    elif 0.2 < t < 2.2:
        mass = 20 * t - 20 * (t-dt)
    elif 2.2 < t < 2.4:
        mass = (-50 * pow(t, 2) + 240 * t) - (-50 * pow(t-dt, 2) + 240 * (t-dt))
    return mass

def compute_V(l = 500, d = 10):
    """
    计算油管的体积
    :param l: 长度
    :param d: 直径
    :return: 体积
    """
    V = PI * pow(d/2, 2) * l
    return V

def tes_function(T, dt=0.01, max_time=10000):
    t_to_draw = []
    p_b_to_draw = []
    print("test {}".format(T))
    density_a = from_p_to_density(160)
    p_b = 100
    t = 0
    V = compute_V()
    m = 0.850 * V

    while (t < max_time):
        t = t + dt
        m_a = compute_the_mass_of_a(t, T, density_a, p_b, dt)
        m_b = compute_the_mass_of_b(t, dt)
        m = m + m_a - m_b
        density_b = m / V
        p_b = from_density_to_p(density_b)
        t_to_draw.append(t)
        p_b_to_draw.append(p_b)
        print(t, p_b)
    draw_curve(t_to_draw, p_b_to_draw, T)


def draw_curve(t_to_draw, p_b_to_draw, T):
    plt.plot(t_to_draw, p_b_to_draw)
    plt.title("Single open time: {}ms".format(T))
    plt.xlabel("time/ms")
    plt.ylabel("pressure/MPa")
    if T < 0.9:
        plt.ylim(50,125)
    plt.show()

if __name__ == "__main__":
    # 选择一行运行
    # tes_function(0.3423614501953125) # 第二题第一问
    tes_function(0.9982452392578125)   # 第二题第二问