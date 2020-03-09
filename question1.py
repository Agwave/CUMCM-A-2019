from math import log, exp, sqrt
import time

PI = 3.1415
c = - 1 / (1495 * 0.0039) * exp(-0.0039 * 100) - log(0.850)   # 常数项


def from_p_to_density(p):
    """
    通过压力 p 计算密度 density
    :param p: 压力
    :return: 密度
    """
    density = exp(exp(-0.0039 * p) / (-1495 * 0.0039) - c)
    return density

def from_density_to_p(density):
    """
    通过 密度density 计算 压力p
    :param density: 密度
    :return: 压力
    """
    p = log((log(density) + c) * (-1495 * 0.0039)) / -0.0039
    return p

def flow_in_a(C=0.85, d=1.4, p_from=160, p_to=100):
    """
    A口的流量
    :param C: 流量系数
    :param d: 小孔的直径
    :param p_from: A处压力
    :param p_to: 高压油管内的压力
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
    :param p_b: b处在当前时刻的压力
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
    elif 0.2 < t <= 2.2:
        mass = 20 * t - 20 * (t-dt)
    elif 2.2 < t <= 2.4:
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

def main(stable_pressure, interval_length=0.0001, T=6, dt=0.01, iteration_time=10000):
    """
    获得一个时间区间，T的值便在区间之中
    :param stable_pressure: 想要稳定到的压力值
    :param interval_length: 区间的长度（误差容忍度）
    :param T: 最长的a口的打开时间
    :param dt: 分割出来的时间间隔，一小段时间
    :param iteration_time: 进行迭代的时间的长度
    :return: 区间的两个端点
    """
    left, right = 0, T
    density_a = from_p_to_density(160)
    p_b = 100

    while (left + interval_length < right):
        mid  = left + (right - left) / 2
        print("test {}".format(mid))
        t = 0.0
        p_b = 100
        V = compute_V()
        m = 0.850 * V
        m_sum = 0.0

        while (t < iteration_time):
            t = t + dt
            m_a = compute_the_mass_of_a(t, mid, density_a, p_b, dt)
            m_b = compute_the_mass_of_b(t, dt)
            m = m + m_a - m_b
            density_b = m / V
            p_b = from_density_to_p(density_b)
            m_sum += m

        m_mean = m_sum / (iteration_time / dt)
        if m_mean <= from_p_to_density(stable_pressure) * V:
            left = mid
        else:
            right = mid
    print("最后的压强值： {}".format(p_b))
    return left, right



if __name__ == "__main__":
    start = time.time()
    # 下面两行选择一行运行，分别对应一二小问的结果
    # l, r = main(100)                           # 第一小问,耗时约20分钟
    l, r = main(150, dt=0.1, iteration_time=20000)      # 第二小问,耗时约6分钟
    print("A口应该开启的时间： {}".format((l+r)/2))
    end = time.time()
    print("耗时： {}s".format(end-start))