import seaborn as sns
import matplotlib.pyplot as plt


def plot_series(df, x_var, x_label, x_convert, y_vars, y_labels, y_converts, scale='linear'):
    # Set Color Palette
    colors = sns.color_palette("colorblind")
    # Set resolution for saving figures
    DPI = 600
    # set style
    sns.set_style('white')
    sns.set_context('paper')

    f, a = plt.subplots(nrows=len(y_vars), ncols=1, sharex=True)
    for i, (y_var, y_label, y_convert) in enumerate(zip(y_vars, y_labels, y_converts)):

        # get axis
        ax = a[i]

        # get data
        x = df.loc[:, x_var] * x_convert
        y = df.loc[:, y_var] * y_convert

        # plot
        ax.plot(x, y)
        plt.xscale(scale)

        # labels
        ax.set_ylabel(y_label)
        if i == len(y_vars) - 1:
            ax.set_xlabel(x_label)

        # Caption labels
        caption_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']
        plt.text(0.05, 0.85, caption_labels[i], horizontalalignment='center', verticalalignment='center',
                 transform=ax.transAxes, fontsize='medium', fontweight='bold')

    # Adjust layout
    # plt.tight_layout()
