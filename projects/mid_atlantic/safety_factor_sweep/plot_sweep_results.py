import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("sizing_study_results.csv")

f,a = plt.subplots(nrows=3, ncols=1, sharex='all', sharey='none')

ax = a.ravel()

ax[0].plot(df.safety_factor, df.RTE*100, 'x-')
# ax[0].set_xlabel("Safety factor [-]")
ax[0].set_ylabel("Round-trip efficiency\n[%]")
ax[0].set_ylim(bottom=0.0, top = 80)
ax[0].text(-0.1, 1.1, 'a', horizontalalignment='center', verticalalignment='center',
       transform=ax[0].transAxes, fontsize='medium', fontweight='bold')

ax[1].plot(df.safety_factor, df.p_store_max, 'x-')
# ax[1].set_xlabel("Safety factor [-]")
ax[1].set_ylabel("Maximum pressure\n[MPa]")
ax[1].set_ylim(bottom=0.0, top=20)
ax[1].text(-0.1, 1.1, 'b', horizontalalignment='center', verticalalignment='center',
       transform=ax[1].transAxes, fontsize='medium', fontweight='bold')

ax[2].plot(df.safety_factor, df.r_f, 'x-')
ax[2].set_xlabel("Safety factor [-]")
ax[2].set_ylabel("Air plume radius\n[m]")
ax[2].set_ylim(bottom=0.0, top= 700)
ax[2].text(-0.1, 1.1, 'c', horizontalalignment='center', verticalalignment='center',
       transform=ax[2].transAxes, fontsize='medium', fontweight='bold')


width = 8.0  # inches
height = 6.5  # inches
f.set_size_inches(width, height)
plt.savefig("plot_S5_safety_factor.png")