import csv
import random

f = open("features_new.csv")

reader = csv.reader(f)

num_rows = sum(1 for row in reader)

random_numbers = list(range(num_rows))

random.shuffle(random_numbers)

test_indices = random_numbers[:4000]

train_indices = random_numbers[4000:]

testout = open("test_indices_new.csv","w")
trainout = open("train_indices_new.csv","w")

for idx, i in enumerate(test_indices):
    testout.write(str(i))
    if(idx != len(test_indices)-1): testout.write('\n')

for idx, i in enumerate(train_indices):
    trainout.write(str(i))
    if(idx != len(train_indices)-1): trainout.write('\n')

f.close()
testout.close()
trainout.close()


