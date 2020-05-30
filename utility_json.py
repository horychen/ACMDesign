import json
import jsonpickle

def to_json_recursively(obj, fname, suffix=''):
    s = json.dumps( json.loads( jsonpickle.encode(obj)), indent=4 )

    with open(fname + suffix, 'w') as f:
        f.write( s )

def from_json_recursively(fname, suffix=''):
    with open(fname + suffix, 'r') as f:
        read_obj = jsonpickle.decode(f.read())
    return read_obj

if __name__ == '__main__':

    # build the obj
    import module_winding_layout
    wily_by_specs = module_winding_layout.winding_layout_v2(DPNV_or_SEPA=True, Qs=24, p=1, ps=2, coil_pitch_y=9)

    import utility_json
    # save as json
    utility_json.to_json_recursively(wily_by_specs, 'test.json')
    # load from json
    wily = utility_json.from_json_recursively('test.json')

    # test the obj
    from pylab import plt, np
    zQ = 100 # number of conductors/turns per slot
    turns_per_layer = zQ / wily.number_winding_layer
    U_phase = module_winding_layout.PhaseWinding(wily.Qs, wily.m, turns_per_layer, wily.ox_distribution_phase_U)
    U_phase.plotFuncObj(U_phase.winding_func)
    U_phase.plot2piFft(U_phase.winding_func, Fs=1/(2*np.pi/3600), L=65536*2**4) # 采样频率：在2pi的周期内取720个点
    plt.show()



