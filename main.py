import module_winding_layout
wily_by_specs = module_winding_layout.winding_layout_v2(DPNV_or_SEPA=True, Qs=24, p=1, ps=2, coil_pitch_y=9)

import utility_json
utility_json.to_json_recursively(wily_by_specs, 'test.json')
wily = utility_json.from_json_recursively('test.json')


quit()

from pylab import plt, np
zQ = 100 # number of conductors/turns per slot
turns_per_layer = zQ / wily.number_winding_layer
U_phase = module_winding_layout.PhaseWinding(wily.Qs, wily.m, turns_per_layer, wily.ox_distribution_phase_U)
U_phase.plotFuncObj(U_phase.winding_func)
U_phase.plot2piFft(U_phase.winding_func, Fs=1/(2*np.pi/3600), L=65536*2**4) # 采样频率：在2pi的周期内取720个点
plt.show()

