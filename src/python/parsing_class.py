from os import listdir
from pathlib import Path
from datetime import datetime
from pandas import concat, read_csv
import sys
from matplotlib.pyplot import title, xlabel, ylabel, plot, show, figure

class Parser:

    def __init__(self, basePath):
        self.basePath = basePath

    def generate_structure(self) -> dict:
        """Generates a nested dictionary giving access to each file according to its date and hour."""
        datesList = list(set([str(file[:11]) for file in listdir(self.basePath)
                              if Path(f"{listdir(self.basePath)}/{file}").suffix == '.txt']))
        datesDictionary = dict(zip(datesList, [[] for i in range(len(datesList))]))

        for file in [file for file in listdir(self.basePath) if Path(f"{listdir(self.basePath)}/{file}").suffix == '.txt']:
            datesDictionary[str(file[:11])].append(str(file[11:17]))
        for date, hours in datesDictionary.items():
            datesDictionary[date] = dict(zip(hours, [[date + hour + '_gnss.txt', date + hour + '_imu.txt',
                                                      date + hour + '_sonar.txt'] for hour in hours]))

        return datesDictionary

    def grab_files(self, date: str, hours: [int, int]) -> list:
        """Returns certain files given its date and range of hours."""
        datesDictionary = self.generate_structure()
        filenames = []
        if date in datesDictionary.keys():
            hoursDictionary = datesDictionary[date]
            for hour in hoursDictionary.keys():
                if hours[0] < int(hour) < hours[1]:
                    filenames += datesDictionary[date][hour]
        else:
            sys.stderr.write('Unrecognized date.')

        return filenames


if __name__ == '__main__':

    # pass
    base_path = '/home/fundy/Documents/main_test/raw'
    p = Parser(base_path)
    dico = p.generate_structure()
    for date in dico.keys():
        year = date[:4]
        month = date[5:7]
        day = date[8:10]
        if datetime(int(year), int(month), int(day)).weekday() == 0:
            test = sorted([[int(hour), files[0]] for hour, files in dico[date].items()])
            x, y = [], []
            figure(f'{day}')
            i = 0
            for hour in test:
                data = read_csv(f'{base_path}/{hour[1]}', sep=';').values
                print(f'{base_path}/{hour[1]}')
                for _, _, _, dep, _, _ in data:
                    x.append(i)
                    i += 1
                    y.append(dep)
                plot(x, y, 'b-')
                xlabel('Time')
                ylabel('Depth')
                title('Depth evolution near Rimouski')

    show()



