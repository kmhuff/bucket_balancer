#! /usr/bin/env python3

import argparse
import configparser

def bucket(input):
    list = input.split(':')
    valueFlt = float(list[2])
    valueFlt = valueFlt * 100
    return Bucket(list[0], list[1], int(valueFlt))


class Bucket:
    def __init__(self, acctName, className, value):
        self.acctName = acctName
        self.className = className
        self.value = value
        self.fill = 0

    def fillUp(self, fillAmt):
        self.fill += fillAmt
        self.value += fillAmt

    def print(self):
        print(self.className + " in " + self.acctName + " controls " + str(float(self.value) / 100) + " (" + str(float(self.fill) / 100) + ")")


class Account:
    def __init__(self, name, maxFill, priority):
        self.name = name
        self.maxFill = maxFill
        self.priority = priority

    def fillUp(self, totalFill):
        if self.maxFill >= totalFill:
            self.maxFill -= totalFill
            return totalFill
        else:
            fillAmt = self.maxFill
            self.maxFill = 0
            return fillAmt
            
    def print(self):
        if self.maxFill != float('inf'):
            print(self.name + " has remaining fill " + str(float(self.maxFill) / 100))

class AssetClass:
    def __init__(self, name, weight, priority):
        self.name = name
        self.weight = weight
        self.priority = priority
        self.valueAccountList = []

    def addValueAccount(self, valueAccountPair):
        self.valueAccountList.append(valueAccountPair)

    def finalizeValueAccountList(self):
        self.valueAccountList.sort(key=lambda tup: tup[0].priority)

        self.value = 0
        for pair in self.valueAccountList:
            self.value += pair[1].value

    def initRatio(self, totalWeight):
        self.ratio = float(self.weight) / float(totalWeight)

    def expectedTotalSize(self):
        return self.value / self.ratio

    def diffToTargetSizeForTotal(self, total):
        targetSize = total * self.ratio

        if targetSize < self.value:
            raise Exception("Target less than current value")
 
        self.diff = targetSize - self.value
        return self.diff

    def fillClass(self, fillAmt):
        toBeFilled = fillAmt

        for pair in self.valueAccountList:
            partialFill = pair[0].fillUp(toBeFilled)
            toBeFilled -= partialFill
            pair[1].fillUp(partialFill)

    def fillDiff(self):
        self.fillClass(self.diff)


def balancedInsert(classMap, insertAmt):
    for value in classMap.values():
        value.finalizeValueAccountList()

    totalWeight = 0
    for item in classMap.items():
        totalWeight += item[1].weight

    for item in classMap.items():
        item[1].initRatio(totalWeight)

    relLargestBuckets = []
    largestExpectedSize = 0
    for item in classMap.items():
        expectedSize = item[1].expectedTotalSize()
        if expectedSize > largestExpectedSize:
            largestExpectedSize = expectedSize
            relLargestBuckets.clear()
            relLargestBuckets.append(item[0])
        elif expectedSize == largestExpectedSize:
            relLargestBuckets.append(item[0])

    totalDiff = 0
    for item in classMap.items():
        totalDiff += item[1].diffToTargetSizeForTotal(largestExpectedSize)

    if totalDiff > insertAmt:
        workingBuckets = {k:classMap[k] for k in classMap if k not in relLargestBuckets}
        balancedInsert(workingBuckets, insertAmt)
    else:
        insertAmt -= totalDiff
        for item in classMap.items():
            item[1].fillDiff()
            item[1].fillClass(int(insertAmt * item[1].ratio))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="Insert money into multiple weighted buckets and preserve their weights.\n\nRequires a config file of the format:\n\n[AccountName]\ntype=account\npriority=integer unique in accounts\nmaxInsert=double with max two decimal places (optional)\n\n[AssetClassName]\ntype=class\npriority=integer unique in classes\nweight=integer")
    parser.add_argument('buckets', metavar='bucket', type=bucket, nargs='+', help='Buckets in the format AccountName:ClassName:CurrentValue where names are non-spaced strings identical to config file names and CurrentValue is a float with a maximum of two decimal places')
    parser.add_argument('--deposit', type=float, help='The ammount to be added (max two decimal places)')
    parser.add_argument('--config', type=str, help='Path to the configuration file to be used')

    args = parser.parse_args()

    parser = configparser.ConfigParser()
    parser.read_file(open('/home/kmhuff/.bucket_balancer.conf'))

    accountMap = {}
    classMap = {}
    for section in parser.sections():
        if parser[section]['type'] == 'account':
            maxInsert = 0
            if 'maxInsert' in parser[section]:
                maxInsert = int(float(parser[section]['maxInsert']) * 100)
            else:
                maxInsert = float('inf')
            accountMap[section] = Account(section, maxInsert, int(parser[section]['priority']))
        elif parser[section]['type'] == 'class':
            classMap[section] = AssetClass(section, int(parser[section]['weight']), int(parser[section]['priority']))
        else:
            raise Exception('Unknown configuration section type')

    for bucket in args.buckets:
        classMap[bucket.className].addValueAccount((accountMap[bucket.acctName], bucket))

    deposit = int(args.deposit * 100)
    balancedInsert(classMap, deposit)

    for bucket in args.buckets:
        bucket.print()

    print()
    for account in accountMap.values():
        account.print()
