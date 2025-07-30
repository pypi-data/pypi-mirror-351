class Solution(object):
    def __init__(self, author, date):
        self.author = author
        self.date = date

    def __str__(self):
        return f'LeetCode Solution by {self.author} on {self.date}'