__author__ = 'rkaye'

import sys
import csv

print('List of arguments: {}'.format(sys.argv))
print('argv[0] is the name of the script: {}'.format(sys.argv[0]))
print('Length of arguments is: {}'.format(len(sys.argv)))

w = open(sys.argv[2], 'w')
csv_writer = csv.writer(w)
index = 0
first_row = True
for index in range(500):
    print('entering index loop with index = {}'.format(index))
    r = open(sys.argv[1], 'r')
    csv_reader = csv.reader(r, delimiter=',')
    for row in csv_reader:
        if row[0] == 'image_name' and first_row:
            csv_writer.writerow(row)
            print('Found First Header row - not ignoring')
            first_row = False
        elif row[0] == 'image_name' and not first_row:
            print('Found Header row after first - ignroing')
        else:
            row[2] = 'test_directory_' + str(index)
            csv_writer.writerow(row)
            # print('row is: {}'.format(row))
    r.close()
w.close()