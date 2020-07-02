library("ggplot2")
library(dplyr)
library(gridExtra)
library(RColorBrewer)

dir = "C:\\Users\\benne\\PycharmProjects\\caes\\examples\\well_flow"


# Set directory
setwd(dir)


df <- read.csv("results.csv")

ggplot(df,aes(x=m_dot, y=delta_p, fill=k, group=k, color=k))+
  facet_grid(r_f~p_f)+
  geom_line()+
  geom_point()+
  labs(x='Mass flow rate [kg/s]', y='Pressure drop [MPa]')


# Save
ggsave('results_r.png', device="png",
       width=7.4, height=5.0, units="in",dpi=300)
