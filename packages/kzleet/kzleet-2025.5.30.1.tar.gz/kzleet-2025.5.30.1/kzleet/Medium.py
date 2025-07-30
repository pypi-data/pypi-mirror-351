from .Solution import Solution

class Solution_2131(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2131, 'Medium')

    def longestPalindrome(self, words):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/longest-palindrome-by-concatenating-two-letter-words/?envType=daily-question&envId=2025-05-25

        :type colors: str
        :type edges: List[List[int]]
        :rtype: int
        '''

        count = {}
        for word in words:
            if word in count:
                count[word] += 1
            else:
                count[word] = 1

        length = 0
        center = False

        for word in list(count.keys()):
            rev = word[::-1]
            if word != rev:
                if rev in count:
                    pairs = min(count[word], count[rev])
                    length += pairs * 4
                    count[word] -= pairs
                    count[rev] -= pairs

            else:
                pairs = count[word] // 2
                length += pairs * 4
                count[word] -= pairs * 2

                if count[word] > 0: # should be odd
                    center = True

        if center:
            length += 2

        return length

    main = longestPalindrome

class Solution_2359(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 2359, 'Medium')

    def closestMeetingNode(self, edges, node1, node2):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/find-closest-node-to-given-two-nodes/?envType=daily-question&envId=2025-05-30

        :type edges: List[int]
        :type node1: int
        :type node2: int
        :rtype: int
        '''

        def distances(node):
            distance = 0
            v = set()
            r = [len(edges) * 10] * len(edges)

            while True:
                if node in v: break
                v.add(node)
                r[node] = distance
                distance += 1
                node = edges[node]
                if node == -1: break

            return r

        d1 = distances(node1)
        d2 = distances(node2)

        argmin = 0
        impossible = True

        for i in range(len(edges)):
            if d1[i] < len(edges) * 10 and d2[i] < len(edges) * 10:
                impossible = False

            if max(d1[i], d2[i]) < max(d1[argmin], d2[argmin]):
                argmin = i

        if impossible: return -1
        return argmin

    main = closestMeetingNode

class Solution_3372(Solution):
    def __init__(self):
        super().__init__('Kevin Zhu', 3372, 'Medium')

    def maxTargetNodes(self, edges1, edges2, k):
        '''
        Author: Kevin Zhu
        Link: https://leetcode.com/problems/maximize-the-number-of-target-nodes-after-connecting-trees-i/?envType=daily-question&envId=2025-05-28

        :type edges1: List[List[int]]
        :type edges2: List[List[int]]
        :type k: int
        :rtype: List[int]
        '''

        def build_adj(edges):
            nodes = {}
            for i, j in edges:
                if i in nodes.keys():
                    nodes[i].append(j)

                else:
                    nodes[i] = [j]

                if j in nodes.keys():
                    nodes[j].append(i)

                else:
                    nodes[j] = [i]

            return nodes

        nodes1 = build_adj(edges1)
        nodes2 = build_adj(edges2)

        def target(node, max_depth, graph):
            result = set()

            def dfs(current, depth):
                if depth > max_depth:
                    return

                if current in result:
                    return

                result.add(current)

                for neighbor in graph.get(current, []):
                    dfs(neighbor, depth + 1)

            dfs(node, 0)
            return result

        max_targets2 = 0
        for node in nodes2:
            reachable = target(node, k - 1, nodes2)
            max_targets2 = max(max_targets2, len(reachable))

        result = []
        for node in nodes1:
            reachable1 = target(node, k, nodes1)
            result.append(len(reachable1) + max_targets2)

        return result

    main = maxTargetNodes
