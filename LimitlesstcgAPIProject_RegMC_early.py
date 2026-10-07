import requests
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
sns.set_theme(rc={'figure.figsize':(14,8)})

base_url = "https://play.limitlesstcg.com/api/tournaments/6a9c5234a4272c53be6480bf/standings"
params = {
    "game": "VGC",
    "format": "M-C"
}

def get_tournaments(url, params):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            tournaments = response.json()
            return tournaments
        else:
            print('Error: unable to acces', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error: wrong url', e)
        return None

def get_standings(url):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            standings = response.json()
            return standings
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

standings = get_standings(base_url)
team = ""

# Pokemon must be in lowercase
def load_tour_data():
    teams_list = np.empty(((len(standings) - 1)*6, 8), dtype = 'object')
    if standings:
        for index, placement in enumerate(standings[1:len(standings)], start = 1):

            # Store teams used
            for i in range((index-1)*6, index*6):
                teams_list[i, :] = [placement['player'], placement['decklist'][i % 6]['name'], placement['decklist'][i % 6]['item'], 
                                    placement['decklist'][i % 6]['attacks'], placement['decklist'][i % 6]['ability'], 
                                    placement['decklist'][i % 6]['nature'], placement['record']['wins'], placement['record']['losses']]

    poke_df = pd.DataFrame(teams_list, columns = ['PID', 'Pokemon', 'Item', 'Moveset', 'Ability', 'Nature', 'Wins', 'Losses'])
    return poke_df

teams = load_tour_data()

# Obtain unique list of all Pokemon
all_poke = teams.Pokemon.unique().to_numpy()
all_items = teams.Item.unique().to_numpy()
all_abilities = teams.Ability.unique().to_numpy()
all_natures = np.char.capitalize(teams.Nature.unique().to_numpy(dtype = "str"))
all_moves = teams.Moveset
sorted_nested_list = [sorted(sublist, key=str.lower) for sublist in all_moves]

all_moves_unique = set()
all_moves_unique = {tuple(my_list) for my_list in sorted_nested_list}

all_moves_sorted = [list(tup) for tup in all_moves_unique]

def find_win_rate(Pokemon1, Pokemon2):
    df1 = teams[teams['Pokemon'] == Pokemon1]
    df2 = teams[teams['Pokemon'] == Pokemon2]

    df_merge = df1.loc[df1.PID.isin(df2.PID)]

    try:
        win_rate = df_merge['Wins'].sum() / (df_merge['Wins'].sum() + df_merge['Losses'].sum())
        #print("These two Pokemon are on a team together")
        return win_rate, len(df_merge)

    except ZeroDivisionError:
        #print("These Pokemon aren't on any teams together")
        return None

    except TypeError:
        return None

def find_best_partner(Pokemon, min_teams):
    # Don't include the selected Pokemon when cycling through teammates
    remove_poke = all_poke[all_poke != Pokemon]
    partner_dict = {}
    wr = 0
    size = 0

    # Find the win/rate of each duo, and how many teams had said duo
    for mon in remove_poke:
        try:
            wr, size = find_win_rate(Pokemon, mon)
        
        # If there are no teams with this duo, throw a type error
        except TypeError:
            wr = 0
            size = 0
        if size >= min_teams:
            partner_dict[mon] = wr
    
    if (not(partner_dict)):
        print("Insufficient teams, returning empty dictionary; consider lowering the number of teams")

    return dict(sorted(partner_dict.items(), key=lambda item: item[1]))

my_dict = find_best_partner("Salamence", 10)
last_key, last_value = next(reversed(my_dict.items()))
print(last_key, "->", last_value)

def item_win_rate(Pokemon, item):
    df1 = teams[teams['Pokemon'] == Pokemon]
    df2 = df1[df1['Item'] == item]

    #df_merge = df1.loc[df1.Pokemon.isin(df2.Pokemon)]

    try:
        win_rate = df2['Wins'].sum() / (df2['Wins'].sum() + df2['Losses'].sum())
        #print("These two Pokemon are on a team together")
        return win_rate, len(df2)

    except ZeroDivisionError:
        #print("None of these Pokemon were holding this item!")
        return None

    except TypeError:
        return None

def ability_win_rate(Pokemon, ability):
    df1 = teams[teams['Pokemon'] == Pokemon]
    df2 = df1[df1['Ability'] == ability]

    #df_merge = df1.loc[df1.Pokemon.isin(df2.Pokemon)]

    try:
        win_rate = df2['Wins'].sum() / (df2['Wins'].sum() + df2['Losses'].sum())
        #print("These two Pokemon are on a team together")
        return win_rate, len(df2)

    except ZeroDivisionError:
        #print("This Pokemon doesn't have this ability!")
        return None

    except TypeError:
        return None

def nature_win_rate(Pokemon, nature):
    df1 = teams[teams['Pokemon'] == Pokemon]
    df2 = df1[df1['Nature'] == nature]

    #df_merge = df1.loc[df1.Pokemon.isin(df2.Pokemon)]

    try:
        win_rate = df2['Wins'].sum() / (df2['Wins'].sum() + df2['Losses'].sum())
        #print("These two Pokemon are on a team together")
        return win_rate, len(df2)

    except ZeroDivisionError:
        #print("This Pokemon doesn't have this nature!")
        return None

    except TypeError:
        return None

def moveset_win_rate(Pokemon, moveset):
    df1 = teams[teams['Pokemon'] == Pokemon]
    target_set = {tuple(inner) for inner in moveset}
    mask = df1['Moveset'].apply(
        lambda x: {tuple(inner) for inner in x} == target_set
    )
    df2 = df1[mask]

    try:
        win_rate = df2['Wins'].sum() / (df2['Wins'].sum() + df2['Losses'].sum())
        #print("These two Pokemon are on a team together")
        return win_rate, len(df2)

    except ZeroDivisionError:
        #print("This Pokemon doesn't can't learn some of these moves!")
        return None

    except TypeError:
        return None

def find_best_item(Pokemon, min_teams):
    item_dict = {}
    wr = 0
    size = 0
    for myItem in all_items:
        try:
            wr, size = item_win_rate(Pokemon, myItem)
        except TypeError:
            wr = 0
            size = 0
        if size >= min_teams:
            item_dict[myItem] = wr
    
    if (not(item_dict)):
        print("Insufficient teams, returning empty dictionary; consider lowering the number of teams")

    return dict(sorted(item_dict.items(), key=lambda item: item[1]))

def find_best_ability(Pokemon, min_teams):
    ability_dict = {}
    wr = 0
    size = 0
    for myAbility in all_abilities:
        try:
            wr, size = ability_win_rate(Pokemon, myAbility)
        except TypeError:
            wr = 0
            size = 0
        if size >= min_teams:
            ability_dict[myAbility] = wr
    
    if (not(ability_dict)):
        print("Insufficient teams, returning empty dictionary; consider lowering the number of teams")

    return dict(sorted(ability_dict.items(), key=lambda item: item[1]))

def find_best_nature(Pokemon, min_teams):
    nature_dict = {}
    wr = 0
    size = 0
    for myNature in all_natures:
        try:
            wr, size = nature_win_rate(Pokemon, myNature)
        except TypeError:
            wr = 0
            size = 0
        if size >= min_teams:
            nature_dict[myNature] = wr
    
    if (not(nature_dict)):
        print("Insufficient teams, returning empty dictionary; consider lowering the number of teams")

    return dict(sorted(nature_dict.items(), key=lambda item: item[1]))

def find_best_moveset(Pokemon, min_teams):
    move_dict = {}
    wr = 0
    size = 0
    for myMove in all_moves_sorted:
        try:
            wr, size = moveset_win_rate(Pokemon, sorted(myMove))
        except TypeError:
            wr = 0
            size = 0
        if size >= min_teams:
            move_dict[tuple(myMove)] = wr
    
    if (not(move_dict)):
        print("Insufficient teams, returning empty dictionary; consider lowering the number of teams")

    return dict(sorted(move_dict.items(), key=lambda item: item[1]))

def plot_summary(Pokemon, min_teams):

    partner_dict = find_best_partner(Pokemon, min_teams)
    item_dict = find_best_item(Pokemon, min_teams)
    nature_dict = find_best_nature(Pokemon, min_teams)
    ability_dict = find_best_ability(Pokemon, min_teams)

    plt.close('all')
    partner_df = pd.DataFrame(list(partner_dict.items()), columns=["Partner", "Win Rate"])
    item_df = pd.DataFrame(list(item_dict.items()), columns=["Item", "Win Rate"])
    nature_df = pd.DataFrame(list(nature_dict.items()), columns=["Nature", "Win Rate"])
    ability_df = pd.DataFrame(list(ability_dict.items()), columns=["Ability", "Win Rate"])

    # Create the barplot
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes_flat = axes.flatten()

    #result = df.groupby(["Partner"])['Win Rate'].aggregate(np.median).reset_index().sort_values('Win Rate')
    sns.barplot(data=partner_df, x="Partner", y="Win Rate", 
    order = partner_df.sort_values(by=['Win Rate'], ascending=False).set_index('Partner').index, 
    palette = sns.color_palette("husl", 9),
    ax = axes_flat[0])
    axes_flat[0].tick_params('x', labelrotation=-45)
    axes_flat[0].set_title("Best Partners")

    sns.barplot(data=item_df, x="Item", y="Win Rate", 
    order = item_df.sort_values(by=['Win Rate'], ascending=False).set_index('Item').index, 
    palette = sns.color_palette("husl", 9),
    ax = axes_flat[1])
    axes_flat[1].set_title("Best Items")

    sns.barplot(data=nature_df, x="Nature", y="Win Rate", 
    order = nature_df.sort_values(by=['Win Rate'], ascending=False).set_index('Nature').index, 
    palette = sns.color_palette("husl", 9),
    ax = axes_flat[2])
    axes_flat[2].set_title("Best Natures")

    sns.barplot(data=ability_df, x="Ability", y="Win Rate", 
    order = ability_df.sort_values(by=['Win Rate'], ascending=False).set_index('Ability').index, 
    palette = sns.color_palette("husl", 9),
    ax = axes_flat[3])
    axes_flat[3].set_title("Best Abilities")

    my_title = "Overview of " + Pokemon + " performance"
    fig.suptitle(my_title)
    plt.tight_layout()
    plt.show()

my_dict = find_best_moveset("Sneasler", 10)
last_key, last_value = next(reversed(my_dict.items()))
print(last_key, "->", last_value)

plot_summary("Sneasler", 10)