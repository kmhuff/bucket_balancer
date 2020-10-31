#! /usr/bin/env python3

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

        if self.targetSize < self.value:
            raise Exception("Target less than current value")
 
        self.diff = targetSize - self.value
        return self.diff

    def fillDiff(self):
        self.fill += self.diff

    def initRatio(self, totalWeight):
        self.ratio = float(self.weight) / float(totalWeight)

    def print(self):
        print("%s (weight %d): %.2f\n" %(name, weight, float(fill)/100))


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
        finishedBuckets = {k:bucketMap[k] for k in bucketMap if k in relLargestBuckets}
        workingBuckets = {k:bucketMap[k] for k in bucketMap if k not in relLargestBuckets}
        balancedInsert(workingBuckets, insertAmt)
    else:
        insertAmt -= totalDiff
        for item in bucketMap.items():
            item[1].fillDiff()
            item[1].fill += insertAmt * item[1].ratio

    for item in bucketMap.items():
        item[1].print()

