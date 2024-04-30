import seaborn as sns
from matplotlib import pyplot as plt

import fastf1
import fastf1.plotting

from pathlib import Path

# activate the fastf1 color scheme (and no other modifications)
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)

###############################################################################
# Load the race session.
# Pick all quick laps (within 107% of fastest lap).
# For races with mixed conditions, pick_wo_box() is better.
def plot(year: int, event: str, path: Path) -> str:
    race = fastf1.get_session(year, event, 'R')
    race.load()
    
    laps = race.laps.pick_quicklaps()

    ###############################################################################
    # Convert the lap time column from timedelta to integer.
    # This is a seaborn-specific modification.
    # If plotting with matplotlib, set mpl_timedelta_support to true
    # with plotting.setup_mpl.
    transformed_laps = laps.copy()
    transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()

    # order the team from the fastest (lowest median lap time) tp slower
    team_order = (
        transformed_laps[["Team", "LapTime (s)"]]
        .groupby("Team")
        .median()["LapTime (s)"]
        .sort_values()
        .index
    )
    print(team_order)

    # make a color palette associating team names to hex codes
    team_palette = {team: fastf1.plotting.team_color(team) for team in team_order}

    ###############################################################################
    fig, ax = plt.subplots(figsize=(15, 10))
    sns.boxplot(
        data=transformed_laps,
        x="Team",
        y="LapTime (s)",
        hue="Team",
        order=team_order,
        palette=team_palette,
        whiskerprops=dict(color="white"),
        boxprops=dict(edgecolor="white"),
        medianprops=dict(color="grey"),
        capprops=dict(color="white"),
    )

    plt.grid(visible=False)

    # x-label is redundant
    ax.set(xlabel=None)
    plt.tight_layout()

    # Show the plot
    plt.savefig(path,  dpi=100)

    # retun event full name
    return f'{race}'