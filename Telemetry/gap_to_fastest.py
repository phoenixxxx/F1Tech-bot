import fastf1.plotting
from fastf1.core import Laps
import pandas as pd
from timple.timedelta import strftimedelta
import matplotlib.pyplot as plt
from pathlib import Path

# we only want support for timedelta plotting in this example
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme=None,
                          misc_mpl_mods=False)

def plot(year: int, event: str, session: str, path: Path, drivers: str = None, remove: str = None):
    session = fastf1.get_session(year, event, session)
    session.load()

    if drivers:
        drivers = drivers.split(',')
    else:
        drivers = pd.unique(session.laps['Driver']).tolist()

    if remove:
        for drv in remove:
            drivers.remove(drv)
    ##############################################################################
    # After that we'll get each drivers fastest lap, create a new laps object
    # from these laps, sort them by lap time and have pandas reindex them to
    # number them nicely by starting position.

    list_fastest_laps = list()
    for drv in drivers:
        drvs_fastest_lap = session.laps.pick_driver(drv).pick_fastest()
        if pd.isnull(drvs_fastest_lap['LapTime']) == False:
            list_fastest_laps.append(drvs_fastest_lap)
            fastest_laps = Laps(list_fastest_laps) \
            .sort_values(by='LapTime') \
            .reset_index(drop=True)

    ##############################################################################
    # The plot is nicer to look at and more easily understandable if we just plot
    # the time differences. Therefore we subtract the fastest lap time from all
    # other lap times.

    fastest_lap = fastest_laps.pick_fastest()
    fastest_laps['LapTimeDelta'] = fastest_laps['LapTime'] - fastest_lap['LapTime']

    ##############################################################################
    # Finally, we'll create a list of team colors per lap to color our plot.
    team_colors = list()
    for index, lap in fastest_laps.iterlaps():
        team = lap['Team']
        color = fastf1.plotting.team_color(team)
        team_colors.append(color)

    ##############################################################################
    # Now, we can plot all the data
    plt.style.use('dark_background')
    fig, ax = plt.subplots()
    ax.barh(fastest_laps.index, fastest_laps['LapTimeDelta'],
            color=team_colors, edgecolor='grey')
    ax.set_yticks(fastest_laps.index)
    ax.set_yticklabels(fastest_laps['Driver'])

    # show fastest at the top
    ax.invert_yaxis()

    # draw vertical lines behind the bars
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, which='major', linestyle='--', color='white', zorder=-1000)
    # sphinx_gallery_defer_figures

    ##############################################################################
    # Finally, give the plot a meaningful title

    lap_time_string = strftimedelta(fastest_lap['LapTime'], '%m:%s.%ms')

    # plt.suptitle(f"{session}\n"
    #             f"Fastest Lap: {lap_time_string} ({fastest_lap['Driver']})")

    plt.savefig(path,  dpi=100)

    # retun event full name
    return f'{session}', f'{fastest_lap['Driver']}', lap_time_string