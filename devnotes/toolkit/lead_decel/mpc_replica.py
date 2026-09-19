"""long_mpc.py(acados OCP)의 casadi/IPOPT 복제본(오프라인 what-if 전용, 실제 acados 결과와 동일하지 않음). 의존: casadi, numpy.
- 검증(97차): 로그 accels 궤적 대비 RMSE 약 0.22 m/s²(jerk_factor=1.0, comfort_brake=2.47, stop_distance=11.6은 로그의 desiredDistance 역산값). 강한 감속(-3.7) 사례는 -2.75로 과소 재현.
- 동적계: x'=v, v'=a, a'=j (구간별 j 상수, 정확 이산화)
- 비용: 0.5*W*r^2, r0=((xo-x)-d_comf(v))/(v+10), r4=a-prev_a, r5=j ; W=[5,.,.,.,a_change*interp(t),jerk_factor*5]
- 소프트 제약: danger((xo-x)-0.8*d_comf)/(v+10) >= 0 (L2 슬랙 100), a_min<=a<=a_max, v>=0
- 리드 투사: process_lead/extrapolate_lead 그대로(aLeadK, aLeadTau)
"""
import numpy as np, casadi as ca
N=12; MAX_T=10.0
T = MAX_T*(np.arange(N+1)/N)**2
DT = np.diff(T)
TD = np.diff(T, prepend=[0.])
CB_DEFAULT, STOP_DEFAULT = 2.47, 11.6
def d_comf(v, tf, cb, sd): return v**2/(2*cb) + tf*v + sd
def stop_eq(v, cb): return v**2/(2*cb)
def extrapolate_lead(x, v, a, tau):
    a_tr = a*np.exp(-tau*(T**2)/2.)
    v_tr = np.clip(v + np.cumsum(TD*a_tr), 0.0, 1e8)
    x_tr = x + np.cumsum(TD*v_tr)
    return x_tr, v_tr
def process_lead(dRel, vLead, aLeadK, tau, v_ego, a_min=-3.5):
    min_x = ((v_ego+vLead)/2)*(v_ego-vLead)/(-a_min*2)
    x = max(dRel, min_x); v = max(vLead, 0.0); a = float(np.clip(aLeadK,-10.,5.))
    return extrapolate_lead(x, v, a, tau)
def obstacle(x_tr, v_tr, cb): return x_tr + stop_eq(v_tr, cb)
def solve(v0, a0, xo, tf, prev_a, jerk_factor=1.0, a_change=200., cb=CB_DEFAULT, sd=STOP_DEFAULT,
          a_min=-3.5, a_max=1.5, warm=None):
    opti = ca.Opti()
    X = opti.variable(3, N+1); J = opti.variable(N); S = opti.variable(N+1)
    opti.subject_to(X[:,0] == ca.vertcat(0., v0, a0))
    cost = 0
    for i in range(N):
        dt = DT[i]; x,v,a = X[0,i],X[1,i],X[2,i]; j=J[i]
        opti.subject_to(X[0,i+1] == x + v*dt + a*dt**2/2 + j*dt**3/6)
        opti.subject_to(X[1,i+1] == v + a*dt + j*dt**2/2)
        opti.subject_to(X[2,i+1] == a + j*dt)
    for i in range(N+1):
        x,v,a = X[0,i],X[1,i],X[2,i]
        dc = d_comf(v, tf, cb, sd)
        r0 = ((xo[i]-x)-dc)/(v+10.)
        wac = a_change*np.interp(T[i],[0,1,2],[1,1,0])
        c = 5.*r0**2 + wac*(a-prev_a[i])**2
        if i < N: c += jerk_factor*5.*J[i]**2
        cost += 0.5*c
        h3 = ((xo[i]-x)-0.8*dc)/(v+10.)
        opti.subject_to(h3 + S[i] >= 0); opti.subject_to(S[i] >= 0)
        cost += 0.5*100.*S[i]**2
        opti.subject_to(opti.bounded(a_min, a, a_max)); opti.subject_to(v >= -0.5)
    opti.minimize(cost)
    if warm is not None:
        opti.set_initial(X, warm[0]); opti.set_initial(J, warm[1])
    else:
        opti.set_initial(X[1,:], v0); 
    opti.solver('ipopt', {'print_time':False}, {'print_level':0,'max_iter':200,'sb':'yes','tol':1e-6})
    sol = opti.solve()
    return sol.value(X), sol.value(J)
