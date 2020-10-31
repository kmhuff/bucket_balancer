#! /usr/bin/env python3

import argparse

def bucket(input):
    list = input.split(':')
    valueFlt = float(list[1])
    valueFlt = valueFlt * 100
    return Bucket(list[0], int(valueFlt), int(list[2]))

class Bucket:
    def __init__(self, name, value, weight):
        self.name = name
        self.value = value
        self.fill = 0
        self.weight = weight

    def expectedTotalSize(self):
        return self.value / self.ratio

    def diffToTargetSizeForTotal(self, total):
        targetSize = total * self.ratio

        if targetSize < self.value:
            raise Exception("Target less than current value")
 
        self.diff = targetSize - self.value
        return self.diff

    def fillDiff(self):
        self.fill += self.diff

    def initRatio(self, totalWeight):
        self.ratio = float(self.weight) / float(totalWeight)

    def print(self):
        print("%s (weight %d): %.2f\n" %(self.name, self.weight, float(self.fill)/100))


def balancedInsert(bucketMap, insertAmt):
    totalWeight = 0
    for item in bucketMap.items():
        totalWeight += item[1].weight

    for item in bucketMap.items():
        item[1].initRatio(totalWeight)

    relLargestBuckets = []
    largestExpectedSize = 0
    for item in bucketMap.items():
        expectedSize = item[1].expectedTotalSize()
        if expectedSize > largestExpectedSize:
            largestExpectedSize = expectedSize
            relLargestBuckets.clear()
            relLargestBuckets.append(item[0])
        elif expectedSize == largestExpectedSize:
            relLargestBuckets.append(item[0])

    totalDiff = 0
    for item in bucketMap.items():
        totalDiff += item[1].diffToTargetSizeForTotal(largestExpectedSize)

    if totalDiff > insertAmt:
        workingBuckets = {k:bucketMap[k] for k in bucketMap if k not in relLargestBuckets}
        balancedInsert(workingBuckets, insertAmt)
    else:
        insertAmt -= totalDiff
        for item in bucketMap.items():
            item[1].fillDiff()
            item[1].fill += insertAmt * item[1].ratio


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Insert money into multiple weighted buckets and preserve their weights")
    parser.add_argument('buckets', metavar='bucket', type=bucket, nargs='+', help='Buckets in the format Name:CurrentValue:Weight where Name is a non-spaced string, CurrentValue is a float with a maximum of two decimal places, and Weight is an int')
    parser.add_argument('--deposit', type=float, help='The ammount to be added')

    args = parser.parse_args()

    bucketMap = {bucket.name:bucket for bucket in args.buckets}
    deposit = int(args.deposit * 100)

    balancedInsert(bucketMap, deposit)

    for item in bucketMap.items():
        item[1].print()

