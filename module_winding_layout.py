import json

def infer_Y_layer_phases_from_X_layer_and_coil_pitch_y(layer_X_phases, coil_pitch):
    return layer_X_phases[-coil_pitch:] + layer_X_phases[:-coil_pitch]
def infer_Y_layer_signs_from_X_layer_and_coil_pitch_y(layer_X_signs, coil_pitch):
    temp = layer_X_signs[-coil_pitch:] + layer_X_signs[:-coil_pitch]
    return [('-' if el == '+' else '+') for el in temp]

class winding_layout_v2(object):
    def __init__(self, DPNV_or_SEPA=None, Qs=None, p=None, ps=None, coil_pitch_y=None, fname=None):
        if fname is not None:
            self.from_json(fname)
        else:
            # Naming convention:
            # right layer = 1st layer = X layer = torque layer for separate winding
            # left layer  = 2nd layer = Y layer = suspension layer for separate winding
            m = 3 # number of phase

            #~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
            # combined winding
            #~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
            if DPNV_or_SEPA == True \
            and Qs == 24 \
            and p == 1 \
            and ps == 2 \
            and coil_pitch_y == 9:

                self.layer_X_phases = ['U', 'U', 'U', 'W', 'W', 'W', 'W', 'V', 'V', 'V', 'V', 'U', 'U', 'U', 'U', 'W', 'W', 'W', 'W', 'V', 'V', 'V', 'V', 'U']
                self.layer_X_signs  = ['+', '+', '+', '-', '-', '-', '-', '+', '+', '+', '+', '-', '-', '-', '-', '+', '+', '+', '+', '-', '-', '-', '-', '+']
                self.coil_pitch_y   = coil_pitch_y
                self.layer_Y_phases = infer_Y_layer_phases_from_X_layer_and_coil_pitch_y(self.layer_X_phases, self.coil_pitch_y)
                self.layer_Y_signs  = infer_Y_layer_signs_from_X_layer_and_coil_pitch_y(self.layer_X_signs, self.coil_pitch_y)

                self.grouping_AC            = [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0]
                self.number_parallel_branch = 2
                self.number_winding_layer   = 2

                self.bool_3PhaseCurrentSource = False
                self.CommutatingSequenceD = 1
                self.CommutatingSequenceB = 0

            #~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
            # End of winding definition
            #~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
            try: 
                self.coil_pitch_y
                self.distributed_or_concentrated = False if abs(self.coil_pitch_y) == 1 else True

                # below is valid for PMSM only

                q = SPP = Qs / (2*p * m)
                print('[wily] q =', q)
                # if q%1 > 0:
                #     print('[wily] Fractional slot winding with an SPP of %g.'%(q))
                #     if q>1:
                #         raise Exception('This case is not thought thorough.')

                # Example: Q24p1
                # + + + + 0 0 0 0 0 - - - -
                # 0 1 2 3 4 5 6 7 8 9
                # 电流激励是sin(t)，0时刻的时候，电流导致的磁场刚好和U相相轴正交，所以转子的初始位置就应该是U轴相轴的位置。

                # Valid for PMSM                                                这个1是由于1号槽从x轴便宜了半个槽距角所导致的，那么为什么1号槽这么特别？因为我们默认了u相是从1号槽开始的，但是有时候U相可能从24号槽开始，那么就要进一步进入这种情况
                # self.initial_excitation_bias_compensation_deg = 360/Qs*0.5 * (1 + self.coil_pitch_y)

                if q%1 == 0:
                    # integral slot

                    phase_U_belt = self.layer_X_phases[:int(q)]
                    number_of_U = sum([1 for el in phase_U_belt if el =='U'])
                    if number_of_U<q:
                        print('目前只有%d个字母U，需要寻找一共q(=%d)个字母U。'%(number_of_U, q))
                        for phase_U_starting_slot_number in range(-1, -int(q)-1, -1):
                            new_phase_U_belt = self.layer_X_phases[phase_U_starting_slot_number:] + phase_U_belt
                            number_of_U = sum([1 for el in new_phase_U_belt if el =='U'])
                            print(phase_U_starting_slot_number, number_of_U)
                            if number_of_U < q:
                                continue
                            else:
                                break
                    else:
                        phase_U_starting_slot_number = 1 # 没有等于0的哈，等于0你得以槽的中线作图绘制定子铁芯；现在的代码是以齿的中线作图绘制定子铁芯的哦。

                    self.deg_winding_U_phase_phase_axis_angle = 360/Qs*0.5 * (phase_U_starting_slot_number + self.coil_pitch_y+(SPP-1) )
                else:
                    # This clause includes fractional slot winding with an SPP value below 1.
                    phase_U_starting_slot_number = 1

                    print('[wily] Fractional slot winding with an SPP of %g.'%(q))

                    if q<1:
                        # fractional slot and q<1
                        self.deg_winding_U_phase_phase_axis_angle = 360/Qs*0.5 * (phase_U_starting_slot_number + self.coil_pitch_y )
                    else:
                        # fractional slot and q>1
                        self.deg_winding_U_phase_phase_axis_angle = 360/Qs*0.5 * (phase_U_starting_slot_number + self.coil_pitch_y )
                        msg = 'This case (q=%g) is not thought thorough, so you must inspect the initial excitation angle and initial rotor position manually to make sure it is id=0 control.'%(q)
                        print(msg)
                        if q>2:
                            raise Exception(msg)

                        # 2019/12/25: Q18, p2, ps1 case is verified to be okay with q=1.5.

                print('[wily] phase_U_starting_slot_number', phase_U_starting_slot_number)
                print('[wily] self.deg_winding_U_phase_phase_axis_angle:', self.deg_winding_U_phase_phase_axis_angle)
                # quit()
            except:
                print(Qs,p,ps,coil_pitch_y)
                raise Exception('Error: This winding is not implemented.')

            # ACMDM: motor mode and suspension mode
            if self.number_winding_layer == 1: # this is equivalent to separate winding for now
                self.list_layer_motor_phases      = [self.layer_X_phases]
                self.list_layer_motor_signs       = [self.layer_X_signs]
                self.list_layer_suspension_phases = [self.layer_Y_phases]
                self.list_layer_suspension_signs  = [self.layer_Y_signs]

            elif self.number_winding_layer == 2: # this is equivalent to combined winding for now
                self.list_layer_motor_phases      = [self.layer_X_phases, self.layer_Y_phases] #??? 这有啥用？？？
                self.list_layer_motor_signs       = [self.layer_X_signs, self.layer_Y_signs]
                self.list_layer_suspension_phases = self.list_layer_motor_phases[::]
                suspension_layer_X_signs = [(el if ac==0 else ('-' if el == '+' else '+')) for el, ac in zip(self.layer_X_signs, self.grouping_AC)]
                self.list_layer_suspension_signs  = [ suspension_layer_X_signs, 
                                                      infer_Y_layer_signs_from_X_layer_and_coil_pitch_y(suspension_layer_X_signs, self.coil_pitch_y)]
            else:
                raise Exception('Invalid number_winding_layer.')

            # save for winding function analysis
            self.DPNV_or_SEPA = DPNV_or_SEPA
            self.Qs = Qs
            self.p = p
            self.m = 3
            self.SPP = self.Qs / (2*self.p * self.m)
            self.ox_distribution_three_phase = []
            for phases, signs in zip(self.list_layer_motor_phases, self.list_layer_motor_signs):
                temp = [phase+sign for phase, sign in zip(phases, signs)]
                self.ox_distribution_three_phase = temp if self.ox_distribution_three_phase == [] else [a+b for a,b in zip(self.ox_distribution_three_phase, temp)]
            def replace_uvw_with_ox(string, UVW):
                string = string.replace(UVW+'+', 'x')
                string = string.replace(UVW+'-', 'o')
                return string
            def replace_uvw_with_empty_string(string, UVW):
                string = string.replace(UVW+'+', '')
                string = string.replace(UVW+'-', '')
                return string
            self.ox_distribution_phase_U = [replace_uvw_with_ox(el, 'U') for el in self.ox_distribution_three_phase]
            self.ox_distribution_phase_U = [replace_uvw_with_empty_string(el, 'V') for el in self.ox_distribution_phase_U]
            self.ox_distribution_phase_U = [replace_uvw_with_empty_string(el, 'W') for el in self.ox_distribution_phase_U]
            print(self.ox_distribution_three_phase)
            print(self.ox_distribution_phase_U)

    def to_json(self, fname):
        with open(self.build_json_fname(fname), 'w') as f:
            json.dump(self.__dict__, f, indent=4)        

    def from_json(self, fname):
        with open(self.build_json_fname(fname), 'r') as f:
            d = json.load(f)
            self.__dict__.update(d)

    @staticmethod
    def build_json_fname(fname):
        if fname[:2] != '__':
            return '__'+fname+'-WindingLayout'+'.json'
        else:
            return fname

# if __name__ == '__main__':
#     wily = winding_layout_v2(DPNV_or_SEPA=True, Qs=24, p=2, ps=1, coil_pitch=6)
#     quit()

from pylab import np, plt, fft, linspace
import scipy.integrate as integrate

def nextpow2(L):
    n = 0
    while 2**n < L:
        n += 1
    return n

def periodic2pi(x):
    # make x periodic positive
    while(x<0):
        x += 2*np.pi

    # make it within 2*pi
    if int(x / (2*np.pi)) != 0:
        x = x % (2*np.pi)

    return x

def segmented_func(x, lst_x, lst_y):
    ''' The value in lst_x must increase monotonously.
        根据判断，x在lst_x中的位置，返回对应的阶梯函数值。
    '''
    x = periodic2pi(x)
    
    if len(lst_x) != len(lst_y):
        raise Exception('Error: lst_x & y must has same length.')

    for i in range(0,len(lst_x)):
        if x > lst_x[i]: # x 超过了lst_x[i]的位置，
            if i == len(lst_x)-1: # last i。比最后一个位置lst_x[-1]大，比2pi小。
                return lst_y[-1]

        else: # x 比lst_x[i]小，但是比lst_x[i-1]大。
            if i-1 < 0: # first i。比第一个位置lst_x[0]小，比0大。
                return lst_y[-1] # 注意lst_y[0]的值不是0，但是lst_y[-1]是0.
            else: # 普通情况：
                return lst_y[i-1]

class PhaseWinding:
    '''[PhaseWinding]
    
    [The winding function and turn function are consistent with Lipo's 2012 book.]
    '''
    def __init__(self, Qs, m, turns_per_slot, ox_distribution_phase_U, desc_type = 'STEP_DISTRIBUTED'):
        if desc_type == 'STEP_DISTRIBUTED':
            pass
        else:
            raise Exception('Not implemented for other type of descripsion.')

        self.slot_per_phase = Qs / m # Only upper layer counts for one slot.
        self.turns_per_slot = turns_per_slot
        self.degree_between_slots = 360.0 / Qs # mechanical deg.
        self.radian_between_slots = self.degree_between_slots / 180.0 * np.pi # mechanical rad.
        self.ox_distribution_phase_U = ox_distribution_phase_U
        print(self.ox_distribution_phase_U)

        # turn function 
        self.setTurnFuncObject(self.ox_distribution_phase_U) # define self.turn_func
        # <turn function> defined by Lipo 2012
        self.avg_val_of_turn_func = integrate.quad(self.turn_func, 0, 2*np.pi)[0] / (2*np.pi) # [1] is error of integration
        # winding function
        self.winding_func = lambda x: self.turn_func(x)-self.avg_val_of_turn_func

        # get self.sym_begin_pos 
        self.setSymPos()
        # symmetric turn function
        self.sym_turn_func = lambda x: self.turn_func(x + self.sym_begin_pos)
        # symmetric winding function
        self.sym_winding_func = lambda x: self.winding_func(x + self.sym_begin_pos)

    def setTurnFuncObject(self, ox_distribution_phase_U):
        '''  ['x','x','x','x',
              'n','n','n','n',
              'o','o','o','o',
              'n','n','n','n']
              非n地方才记录，x增，o减。
        '''
        x_val, y_val, lst_x, lst_y = 0, 0, [], []
        for el in ox_distribution_phase_U:
            x_val += self.radian_between_slots
            if el == 'x':
                y_val += self.turns_per_slot
                lst_y.append(y_val)
                lst_x.append(x_val)
            elif el == 'xx':
                y_val += 2* self.turns_per_slot                
                lst_y.append(y_val)
                lst_x.append(x_val)
            elif el == 'o':
                y_val -= self.turns_per_slot                
                lst_y.append(y_val)
                lst_x.append(x_val)
            elif el == 'oo':
                y_val -= 2 * self.turns_per_slot                
                lst_y.append(y_val)
                lst_x.append(x_val)
            else:
                pass
        self.lst_x = lst_x
        self.lst_y = lst_y
        self.turn_func = lambda x: segmented_func(x, self.lst_x, self.lst_y)

    def setSymPos(self, index=2):
        '''
            可选择两种不同的对称位置。用作原始turn_func和wind_func的偏移。举例：
            和lst_x一一对应的lst_y:
                50
                100
                150
                200      <- pos2 @ max y 
                150x
                100x
                50x
                0        <- pos1 @ min y
        '''
        # symmetrical pos_2 = pos_200 + (pos_150x - pos_200) / 2
        index = self.lst_y.index(max(self.lst_y))
        self.sym_begin_pos_2 = self.lst_x[index] + (self.lst_x[index+1] - self.lst_x[index]) / 2.

        # symmetrical pos_1
        self.sym_begin_pos_1 = self.sym_begin_pos_2 + np.pi

        if index == 1:
            self.sym_begin_pos = self.sym_begin_pos_1
        else:
            self.sym_begin_pos = self.sym_begin_pos_2

    def plot2piFft(self, func, Fs, L):
        ''' Fs is the sampling freq. 
            L is length of signal list.
            This plot is for a func that has period of 2pi.

            If you found the time domain wave is not very accurate,
            that is because you set too small Fs, which leads to
            to big step Ts.
        '''
        base_freq = 1.0/(2*np.pi) #频域横坐标除以基频，即以基频为单位，此处的基频为 2*pi rad/s
        Ts = 1.0/Fs
        t = [el*Ts for el in range(0,L)]
        x = [func(el) for el in t]

        # https://www.ritchievink.com/blog/2017/04/23/understanding-the-fourier-transform-by-example/

        # 小明给的代码：
        # sampleF = Fs
        # print('小明：')
        # for f, Y in zip(
        #                 np.arange(0, len(x)*sampleF,1) * 1/len(x) * sampleF, 
        #                 np.log10(np.abs(np.fft.fft(x) / len(x))) 
        #              ):
            # print('\t', f, Y)


        L_4pi = int(4*np.pi / Ts) +1 # 画前两个周期的
        
        self.fig_plot2piFft = plt.figure(7)
        plt.subplot(211)
        plt.plot(t[:L_4pi], x[:L_4pi])
        #title('Signal in Time Domain')
        #xlabel('Time / s')
        #ylabel('x(t)')
        plt.title('Winding Function')
        plt.xlabel('Angular location along air gap [mech. rad.]')
        plt.ylabel('Current Linkage by unit current [Ampere]')

        NFFT = 2**nextpow2(L)
        print('NFFT =', NFFT, '= 2^%g' % (nextpow2(L)), '>= L =', L)
        y = fft(x,NFFT) # y is a COMPLEX defined in numpy
        Y = [2 * el.__abs__() / L for el in y] # /L for spectrum aplitude consistent with actual signal. 2* for single-sided. abs for amplitude.
        f = Fs/2.0/base_freq*linspace(0,1,int(NFFT/2+1)) # unit is base_freq Hz
        #f = Fs/2.0*linspace(0,1,NFFT/2+1) # unit is Hz

        plt.subplot(212)
        plt.plot(f, Y[0:int(NFFT/2+1)])
        plt.title('Single-Sided Amplitude Spectrum of x(t)')
        plt.xlabel('Frequency divided by base_freq [base freq * Hz]')
        #plt.ylabel('|Y(f)|')
        plt.ylabel('Amplitude [1]')
        plt.xlim([0,50])
        # plt.show()

    def plotFuncObj(self, func):
        x = np.arange(0, 2*np.pi, 0.5/180*np.pi)
        y = [func(el) for el in x]
        x = [el/np.pi for el in x] # x for plot. unit is pi
        
        self.fig_plotFuncObj = plt.figure()
        ax = plt.subplot(111) #注意:一般都在ax中设置,不在plot中设置
        ax.plot(x, y)

        xmajorLocator   = plt.MultipleLocator(0.25) #将x主刻度标签设置为20的倍数
        xmajorFormatter = plt.FormatStrFormatter('%.2fπ') #设置x轴标签文本的格式
        ax.xaxis.set_major_locator(xmajorLocator)  
        ax.xaxis.set_major_formatter(xmajorFormatter)

        ##matplotlib.pyplot.minorticks_on()
        ##xminorLocator   = MultipleLocator(0.25)
        ##xminorFormatter = FormatStrFormatter(u'%.2fπ')
        ##ax.xaxis.set_minor_locator(xminorLocator)  
        ##ax.xaxis.set_minor_formatter(xminorFormatter)

        plt.xlabel('Angular location along the gap [mech. rad.]')
        plt.ylabel('Turns of winding [1]')
        # plt.title('Turn Function or Winding Function')
        plt.grid(True) # or ax.grid(True)
        # plt.gcf().savefig("turn_function.png")
        # plt.show()

if __name__ == '__main__':

    wily_by_specs = winding_layout_v2(DPNV_or_SEPA=True, Qs=24, p=1, ps=2, coil_pitch_y=9)
    wily_by_specs.to_json('2019-blim-prototype')

    wily_by_json = winding_layout_v2(fname='__2019-blim-prototype-WindingLayout.json')

    wily = wily_by_json

    zQ = 100 # number of conductors/turns per slot
    turns_per_layer = zQ / wily.number_winding_layer
    U_phase = PhaseWinding(wily.Qs, wily.m, turns_per_layer, wily.ox_distribution_phase_U)
    U_phase.plotFuncObj(U_phase.winding_func)
    U_phase.plot2piFft(U_phase.winding_func, Fs=1/(2*np.pi/3600), L=65536*2**4) # 采样频率：在2pi的周期内取720个点


    plt.show()

