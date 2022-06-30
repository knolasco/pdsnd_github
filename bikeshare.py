import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DATA_PATH = 'all-project-files'

class DescribeBikeShare:
    """
    We will build a class that gathers statistics for the user to view based on the input given
    """

    def __init__(self):
        """
        Initialize the names of the files we will choose to open.
        Initialize a data dictionary to interpret the user input.
        """
        # first welcome message
        print('Hello! Welcome to the BikeShare Interactive EDA.\n')
        self.chicago = 'chicago.csv'
        self.new_york = 'new_york_city.csv'
        self.washington = 'washington.csv'
        self.data_dict = {'chicago' : self.chicago,
                        'new york'  : self.new_york,
                        'washington' : self.washington}
        self.num_to_city = {1 : 'chicago',
                            2 : 'new york',
                            3 : 'washington'}
        self.first_question_dict = {1 : 'Compare Bike Usage by City',
                                    2 : 'Find High and Low Traffic Times',
                                    3 : 'Compare User Statistics'}
        self.third_question_dict = {1 : ['daily', 'D'],
                                    2 : ['weekly', 'W-MON'],
                                    3 : ['monthly', 'M']}
        self.goodbye_message = 'Thanks for joining us today. Hope you learned something new!'
    
    def ask(self):
        """
        Print welcome message to user and save their choice.
        """
        # print message
        self.n_stars = 50
        print('Below are the possible topics you can choose from.')
        print('*'*self.n_stars)
        print('1. Compare Bike Usage by City')
        print('2. Find High and Low Traffic Times')
        print('3. Compare User Statistics')
        print('*'*self.n_stars + '\n')

        self.user_choice = input('What topic do you want to focus on? Type "None" at any point to exit the program : ')
        self.process_first_answer()

    def print_and_ask(self):
        """
        Show the first 5 rows automatically, ask user if they would like to see 5 more
        """
        # print results
        self.exit_script = False
        n_rows = self.grouped.shape[0]
        ind = 0
        print(self.grouped.iloc[ind: ind + 5])
        while ind < n_rows:
            self.show_more = input('Would you like to see 5 more rows? (yes or no): ')
            if self.show_more.lower().strip() in ['none', '"none"']:
                print(self.goodbye_message)
                self.exit_script = True
                return
            elif self.show_more.lower().strip() not in ['yes', 'no', 'none', '"none"']:
                print('Please respond with yes or no (or None to quit) : ')
            elif self.show_more.lower().strip() == 'yes':
                ind += 5
                print(self.grouped.iloc[ind: ind + 5])
            else:
                break
        if not self.exit_script:
            print('Done viewing raw data ...')
        else:
            return

    def describe(self):
        """
        Show summary statistics based on the answer to the first question
        """
        time_choice = self.third_question_dict[self.third_answer_choice][0]
        resample_choice = self.third_question_dict[self.third_answer_choice][1]
        print('\nYou chose to {} {}'.format(self.first_question_dict[self.first_answer_choice], time_choice))
        self.volume_col = '{}_volume'.format(time_choice)
        
        if self.first_answer_choice == 1:
            self.hue_choice = 'city'    
            print('Below we see the volume by city, ordered by largest volume to smallest, aggregated {}'.format(time_choice))
            self.grouped = self.data.groupby(by = ['city', pd.Grouper(key='Start Time', freq = resample_choice)])\
                            .size().reset_index(name = self.volume_col)\
                                .sort_values(by = 'Start Time', ascending = True).reset_index(drop = True)
            self.print_and_ask()
        
        elif self.first_answer_choice == 2:
            self.hue_choice = 'Traffic Pattern'
            print('Below we see the highest and lowest traffic times, ordered by largest volume to smallest, aggregated {}'.format(time_choice))
            self.data['Start_hour'] = self.data['Start Time']
            self.grouped = self.data.groupby(by = [pd.Grouper(key='Start Time', freq = resample_choice), self.data['Start_hour'].dt.hour])\
                            .size().reset_index(name = self.volume_col)\
                                .sort_values(by = ['Start Time', self.volume_col], ascending = [True, False]).reset_index(drop = True)
            self.grouped = self.grouped.groupby('Start Time').agg(['first', 'last']).stack().reset_index()
            self.grouped['level_1'] = self.grouped['level_1'].apply(lambda level: 'High Traffic' if level == 'first' else 'Low Traffic')
            self.grouped.rename({'level_1' : 'Traffic Pattern'}, axis = 1, inplace = True)
            self.print_and_ask()
        else:
            self.hue_choice = 'User Type'
            print('Below we see the volume based on user type, ordered by largest volume to smallest, aggregated {}'.format(time_choice))
            self.grouped = self.data.groupby(by = [pd.Grouper(key='Start Time', freq = resample_choice), 'User Type'])\
                            .size().reset_index(name = self.volume_col)\
                                .sort_values(by = ['Start Time', self.volume_col], ascending = [True, False]).reset_index(drop = True)
            self.print_and_ask()

        if not self.exit_script:
            self.visualization_answer = input('Would you like to see a visualization? (yes or no) : ')
            self.process_visualization_response()
        else:
            return
    
    def process_visualization_response(self):
        """
        Deal with the visualization answer
        """
        self.visualization_answer_cleaned = self.visualization_answer.lower().strip()
        if self.visualization_answer_cleaned in ['none', '"none"']:
            print(self.goodbye_message)
            return
        elif self.visualization_answer_cleaned not in ['yes', 'no', 'none', '"none"']:
            self.visualization_answer = input('Please respond with yes or no (or None to quit) : ')
            self.process_visualization_response()
        elif self.visualization_answer_cleaned == 'yes':
            self.visualize()
        else:
            print('Okay, we won\'t visualize the data for this question.\n')
        self.ask()

    def visualize(self):
        """
        Visualize the results. Line plot with start time in x-axis
        """
        # set up plots
        fig, _ = plt.subplots(1,1)
        fig.set_size_inches(20,10)
        if self.first_answer_choice == 1:
            g = sns.lineplot(data = self.grouped, x = 'Start Time', y = self.volume_col, hue = self.hue_choice)
        elif self.first_answer_choice == 2:
            g = sns.lineplot(data = self.grouped, x = 'Start Time', y = 'Start_hour', hue = self.hue_choice)
        else:
            g = sns.lineplot(data = self.grouped, x = 'Start Time', y = self.volume_col, hue = self.hue_choice)

        g.set(title = 'Line Plot for "{}" aggregated {}'.format(self.first_question_dict[self.first_answer_choice], self.third_question_dict[self.third_answer_choice][0]))
        plt.show()

    def process_first_answer(self):
        """
        Figure out what the user chose.
        """
        self.formatted_input = self.user_choice.lower().strip()
        # deal with innappropriate inputs first
        if self.formatted_input not in ['none', '"none"', '1','2','3']:
            self.user_choice = input('Sorry, that\'s not an option in this program. Please choose from the list above (type 1, 2, or 3) or type "None" to exit : ')
            self.process_first_answer()
        
        # exit the code, check if user inputs none with quotes as well
        elif self.formatted_input in ['none', '"none"']:
            print(self.goodbye_message)
            return
        
        else:
            self.first_answer_choice = int(self.formatted_input)
            self.ask_second_question()
    
    def ask_second_question(self):
        """
        Ask questions depending on what the answer to the initial question was.
        """
        print('\nTell me which cities you are most interested in')
        print('*'*self.n_stars)
        print('1. Chicago?')
        print('2. New York?')
        print('3. Washington?')
        print('*'*self.n_stars + '\n')
        self.user_choice = input('Choose two of the three options (separated by a comma. EX: 1,2 to compare Chicago and New York), or type "all" to compare all cities at once. : ')
        self.process_second_answer()
    
    def process_second_answer(self):
        """
        Parse the user's input for the second question to determine which path to take.
        """
        self.formatted_input = self.user_choice.replace(' ', '').lower().split(',')
        # deal with innappropriate inputs first
        if (sum([0 if user_input in ['none', '"none"', '1','2','3', 'all'] else 1 for user_input in self.formatted_input]) > 0) or (len(self.formatted_input) > 2):
            self.user_choice = input('Sorry, that\'s not an option in this program. Please choose two of the three options (separated by a comma. EX: 1,2 to compare Chicago and New York), or type "all" to compare all cities at once : ')
            self.process_second_answer()

        # exit the code, check if user inputs none with quotes as well
        elif sum([1 if user_input in ['none', '"none"'] else 0 for user_input in self.formatted_input]) > 0:
            print(self.goodbye_message)
            return

        # compare all cities
        elif 'all' in self.formatted_input:
            self.load_files()
        
        # compare any two cities
        else:
            city1, city2 = int(self.formatted_input[0]), int(self.formatted_input[1])
            self.load_files(cities = [city1, city2])

        self.ask_third_question()
    
    def ask_third_question(self):
        """
        Ask what time window to aggregate the rentals.
        """
        print('\nTell me how to group the data')
        print('*'*self.n_stars)
        print('1. Daily?')
        print('2. Weekly?')
        print('3. Monthly?')
        print('*'*self.n_stars + '\n')
        self.user_choice = input('Choose one of the three options : ')
        self.process_third_answer()

    def process_third_answer(self):
        """
        Parse the user's input for the third question to determine which path to take.
        """
        self.formatted_input = self.user_choice.lower().strip()
        # deal with innappropriate inputs first
        if self.formatted_input not in ['none', '"none"', '1','2','3']:
            self.user_choice = input('Sorry, that\'s not an option in this program. Please choose from the list above (type 1, 2, or 3) or type "None" to exit : ')
            self.process_third_answer()

        # exit the code, check if user inputs none with quotes as well
        elif self.formatted_input in ['none', '"none"']:
            print(self.goodbye_message)
            return
        
        else:
            self.third_answer_choice = int(self.formatted_input)
        
        self.describe()

    def load_files(self, cities = 'all'):
        """
        Load and concat based on response
        """
        if cities == 'all':
            self.chicago_df = pd.read_csv(os.path.join(DATA_PATH, self.chicago))
            self.ny_df = pd.read_csv(os.path.join(DATA_PATH, self.new_york))
            self.washington_df = pd.read_csv(os.path.join(DATA_PATH, self.washington))
            # add city names
            self.chicago_df['city'] = 'chicago'
            self.ny_df['city'] = 'new york'
            self.washington_df['city'] = 'washington'
            self.data = pd.concat([self.chicago_df, self.ny_df, self.washington_df], axis = 0)

        else:
            # use the dictionaries to automatically read the cities chosen
            self.city1 = self.num_to_city[cities[0]]
            self.city2 = self.num_to_city[cities[1]]
            self.df1 = pd.read_csv(os.path.join(DATA_PATH, self.data_dict[self.city1]))
            self.df2 = pd.read_csv(os.path.join(DATA_PATH, self.data_dict[self.city2]))
            # add city names
            self.df1['city'] = self.city1
            self.df2['city'] = self.city2
            self.data = pd.concat([self.df1, self.df2], axis = 0)
        
        # convert time to pd.datetime
        self.data['Start Time'] = pd.to_datetime(self.data['Start Time'])
        self.data['End Time'] = pd.to_datetime(self.data['End Time'])

def main():
    describer = DescribeBikeShare()
    describer.ask()

if __name__ == '__main__':
    main()